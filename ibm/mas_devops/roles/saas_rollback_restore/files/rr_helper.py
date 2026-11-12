#!/usr/bin/env python3
# Helper for the saas_rollback_restore role.
#
# It talks to the cluster only through the `oc` CLI that the playbook is already logged in with.
# Sub-commands:
#   apply        put (create or fully replace) objects from a raw export, fixing ownerReference UIDs   (03 helpers put, fix_owner_uids)
#   export       write the live objects in the same layout as the backup raw export (02 B3.6)
#   index        write "kind/ns/name <TAB> sha256" for an export directory                              (02 B3.7)
#   diff-index   compare two export directories (changed / only in A / only in B)
#   levers       compare the upgrade levers of the saved config-repo copy with a clone                  (03 10.0)
#   ops-diff     list Subscriptions whose installed CSV differs from the recorded one                   (03 11)
#   crd-gate     list CRDs whose stored/storage versions the old CSV could not reinstall                (03 11 step 3)
#   certs-check  compare cert-manager Certificate revisions and Issuer readiness with the backup         (03 S5, X5)
#   critical     check the critical Secrets exist and equal the backup                                   (03 S4 rule 4, X4)
#
# Output is JSON on stdout. Secret values are never printed.

import argparse
import copy
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import time

SERVER_FIELDS = ("uid", "resourceVersion", "creationTimestamp", "managedFields", "generation", "selfLink")
TRACKING = "argocd.argoproj.io/tracking-id"
MAS_CRD_EXPORT_RE = re.compile(
    r"\.(core|apps|config|addons|internal)\.mas\.ibm\.com$|^[a-z]+\.sls\.ibm\.com$|\.db2u\.databases\.ibm\.com$|marketplace\.redhat\.com$|mongodbcommunity")
MAS_CRD_GROUP_RE = re.compile(r"mas\.ibm\.com|sls\.ibm\.com|db2u\.databases\.ibm\.com|marketplace\.redhat\.com|mongodbcommunity")
ALL_KINDS = ("subscription.operators.coreos.com", "operatorgroup", "catalogsource", "issuer", "certificate", "route")
CLUSTER_KINDS = ("clusterissuer", "storageclass", "clusterrole", "clusterrolebinding")


def oc(args, stdin=None):
    return subprocess.run(["oc"] + args, input=stdin, capture_output=True, text=True)


def oc_json(args):
    p = oc(args + ["-o", "json"])
    if p.returncode != 0:
        return None, p.stderr.strip()
    return json.loads(p.stdout), ""


def strip_server(obj):
    o = copy.deepcopy(obj)
    md = o.get("metadata", {})
    for f in SERVER_FIELDS:
        md.pop(f, None)
    return o


def resource_name(obj):
    """kind.group, usable with `oc get`"""
    api = obj.get("apiVersion", "v1")
    group = api.split("/")[0] if "/" in api else ""
    return obj["kind"] + ("." + group if group else "")


def ident(obj):
    md = obj.get("metadata", {})
    return "%s/%s/%s" % (obj.get("kind"), md.get("namespace", "-"), md.get("name"))


def load_list(path):
    with open(path) as fh:
        data = json.load(fh)
    return data if isinstance(data, list) else data.get("items", [])


