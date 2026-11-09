"""Fixtures for the module_utils unit tests: a fake OpenSSL that does not need ML-KEM support on the host."""

import hashlib
import os
import subprocess
import sys

import pytest

modulePath = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../plugins/module_utils"))
if modulePath not in sys.path:
    sys.path.insert(0, modulePath)

import saas_backup_encryption as enc  # noqa: E402

KEM_SIZE = enc.KEM_CIPHERTEXT_SIZE


def keyId(content: str) -> str:
    """Return the id embedded in a fake key file ("id=<name>")."""
    return content.split("id=")[1].split()[0]


class FakeOpenSsl:
    """Stand-in for the OpenSSL command line implementing only what saas_backup_encryption calls.

    Fake keys are text files containing ``id=<name>``. Encapsulation produces random bytes as the KEM ciphertext
    and a shared secret that is derived from the KEM ciphertext and the key id, so decapsulation with a key that
    has a different id produces a different secret (as ML-KEM implicit rejection does).
    """

    def __init__(self, supportsMlKem=True, supportsEncap=True):
        self.supportsMlKem = supportsMlKem
        self.supportsEncap = supportsEncap
        self.calls = []
        self.secretFiles = []

    @staticmethod
    def secretFor(kemCiphertext: bytes, ident: str) -> bytes:
        return hashlib.sha256(ident.encode() + kemCiphertext).digest()

    def __call__(self, opensslPath, args):
        self.calls.append(list(args))
        result = lambda rc=0, out="", err="": subprocess.CompletedProcess([opensslPath] + args, rc, out, err)  # noqa: E731
        if args == ["version"]:
            return result(out="OpenSSL 3.6.0 (fake)\n")
        if args == ["list", "-kem-algorithms"]:
            return result(out="  X25519\n  ML-KEM-768 @ default\n" if self.supportsMlKem else "  X25519\n")
        if args == ["pkeyutl", "-help"]:
            return result(err=" -encap\n -decap\n" if self.supportsEncap else " -derive\n")
        if args[0] == "pkey":
            path = args[args.index("-in") + 1]
            content = open(path).read()
            if "id=" not in content:
                return result(rc=1, err="Could not read key")
            return result(out="ML-KEM-768 Public-Key:\n")
        if args[:2] == ["pkeyutl", "-encap"]:
            ident = keyId(open(args[args.index("-inkey") + 1]).read())
            kem = os.urandom(KEM_SIZE)
            open(args[args.index("-out") + 1], "wb").write(kem)
            secretPath = args[args.index("-secret") + 1]
            open(secretPath, "wb").write(self.secretFor(kem, ident))
            self.secretFiles.append(secretPath)
            return result()
        if args[:2] == ["pkeyutl", "-decap"]:
            ident = keyId(open(args[args.index("-inkey") + 1]).read())
            kem = open(args[args.index("-in") + 1], "rb").read()
            secretPath = args[args.index("-secret") + 1]
            open(secretPath, "wb").write(self.secretFor(kem, ident))
            self.secretFiles.append(secretPath)
            return result()
        return result(rc=1, err="unexpected fake openssl call")


@pytest.fixture
def fakeOpenSsl(monkeypatch):
    """Patch the OpenSSL subprocess boundary with FakeOpenSsl and return it."""
    fake = FakeOpenSsl()
    monkeypatch.setattr(enc, "runOpenSsl", fake)
    return fake


@pytest.fixture
def keys(tmp_path):
    """Create a fake public key, its matching private key and an unrelated private key."""
    keyDir = tmp_path / "keys"
    keyDir.mkdir()
    pub = keyDir / "public.pem"
    pub.write_text("-----BEGIN PUBLIC KEY-----\nid=alpha\n-----END PUBLIC KEY-----\n")
    priv = keyDir / "private.pem"
    priv.write_text("-----BEGIN PRIVATE KEY-----\nid=alpha\n-----END PRIVATE KEY-----\n")
    other = keyDir / "other-private.pem"
    other.write_text("-----BEGIN PRIVATE KEY-----\nid=beta\n-----END PRIVATE KEY-----\n")
    return {"public": str(pub), "private": str(priv), "other": str(other)}


@pytest.fixture
def archive(tmp_path):
    """Create a ~2.5 MiB pseudo archive so that several 1 MiB chunks are processed."""
    path = tmp_path / "backup.tar.gz"
    path.write_bytes(os.urandom(2 * 1024 * 1024 + 4321))
    return str(path)