def emit(obj, code=0):
    json.dump(obj, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    sys.exit(code)


# --------------------------------------------------------------------------------------- apply
class OwnerResolver:
    def __init__(self):
        self.cache = {}

    def uid(self, ref, ns):
        group = ref.get("apiVersion", "v1").split("/")[0] if "/" in ref.get("apiVersion", "") else ""
        res = ref["kind"] + ("." + group if group else "")
        for scope in ([["-n", ns]] if ns else []) + [[]]:
            key = (res, ref["name"], tuple(scope))
            if key not in self.cache:
                p = oc(["get", res, ref["name"]] + scope + ["-o", "jsonpath={.metadata.uid}"])
                self.cache[key] = p.stdout.strip() if p.returncode == 0 else ""
            if self.cache[key]:
                return self.cache[key]
        return ""


def fix_owner_uids(obj, resolver, notes):
    refs = obj.get("metadata", {}).get("ownerReferences")
    if not refs:
        return obj
    ns = obj["metadata"].get("namespace")
    kept = []
    for ref in refs:
        live = resolver.uid(ref, ns)
        if live:
            ref = dict(ref, uid=live)
            kept.append(ref)
        else:
            notes.append("owner %s/%s not found, reference dropped" % (ref.get("kind"), ref.get("name")))
    if kept:
        obj["metadata"]["ownerReferences"] = kept
    else:
        del obj["metadata"]["ownerReferences"]
    return obj


def transform_manage_down(obj):
    if obj.get("kind") == "ManageWorkspace":
        obj.setdefault("spec", {}).setdefault("settings", {}).setdefault("deployment", {})["mode"] = "down"
    return obj


def transform_facilities_zero(obj):
    if obj.get("kind") == "FacilitiesWorkspace":
        for t in obj.get("spec", {}).get("podTemplates", []) or []:
            t["replicas"] = 0
    return obj


TRANSFORMS = {"manage-down": transform_manage_down, "facilities-zero": transform_facilities_zero}


def normalised(obj):
    o = strip_server(obj)
    o.pop("status", None)
    return o


def cmd_apply(a):
    wanted_ns = set(filter(None, (a.namespaces or "").split(",")))
    name_re = re.compile(a.name_regex) if a.name_regex else None
    resolver = OwnerResolver()
    report, errors = [], 0
    paths = []
    for pat in a.file:
        paths.extend(sorted(glob.glob(pat)) or [pat])
    for path in paths:
        if not os.path.exists(path):
            report.append({"file": os.path.basename(path), "action": "missing-file"})
            continue
        for raw in load_list(path):
            md = raw.get("metadata", {})
            ns = md.get("namespace")
            item = {"object": ident(raw)}
            if ns and wanted_ns and ns not in wanted_ns:
                continue
            if not ns and not a.cluster_scoped:
                continue
            if name_re and not name_re.search(md.get("name", "")):
                continue
            if a.only and ident(raw) not in a.only:
                continue
            if a.filter == "nogit" and (md.get("annotations") or {}).get(TRACKING):
                item["action"] = "skipped-tracked-by-argocd"
                report.append(item)
                continue
            if raw.get("kind") == "Secret" and raw.get("type") in ("kubernetes.io/service-account-token", "kubernetes.io/dockercfg"):
                continue
            if raw.get("kind") == "ConfigMap" and md.get("name") in ("kube-root-ca.crt", "openshift-service-ca.crt"):
                continue
            obj = strip_server(raw)
            obj.pop("status", None)
            notes = []
            for t in a.transform or []:
                obj = TRANSFORMS[t](obj)
            obj = fix_owner_uids(obj, resolver, notes)
            res = resource_name(obj)
            live, err = oc_json(["get", res, md["name"]] + (["-n", ns] if ns else []))
            if live is None and "NotFound" not in err and "not found" not in err:
                item.update(action="error", detail=err)
                errors += 1
                report.append(item)
                continue
            if live is None:
                action = "create"
            elif a.create_only:
                action = "exists-kept"
            elif normalised(live) == normalised(obj):
                action = "unchanged"
            elif obj.get("kind") == "Secret" and live.get("type") != obj.get("type"):
                action = "delete-create"
            else:
                action = "replace"
            item["action"] = action
            if notes:
                item["notes"] = notes
            if not a.dry_run and action in ("create", "replace", "delete-create"):
                if action == "delete-create":
                    p = oc(["delete", res, md["name"]] + (["-n", ns] if ns else []))
                    if p.returncode != 0:
                        item.update(action="error", detail=p.stderr.strip())
                        errors += 1
                        report.append(item)
                        continue
                    live = None
                if action == "replace" or (live is not None):
                    obj["metadata"]["resourceVersion"] = live["metadata"]["resourceVersion"]
                p = oc(["create" if live is None else "replace", "-f", "-"], stdin=json.dumps(obj))
                if p.returncode != 0:
                    item.update(action="error", detail=p.stderr.strip())
                    errors += 1
            report.append(item)
    summary = {}
    for r in report:
        summary[r.get("action", "?")] = summary.get(r.get("action", "?"), 0) + 1
    out = {"dryRun": a.dry_run, "summary": summary, "errors": errors, "items": report}
    if a.report:
        with open(a.report, "w") as fh:
            json.dump(out, fh, indent=2)
    emit({"dryRun": a.dry_run, "summary": summary, "errors": errors,
          "failed": [r for r in report if r.get("action") == "error"]}, 1 if errors else 0)


# ------------------------------------------------------------------------------------- export
def cmd_export(a):
    os.makedirs(a.out, exist_ok=True)

    def write(name, items):
        with open(os.path.join(a.out, name), "w") as fh:
            json.dump(items, fh)

    for ns in filter(None, a.namespaces.split(",")):
        d, _ = oc_json(["get", "secret", "-n", ns])
        items = []
        for o in (d or {}).get("items", []):
            if o.get("type") in ("kubernetes.io/service-account-token", "kubernetes.io/dockercfg"):
                continue
            o = strip_server(o)
            o.pop("status", None)
            items.append(o)
        write("%s__secrets.json" % ns, items)
        d, _ = oc_json(["get", "configmap", "-n", ns])
        items = [strip_server(o) for o in (d or {}).get("items", [])
                 if o["metadata"]["name"] not in ("kube-root-ca.crt", "openshift-service-ca.crt")]
        write("%s__configmaps.json" % ns, items)
    crds, _ = oc_json(["get", "crd"])
    crd_items = (crds or {}).get("items", [])
    for crd in crd_items:
        name = crd["metadata"]["name"]
        if MAS_CRD_EXPORT_RE.search(name):
            d, _ = oc_json(["get", name, "-A"])
            write("cr__%s.json" % name, [strip_server(o) for o in (d or {}).get("items", [])])
    write("crds.json", [c for c in crd_items if MAS_CRD_GROUP_RE.search(c["spec"]["group"])])
    for k in ALL_KINDS:
        d, _ = oc_json(["get", k, "-A"])
        write("all__%s.json" % k, [strip_server(o) for o in (d or {}).get("items", [])])
    for k in CLUSTER_KINDS:
        d, _ = oc_json(["get", k])
        write("cluster__%s.json" % k, [strip_server(o) for o in (d or {}).get("items", [])])
    d, _ = oc_json(["get", "ns"])
    ns_re = re.compile(a.namespace_regex) if a.namespace_regex else None
    items = []
    for o in (d or {}).get("items", []):
        if ns_re is None or ns_re.search(o["metadata"]["name"]):
            o = strip_server(o)
            o.pop("status", None)
            items.append(o)
    write("cluster__namespace.json", items)
    emit({"out": a.out, "files": len(os.listdir(a.out))})


# -------------------------------------------------------------------------------------- index
def build_index(directory, namespaces=None):
    idx = {}
    wanted = set(filter(None, (namespaces or "").split(",")))
    for fname in sorted(os.listdir(directory)):
        path = os.path.join(directory, fname)
        if fname.endswith("__secrets.json") or fname.endswith("__configmaps.json"):
            part = "data"
        elif fname.startswith("cr__"):
            part = "spec"
        else:
            continue
        for o in load_list(path):
            ns = o.get("metadata", {}).get("namespace")
            if wanted and ns and ns not in wanted:
                continue
            payload = json.dumps(o.get(part) or {}, sort_keys=True, separators=(",", ":"))
            idx[ident(o)] = hashlib.sha256(payload.encode()).hexdigest()
    return idx


def cmd_index(a):
    lines = ["%s\t%s\n" % (k, v) for k, v in sorted(build_index(a.dir, a.namespaces).items())]
    if a.out:
        with open(a.out, "w") as fh:
            fh.writelines(lines)
    emit({"entries": len(lines), "out": a.out})


def cmd_diff_index(a):
    x, y = build_index(a.a, a.namespaces), build_index(a.b, a.namespaces)
    out = {"changed": sorted(k for k in x if k in y and x[k] != y[k]),
           "onlyInA": sorted(k for k in x if k not in y),
           "onlyInB": sorted(k for k in y if k not in x)}
    emit(out, 1 if (a.fail_on_diff and (out["changed"] or out["onlyInA"] or out["onlyInB"])) else 0)


# ------------------------------------------------------------------------------------- levers
def load_yaml(path):
    import yaml
    with open(path) as fh:
        return yaml.safe_load(fh)


def walk_suffix(node, suffix, trail=()):
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, (dict, list)):
                yield from walk_suffix(v, suffix, trail + (k,))
            elif re.search(suffix, k):
                yield trail + (k,)


def get_path(node, path):
    for p in path:
        if isinstance(node, dict) and p in node:
            node = node[p]
        else:
            return False, None
    return True, node


def dotted_to_path(expr):
    return tuple(p for p in expr.strip(".").split(".") if p)


def yq_expr(path):
    return "." + "".join('["%s"]' % p for p in path)


def cmd_levers(a):
    levers = json.loads(a.levers)
    out = []
    for lv in levers:
        rel = lv["file"].replace("{inst}", a.inst)
        base = os.path.join(a.saved, a.path)
        matches = sorted(os.path.relpath(m, base) for m in glob.glob(os.path.join(base, rel)))
        if not matches:
            out.append({"file": rel, "status": "no-saved-copy"})
            continue
        for rel in matches:
            out.extend(_levers_one(a, lv, rel))
    emit({"levers": out, "differing": [x for x in out if x.get("differs") or x.get("status") != "ok"]})


def _levers_one(a, lv, rel):
    out = []
    if True:
        saved_f, clone_f = os.path.join(a.saved, a.path, rel), os.path.join(a.clone, a.path, rel)
        saved, clone = load_yaml(saved_f), (load_yaml(clone_f) if os.path.exists(clone_f) else None)
        if clone is None:
            return [{"file": rel, "status": "no-file-in-clone"}]
        paths = [dotted_to_path(p) for p in lv.get("paths", [])]
        if lv.get("key_suffix"):
            paths += list(walk_suffix(saved, lv["key_suffix"]))
        paths = list(dict.fromkeys(paths))
        for p in paths:
            has_s, vs = get_path(saved, p)
            has_c, vc = get_path(clone, p)
            if not has_s:
                continue
            out.append({"file": rel, "path": ".".join(p), "yq": yq_expr(p), "saved": vs, "current": vc if has_c else None,
                        "presentInClone": has_c, "isString": isinstance(vs, str), "differs": (not has_c) or vs != vc,
                        "status": "ok"})
    return out


# ----------------------------------------------------------------------------- operators / CRDs
def ns_rank(ns, order_res):
    for i, rx in enumerate(order_res):
        if re.search(rx, ns):
            return i
    return len(order_res)


def cmd_ops_diff(a):
    rec = json.load(open(a.record))
    live, _ = oc_json(["get", "subscription.operators.coreos.com", "-A"])
    live_by = {(s["metadata"]["namespace"], s["metadata"]["name"]): s for s in (live or {}).get("items", [])}
    order = a.order_regex
    diffs = []
    for r in rec:
        s = live_by.get((r["ns"], r["name"]))
        li = (s or {}).get("status", {}).get("installedCSV")
        lc = (s or {}).get("spec", {}).get("channel")
        if s is None or li != r.get("installedCSV") or lc != r.get("channel"):
            diffs.append({"ns": r["ns"], "name": r["name"], "recordedCSV": r.get("installedCSV"), "liveCSV": li,
                          "recordedChannel": r.get("channel"), "liveChannel": lc, "recordedApproval": r.get("installPlanApproval"),
                          "missing": s is None})
    diffs.sort(key=lambda d: (ns_rank(d["ns"], order), d["ns"], d["name"]))
    emit({"differing": diffs, "recordedCount": len(rec)})


def cmd_crd_gate(a):
    saved = {c["metadata"]["name"]: c for c in load_list(a.saved)}
    live, _ = oc_json(["get", "crd"])
    problems = []
    for c in (live or {}).get("items", []):
        n = c["metadata"]["name"]
        if not MAS_CRD_GROUP_RE.search(c["spec"]["group"]):
            continue
        stored = c.get("status", {}).get("storedVersions", [])
        storage = [v["name"] for v in c["spec"]["versions"] if v.get("storage")]
        s = saved.get(n)
        if s is None:
            problems.append({"crd": n, "problem": "CRD did not exist at backup time"})
            continue
        s_versions = {v["name"]: bool(v.get("storage")) for v in s["spec"]["versions"]}
        if set(storage) != {k for k, v in s_versions.items() if v}:
            problems.append({"crd": n, "problem": "storage version changed", "backup": s_versions, "live": storage})
        extra = [v for v in stored if v not in s_versions]
        if extra:
            problems.append({"crd": n, "problem": "storedVersions contains versions the backup CRD lacks", "extra": extra})
    emit({"problems": problems}, 0)


def cmd_certs_check(a):
    problems = []
    saved_certs = {ident(o): o for o in load_list(os.path.join(a.raw, "all__certificate.json"))}
    live, _ = oc_json(["get", "certificate", "-A"])
    for o in (live or {}).get("items", []):
        k = ident(o)
        if a.name_regex and not re.search(a.name_regex, o["metadata"]["name"]):
            continue
        s = saved_certs.get(k)
        if s is None:
            continue
        if (o.get("status", {}).get("revision") or 0) > (s.get("status", {}).get("revision") or 0):
            problems.append({"object": k, "problem": "re-issued", "backupRevision": s.get("status", {}).get("revision"),
                             "liveRevision": o.get("status", {}).get("revision")})
    for kind, f in (("clusterissuer", "cluster__clusterissuer.json"), ("issuer", "all__issuer.json")):
        d, _ = oc_json(["get", kind] + ([] if kind == "clusterissuer" else ["-A"]))
        for o in (d or {}).get("items", []):
            if a.name_regex and not re.search(a.name_regex, o["metadata"]["name"]):
                continue
            ready = [c for c in o.get("status", {}).get("conditions", []) if c.get("type") == "Ready"]
            if not ready or ready[0].get("status") != "True":
                problems.append({"object": ident(o), "problem": "not Ready"})
    emit({"problems": problems})


def secret_hash(o):
    return hashlib.sha256(json.dumps(o.get("data") or {}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def cmd_critical(a):
    inst = a.inst
    wanted = [("mas-%s-manage" % inst, "main-manage-encryption-secret"),
              ("mas-%s-manage" % inst, "main-manage-encryption-secret-operator"),
              ("mas-%s-core" % inst, "%s-keys-ltpa" % inst),
              ("mas-%s-core" % inst, "%s-keys-jwt" % inst),
              ("mas-%s-core" % inst, "%s-credentials-superuser" % inst),
              (a.ca_namespace, "%s-cert-internal-ca" % inst)]
    res = []
    for ns, name in wanted:
        fpath = os.path.join(a.raw, "%s__secrets.json" % ns)
        saved = next((o for o in (load_list(fpath) if os.path.exists(fpath) else []) if o["metadata"]["name"] == name), None)
        live, _ = oc_json(["get", "secret", name, "-n", ns])
        res.append({"namespace": ns, "name": name, "inBackup": saved is not None, "present": live is not None,
                    "matchesBackup": (saved is not None and live is not None and secret_hash(saved) == secret_hash(live))})
    bad = [r for r in res if not r["present"] or (r["inBackup"] and not r["matchesBackup"])]
    emit({"checked": res, "bad": bad})


def read_json_stream(path):
    """jq without -s writes concatenated JSON values; also accepts a normal JSON file."""
    text = open(path).read()
    dec, i, out = json.JSONDecoder(), 0, []
    while i < len(text):
        while i < len(text) and text[i].isspace():
            i += 1
        if i >= len(text):
            break
        val, i = dec.raw_decode(text, i)
        out.extend(val if isinstance(val, list) else [val])
    return out


def cmd_not_ready(a):
    bad = []
    for kind in filter(None, a.kinds.split(",")):
        d, err = oc_json(["get", kind, "-n", a.namespace])
        if d is None:
            bad.append({"kind": kind, "problem": "cannot list: " + err})
            continue
        for o in d.get("items", []):
            ready = [c for c in o.get("status", {}).get("conditions", []) if c.get("type") == a.condition]
            if not ready or ready[0].get("status") != "True":
                bad.append({"object": ident(o), "problem": "%s not True" % a.condition,
                            "message": (ready[0].get("message") if ready else "no such condition")})
    emit({"notReady": bad})


def cmd_versions_diff(a):
    saved = read_json_stream(a.saved)
    live, err = oc_json(["get", a.kind, a.name, "-n", a.namespace])
    if live is None:
        emit({"problem": "cannot read live object: " + err, "differs": True})
    want = None
    kind_short = a.kind.split(".")[0].lower()
    for s in saved:
        n = s.get("name", s.get("metadata", {}).get("name"))
        k = s.get("kind")
        if n in (a.name, None) and (k is None or k.lower() == kind_short):
            want = s.get("status", {}).get("versions")
            if want is not None:
                break
    have = live.get("status", {}).get("versions")
    emit({"saved": want, "live": have, "differs": want != have})


def cmd_db2_version(a):
    rec = read_json_stream(a.record)
    live, err = oc_json(["get", "db2uinstance,db2ucluster", "-n", a.ns])
    have = sorted({(o["kind"], o["metadata"]["name"], o.get("spec", {}).get("version")) for o in (live or {}).get("items", [])})
    want = sorted({(o.get("kind"), o.get("name"), o.get("version")) for o in rec})
    emit({"recorded": want, "live": have, "differs": want != have, "err": err})


# ---------------------------------------------------------------------------------- operator return
def wait_for(fn, timeout, interval=10):
    end = time.time() + timeout
    while time.time() < end:
        v = fn()
        if v:
            return v
        time.sleep(interval)
    return None


def cmd_op_return(a):
    """03 section 11 steps 2 and 4 for one Subscription: delete Subscription+CSV, create pinned, approve exactly the recorded CSV, wait Succeeded."""
    rec = next((r for r in json.load(open(a.record)) if r["ns"] == a.ns and r["name"] == a.name), None)
    raw = next((o for o in load_list(a.raw_subs) if o["metadata"]["namespace"] == a.ns and o["metadata"]["name"] == a.name), None)
    if rec is None or raw is None:
        emit({"result": "no-record", "recorded": rec is not None, "raw": raw is not None}, 1)
    csv, pkg, chan = rec.get("installedCSV"), raw["spec"]["name"], raw["spec"]["channel"]
    allowed = {r["installedCSV"] for r in json.load(open(a.record)) if r["ns"] == a.ns and r.get("installedCSV")}
    pm, err = oc_json(["get", "packagemanifest", pkg, "-n", raw["spec"].get("sourceNamespace", "openshift-marketplace")])
    entries = [e["name"] for c in ((pm or {}).get("status", {}).get("channels") or []) if c["name"] == chan for e in c.get("entries", [])]
    if csv not in entries:
        emit({"result": "csv-not-in-catalog", "csv": csv, "channel": chan, "package": pkg, "channelEntries": entries[:5], "err": err}, 1)
    if a.check_only:
        emit({"result": "available", "csv": csv, "channel": chan})
    live, _ = oc_json(["get", "subscription.operators.coreos.com", a.name, "-n", a.ns])
    cur = ((live or {}).get("status") or {}).get("installedCSV")
    oc(["delete", "subscription.operators.coreos.com", a.name, "-n", a.ns, "--ignore-not-found"])
    if cur:
        oc(["delete", "csv", cur, "-n", a.ns, "--ignore-not-found"])
    sub = strip_server(raw)
    sub.pop("status", None)
    sub["spec"]["startingCSV"] = csv
    sub["spec"]["installPlanApproval"] = "Manual"
    p = oc(["create", "-f", "-"], stdin=json.dumps(sub))
    if p.returncode != 0:
        emit({"result": "create-failed", "err": p.stderr.strip()}, 1)

    def approve():
        d, _ = oc_json(["get", "installplan", "-n", a.ns])
        for ip in (d or {}).get("items", []):
            names = ip["spec"].get("clusterServiceVersionNames") or []
            if csv in names and not ip["spec"].get("approved") and set(names) <= allowed:
                q = oc(["patch", "installplan", ip["metadata"]["name"], "-n", a.ns, "--type", "merge", "-p", '{"spec":{"approved":true}}'])
                return ip["metadata"]["name"] if q.returncode == 0 else None
            if csv in names and ip["spec"].get("approved"):
                return ip["metadata"]["name"]
        return None

    ip = wait_for(approve, a.timeout)
    if not ip:
        emit({"result": "no-matching-installplan", "csv": csv}, 1)

    def ok():
        o, _ = oc_json(["get", "csv", csv, "-n", a.ns])
        return o and o.get("status", {}).get("phase") == "Succeeded"

    if not wait_for(ok, a.timeout):
        emit({"result": "csv-not-succeeded", "csv": csv, "installPlan": ip}, 1)
    appr = rec.get("installPlanApproval") or raw["spec"].get("installPlanApproval") or "Automatic"
    oc(["patch", "subscription.operators.coreos.com", a.name, "-n", a.ns, "--type", "merge", "-p",
        json.dumps({"spec": {"installPlanApproval": appr}})])
    emit({"result": "ok", "csv": csv, "installPlan": ip, "approvalRestoredTo": appr})


def cmd_catalog_pin(a):
    lines = [l.strip() for l in open(a.record).read().splitlines() if l.strip()]
    tag = lines[0]
    digests = sorted({l.split("@")[-1] for l in lines[1:] if "@sha256:" in l})
    image = tag.split("@")[0] if "@" in tag else tag
    image = re.sub(r":[^/:]+$", "", image) if re.search(r":[^/:]+$", image) else image
    target = tag if "@sha256:" in tag else (("%s@%s" % (image, digests[0])) if (a.digest and len(digests) == 1) else tag)
    emit({"specImage": tag, "digests": digests, "target": target, "pinned": "@sha256:" in target,
          "ambiguous": a.digest and len(digests) != 1})


# --------------------------------------------------------------------------------------- ArgoCD
def argo_apps(ns):
    d, _ = oc_json(["get", "application", "-n", ns])
    return (d or {}).get("items", [])


def patch(kind, name, ns, body):
    return oc(["patch", kind, name, "-n", ns, "--type", "merge", "-p", json.dumps(body)])


def cmd_argo_state(a):
    apps = argo_apps(a.ns)
    auto = [x["metadata"]["name"] for x in apps if (x.get("spec", {}).get("syncPolicy") or {}).get("automated") is not None]
    run = [x["metadata"]["name"] for x in apps if (x.get("status", {}).get("operationState") or {}).get("phase") == "Running"]
    owned = [x["metadata"]["name"] for x in apps
             if (x.get("spec", {}).get("syncPolicy") or {}).get("automated") is not None
             and any(r.get("kind") == "ApplicationSet" for r in x["metadata"].get("ownerReferences", []))]
    emit({"total": len(apps), "automated": auto, "running": run, "automatedCount": len(auto), "runningCount": len(run),
          "appsetOwnedAutomated": owned, "appsetOwnedAutomatedCount": len(owned)})


def cmd_argo_freeze(a):
    done, failed = [], []

    def go(kind, name, body):
        p = patch(kind, name, a.ns, body)
        (done if p.returncode == 0 else failed).append(kind + "/" + name + ("" if p.returncode == 0 else ": " + p.stderr.strip()))

    off = {"automated": None}
    if a.step == "terminate":
        for x in argo_apps(a.ns):
            if (x.get("status", {}).get("operationState") or {}).get("phase") == "Running":
                go("application", x["metadata"]["name"], {"operation": None})
    elif a.step == "root":
        go("application", a.root, {"spec": {"syncPolicy": off}})
    elif a.step == "appsets":
        d, _ = oc_json(["get", "applicationset", "-n", a.ns])
        for x in (d or {}).get("items", []):
            go("applicationset", x["metadata"]["name"], {"spec": {"template": {"spec": {"syncPolicy": off}}}})
    elif a.step == "apps":
        for x in argo_apps(a.ns):
            if (x.get("spec", {}).get("syncPolicy") or {}).get("automated") is not None:
                go("application", x["metadata"]["name"], {"spec": {"syncPolicy": off}})
    remaining = len([x for x in argo_apps(a.ns) if (x.get("spec", {}).get("syncPolicy") or {}).get("automated") is not None])
    emit({"step": a.step, "patched": len(done), "failed": failed, "remainingAutomated": remaining}, 1 if failed else 0)


def cmd_argo_policy(a):
    summary = {x["name"]: x for x in json.load(open(a.summary))}
    appsets = {x["name"]: x for x in json.load(open(a.appsets))}
    done, skipped, failed = [], [], []
    if a.check:
        def norm(sp):
            return json.dumps({k: v for k, v in (sp or {}).items() if v not in (None, {}, [])}, sort_keys=True)
        live = {x["metadata"]["name"]: x for x in argo_apps(a.ns)}
        diffs, missing = [], []
        for n, x in summary.items():
            l = live.get(n)
            if l is None:
                missing.append(n)
            elif norm(x.get("syncPolicy")) != norm(l.get("spec", {}).get("syncPolicy")):
                diffs.append({"name": n, "recorded": x.get("syncPolicy"), "live": l.get("spec", {}).get("syncPolicy")})
        emit({"differs": diffs, "missing": missing, "checked": len(summary)})

    def sp_body(sp):
        sp = copy.deepcopy(sp) if sp else {}
        if a.no_prune and sp.get("automated"):
            sp["automated"]["prune"] = False
        sp.setdefault("automated", None)
        return sp

    def go(kind, name, body):
        p = patch(kind, name, a.ns, body)
        if p.returncode == 0:
            done.append(kind + "/" + name)
        elif "NotFound" in p.stderr:
            skipped.append(kind + "/" + name)
        else:
            failed.append(kind + "/" + name + ": " + p.stderr.strip())

    for n, x in summary.items():
        if n != a.root:
            go("application", n, {"spec": {"syncPolicy": sp_body(x.get("syncPolicy"))}})
    for n, x in appsets.items():
        go("applicationset", n, {"spec": {"template": {"spec": {"syncPolicy": sp_body(x.get("templateSyncPolicy"))}}}})
    if a.root in summary:
        go("application", a.root, {"spec": {"syncPolicy": sp_body(summary[a.root].get("syncPolicy"))}})
    emit({"patched": len(done), "notFound": skipped, "failed": failed}, 1 if failed else 0)


def cmd_argo_list(a):
    rx = re.compile(a.name_regex)
    out = []
    for x in argo_apps(a.ns):
        n = x["metadata"]["name"]
        if rx.search(n) and not (a.exclude_regex and re.search(a.exclude_regex, n)):
            w = (x["metadata"].get("annotations") or {}).get("argocd.argoproj.io/sync-wave", "0")
            try:
                w = int(w)
            except ValueError:
                w = 0
            if a.min_wave <= w <= a.max_wave:
                out.append({"name": n, "wave": w})
    out.sort(key=lambda r: (r["wave"], r["name"]))
    emit({"apps": out})


def cmd_argo_refresh(a):
    p = oc(["annotate", "application", a.app, "-n", a.ns, "argocd.argoproj.io/refresh=hard", "--overwrite"])
    emit({"app": a.app, "ok": p.returncode == 0, "err": p.stderr.strip()}, p.returncode)


def cmd_argo_sync(a):
    cur, err = oc_json(["get", "application", a.app, "-n", a.ns])
    if cur is None:
        emit({"app": a.app, "result": "not-found", "err": err}, 1)
    before = (cur.get("status", {}).get("operationState") or {}).get("startedAt")
    p = patch("application", a.app, a.ns, {"operation": {"initiatedBy": {"username": "saas-rollback-restore"}, "sync": {"prune": False}}})
    if p.returncode != 0:
        emit({"app": a.app, "result": "patch-failed", "err": p.stderr.strip()}, 1)
    end = time.time() + a.timeout
    last = {}
    while time.time() < end:
        time.sleep(10)
        cur, _ = oc_json(["get", "application", a.app, "-n", a.ns])
        if not cur:
            continue
        op = cur.get("status", {}).get("operationState") or {}
        last = {"phase": op.get("phase"), "sync": cur.get("status", {}).get("sync", {}).get("status"),
                "health": cur.get("status", {}).get("health", {}).get("status"), "message": op.get("message")}
        if op.get("startedAt") != before and op.get("phase") in ("Failed", "Error"):
            emit({"app": a.app, "result": "failed", **last}, 1)
        if op.get("startedAt") != before and op.get("phase") == "Succeeded" and last["sync"] == "Synced" and last["health"] == "Healthy":
            emit({"app": a.app, "result": "ok", **last})
    emit({"app": a.app, "result": "timeout", **last}, 1)


def cmd_argo_unsynced(a):
    rx = re.compile(a.name_regex)
    bad = []
    for x in argo_apps(a.ns):
        n = x["metadata"]["name"]
        if rx.search(n):
            s, h = x.get("status", {}).get("sync", {}).get("status"), x.get("status", {}).get("health", {}).get("status")
            if s != "Synced" or h != "Healthy":
                bad.append({"name": n, "sync": s, "health": h})
    emit({"notSyncedOrHealthy": bad})


# ------------------------------------------------------------------------- scale / pods / facilities
def cmd_scale(a):
    rx = re.compile(a.exclude_regex) if a.exclude_regex else None
    if a.restore:
        rec = json.load(open(a.record))
        if a.include_regex:
            rec = [r for r in rec if re.search(a.include_regex, r["name"])]
        res = []
        for r in rec:
            if a.operators_only:
                if r["kind"].lower() != "deployment":
                    continue
                o, _ = oc_json(["get", "deployment", r["name"], "-n", a.ns])
                if not o or not any(x.get("kind") == "ClusterServiceVersion" for x in o["metadata"].get("ownerReferences", [])):
                    continue
            p = oc(["scale", "%s/%s" % (r["kind"].lower(), r["name"]), "-n", a.ns, "--replicas=%s" % r["replicas"]])
            res.append({"object": r["name"], "ok": p.returncode == 0})
        emit({"restored": res}, 0 if all(x["ok"] for x in res) else 1)
    items = []
    for kind in ("deployment", "statefulset"):
        d, _ = oc_json(["get", kind, "-n", a.ns])
        for o in (d or {}).get("items", []):
            if rx and rx.search(o["metadata"]["name"]):
                continue
            items.append({"kind": o["kind"], "name": o["metadata"]["name"], "replicas": o["spec"].get("replicas", 1)})
    if not os.path.exists(a.record):
        with open(a.record, "w") as fh:
            json.dump(items, fh)
    failed = []
    for r in items:
        p = oc(["scale", "%s/%s" % (r["kind"].lower(), r["name"]), "-n", a.ns, "--replicas=0"])
        if p.returncode != 0:
            failed.append(r["name"] + ": " + p.stderr.strip())
    emit({"scaledToZero": len(items) - len(failed), "failed": failed, "record": a.record}, 1 if failed else 0)


def cmd_pods(a):
    rx = re.compile(a.exclude_regex) if a.exclude_regex else None
    d, err = oc_json(["get", "pod", "-n", a.ns])
    run = [o["metadata"]["name"] for o in (d or {}).get("items", [])
           if o.get("status", {}).get("phase") not in ("Succeeded", "Failed") and not (rx and rx.search(o["metadata"]["name"]))]
    emit({"namespace": a.ns, "running": run, "count": len(run), "err": err})


def cmd_fac(a):
    o, err = oc_json(["get", "facilitiesworkspace.apps.mas.ibm.com", a.name, "-n", a.ns])
    if o is None:
        emit({"result": "not-found", "err": err}, 1)
    tpls = copy.deepcopy(o.get("spec", {}).get("podTemplates") or [])
    if a.check:
        rec = json.load(open(a.record))
        live = {t.get("name"): t.get("replicas") for t in tpls}
        bad = [{"name": r["name"], "recorded": r.get("replicas"), "live": live.get(r["name"])}
               for r in rec if live.get(r["name"]) != r.get("replicas")]
        emit({"differs": bad})
    if a.zero:
        for t in tpls:
            t["replicas"] = 0
    else:
        rec = {r["name"]: r.get("replicas") for r in json.load(open(a.record))}
        for t in tpls:
            if t.get("name") in rec:
                if rec[t["name"]] is None:
                    t.pop("replicas", None)
                else:
                    t["replicas"] = rec[t["name"]]
    p = patch("facilitiesworkspace.apps.mas.ibm.com", a.name, a.ns, {"spec": {"podTemplates": tpls}})
    emit({"podTemplates": tpls, "ok": p.returncode == 0, "err": p.stderr.strip()}, p.returncode)


def cmd_catalog_state(a):
    o, err = oc_json(["get", "catalogsource", a.name, "-n", a.ns])
    if o is None:
        emit({"found": False, "err": err}, 1)
    pods, _ = oc_json(["get", "pod", "-n", a.ns, "-l", "olm.catalogSource=" + a.name])
    ids = sorted({cs.get("imageID", "") for p in (pods or {}).get("items", []) for cs in p.get("status", {}).get("containerStatuses", [])})
    emit({"found": True, "image": o["spec"].get("image"), "state": (o.get("status", {}).get("connectionState") or {}).get("lastObservedState"),
          "podImageIds": ids})


def cmd_secrets_manager(a):
    out = []
    for f in sorted(glob.glob(os.path.join(a.dir, "*.json"))):
        saved = json.load(open(f))
        sid, ver = saved.get("Name") or saved.get("ARN"), saved.get("VersionId")
        if not sid or not ver:
            continue
        p = subprocess.run(["aws", "secretsmanager", "describe-secret", "--secret-id", sid, "--output", "json"] +
                           (["--region", a.region] if a.region else []), capture_output=True, text=True)
        if p.returncode != 0:
            out.append({"secret": sid, "status": "cannot-describe", "err": p.stderr.strip()[:200]})
            continue
        stages = json.loads(p.stdout).get("VersionIdsToStages", {})
        cur = next((v for v, st in stages.items() if "AWSCURRENT" in st), None)
        item = {"secret": sid, "savedVersion": ver, "currentVersion": cur, "status": "same" if cur == ver else "differs"}
        if item["status"] == "differs" and a.restore:
            if ver not in stages:
                item["status"] = "saved-version-gone"
            else:
                q = subprocess.run(["aws", "secretsmanager", "update-secret-version-stage", "--secret-id", sid, "--version-stage", "AWSCURRENT",
                                    "--move-to-version-id", ver, "--remove-from-version-id", cur] + (["--region", a.region] if a.region else []),
                                   capture_output=True, text=True)
                item["status"] = "restored" if q.returncode == 0 else "restore-failed"
                if q.returncode != 0:
                    item["err"] = q.stderr.strip()[:200]
        out.append(item)
    bad = [x for x in out if x["status"] not in ("same", "restored")]
    emit({"secrets": [dict((k, v) for k, v in x.items()) for x in out], "notSame": bad}, 0)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("apply")
    p.add_argument("--file", nargs="+", required=True)
    p.add_argument("--namespaces", default="")
    p.add_argument("--filter", choices=("all", "nogit"), default="all")
    p.add_argument("--name-regex", default="")
    p.add_argument("--only", nargs="*", default=[])
    p.add_argument("--transform", action="append", choices=sorted(TRANSFORMS))
    p.add_argument("--create-only", action="store_true")
    p.add_argument("--cluster-scoped", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--report", default="")
    p.set_defaults(fn=cmd_apply)
    p = sub.add_parser("export")
    p.add_argument("--out", required=True)
    p.add_argument("--namespaces", required=True)
    p.add_argument("--namespace-regex", default="")
    p.set_defaults(fn=cmd_export)
    p = sub.add_parser("index")
    p.add_argument("--dir", required=True)
    p.add_argument("--namespaces", default="")
    p.add_argument("--out", default="")
    p.set_defaults(fn=cmd_index)
    p = sub.add_parser("diff-index")
    p.add_argument("--a", required=True)
    p.add_argument("--b", required=True)
    p.add_argument("--namespaces", default="")
    p.add_argument("--fail-on-diff", action="store_true")
    p.set_defaults(fn=cmd_diff_index)
    p = sub.add_parser("levers")
    p.add_argument("--saved", required=True)
    p.add_argument("--clone", required=True)
    p.add_argument("--path", required=True)
    p.add_argument("--inst", required=True)
    p.add_argument("--levers", required=True)
    p.set_defaults(fn=cmd_levers)
    p = sub.add_parser("ops-diff")
    p.add_argument("--record", required=True)
    p.add_argument("--order-regex", action="append", default=[])
    p.set_defaults(fn=cmd_ops_diff)
    p = sub.add_parser("crd-gate")
    p.add_argument("--saved", required=True)
    p.set_defaults(fn=cmd_crd_gate)
    p = sub.add_parser("certs-check")
    p.add_argument("--raw", required=True)
    p.add_argument("--name-regex", default="")
    p.set_defaults(fn=cmd_certs_check)
    p = sub.add_parser("critical")
    p.add_argument("--raw", required=True)
    p.add_argument("--inst", required=True)
    p.add_argument("--ca-namespace", default="cert-manager")
    p.set_defaults(fn=cmd_critical)
    p = sub.add_parser("not-ready")
    p.add_argument("--kinds", required=True)
    p.add_argument("--namespace", required=True)
    p.add_argument("--condition", default="Ready")
    p.set_defaults(fn=cmd_not_ready)
    p = sub.add_parser("versions-diff")
    p.add_argument("--saved", required=True)
    p.add_argument("--kind", required=True)
    p.add_argument("--namespace", required=True)
    p.add_argument("--name", required=True)
    p.set_defaults(fn=cmd_versions_diff)
    p = sub.add_parser("argo-state")
    p.add_argument("--ns", required=True)
    p.set_defaults(fn=cmd_argo_state)
    p = sub.add_parser("argo-freeze")
    p.add_argument("--ns", required=True)
    p.add_argument("--root", default="")
    p.add_argument("--step", required=True, choices=("terminate", "root", "appsets", "apps"))
    p.set_defaults(fn=cmd_argo_freeze)
    p = sub.add_parser("argo-policy")
    p.add_argument("--ns", required=True)
    p.add_argument("--root", required=True)
    p.add_argument("--summary", required=True)
    p.add_argument("--appsets", required=True)
    p.add_argument("--no-prune", action="store_true")
    p.add_argument("--check", action="store_true")
    p.set_defaults(fn=cmd_argo_policy)
    p = sub.add_parser("argo-list")
    p.add_argument("--ns", required=True)
    p.add_argument("--name-regex", required=True)
    p.add_argument("--exclude-regex", default="")
    p.add_argument("--min-wave", type=int, default=-1)
    p.add_argument("--max-wave", type=int, default=99999)
    p.set_defaults(fn=cmd_argo_list)
    p = sub.add_parser("argo-refresh")
    p.add_argument("--ns", required=True)
    p.add_argument("--app", required=True)
    p.set_defaults(fn=cmd_argo_refresh)
    p = sub.add_parser("argo-sync")
    p.add_argument("--ns", required=True)
    p.add_argument("--app", required=True)
    p.add_argument("--timeout", type=int, default=1800)
    p.set_defaults(fn=cmd_argo_sync)
    p = sub.add_parser("argo-unsynced")
    p.add_argument("--ns", required=True)
    p.add_argument("--name-regex", default=".")
    p.set_defaults(fn=cmd_argo_unsynced)
    p = sub.add_parser("scale")
    p.add_argument("--ns", required=True)
    p.add_argument("--record", required=True)
    p.add_argument("--restore", action="store_true")
    p.add_argument("--exclude-regex", default="")
    p.add_argument("--include-regex", default="")
    p.add_argument("--operators-only", action="store_true")
    p.set_defaults(fn=cmd_scale)
    p = sub.add_parser("pods")
    p.add_argument("--ns", required=True)
    p.add_argument("--exclude-regex", default="")
    p.set_defaults(fn=cmd_pods)
    p = sub.add_parser("fac-replicas")
    p.add_argument("--ns", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--zero", action="store_true")
    p.add_argument("--check", action="store_true")
    p.add_argument("--record", default="")
    p.set_defaults(fn=cmd_fac)
    p = sub.add_parser("catalog-state")
    p.add_argument("--name", required=True)
    p.add_argument("--ns", required=True)
    p.set_defaults(fn=cmd_catalog_state)
    p = sub.add_parser("secrets-manager")
    p.add_argument("--dir", required=True)
    p.add_argument("--region", default="")
    p.add_argument("--restore", action="store_true")
    p.set_defaults(fn=cmd_secrets_manager)
    p = sub.add_parser("db2-version")
    p.add_argument("--record", required=True)
    p.add_argument("--ns", required=True)
    p.set_defaults(fn=cmd_db2_version)
    p = sub.add_parser("op-return")
    p.add_argument("--ns", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--record", required=True)
    p.add_argument("--raw-subs", required=True)
    p.add_argument("--timeout", type=int, default=1200)
    p.add_argument("--check-only", action="store_true")
    p.set_defaults(fn=cmd_op_return)
    p = sub.add_parser("catalog-pin")
    p.add_argument("--record", required=True)
    p.add_argument("--digest", action="store_true")
    p.set_defaults(fn=cmd_catalog_pin)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
