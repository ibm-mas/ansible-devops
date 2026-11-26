# mirror_ocp
This role supports mirroring the Red Hat Platform and **selected content from the Red Hat operator catalogs**.  Only content in the Red Hat catalogs directly used by IBM Maximo Application Suite is mirrored.

Three actions are supported:

- `direct` Directly mirror content to your target registry
- `to-filesystem` Mirror content to the local filesystem
- `from-filesystem` Mirror content from the local filesystem to your target registry

## Catalogs

Three catalogs are mirrored, containing the following content:

### certified-operator-index

1. gpu-operator-certified (required by ibm.mas_devops.nvidia_gpu role)
2. kubeturbo-certified (required by ibm.mas_devops.kubeturbo role)
3. ibm-metrics-operator (required by ibm.mas_devops.dro role)
4. ibm-data-reporter-operator (required by ibm.mas_devops.dro role)

### community-operator-index

1. grafana-operator (required by ibm.mas_devops.grafana role)
2. strimzi-kafka-operator (required by ibm.mas_devops.kafka role)

### redhat-operator-index

1. amq-streams (required by ibm.mas_devops.kafka role)
2. openshift-pipelines-operator-rh (required by the MAS CLI)
3. nfd (required by ibm.mas_devops.nvidia_gpu role)
4. aws-efs-csi-driver-operator (required by ibm.mas_devops.ocp_efs role)
5. local-storage-operator (required by ibm.mas_devops.ocs role)
6. odf-operator (required by ibm.mas_devops.ocs role)
7. rook-ceph-operator (required by odf)
8. recipe (required by odf)
9. odf-prometheus-operator (required by odf)
10. odf-external-snapshotter-operator (required by odf)
11. odf-csi-addons-operator (required by odf)
12. ocs-operator (required by odf)
13. ocs-client-operator (required by odf)
14. mcg-operator (required by odf)
15. cephcsi-operator (required by odf)
16. odf-dependencies (required by ibm.mas_devops.ocs role for OCP 4.18+)
17. openshift-cert-manager-operator (required by ibm.mas_devops.cert_manager role)
18. serverless-operator (required by ibm.mas_devops.aiservice_rhoai role, OCP 4.18+)
19. servicemeshoperator (required by ibm.mas_devops.aiservice_rhoai role, OCP 4.18+)
20. authorino-operator (required by ibm.mas_devops.aiservice_rhoai role, OCP 4.18+)
21. lvms-operator (not used by any of our roles, but used in SNO installations)

### Additional Images

The following specific images are also mirrored:

1. registry.redhat.io/openshift-service-mesh/istio-operator-bundle (specific digest)

## Requirements

- `oc` tool must be installed
- `oc-mirror` plugin must be installed

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`mirror_mode`](#mirror_mode) | Yes | None |
| [`mirror_working_dir`](#mirror_working_dir) | Yes | None |
| [`mirror_redhat_platform`](#mirror_redhat_platform) | No | `false` |
| [`mirror_redhat_operators`](#mirror_redhat_operators) | No | `false` |
| [`redhat_pullsecret`](#redhat_pullsecret) | Yes | None |
| [`ocp_release`](#ocp_release) | Yes | None |
| [`ocp_min_version`](#ocp_min_version) | No | None (mirrors all versions) |
| [`ocp_max_version`](#ocp_max_version) | No | None (mirrors all versions) |
| [`registry_public_host`](#registry_public_host) | Yes | None |
| [`registry_public_port`](#registry_public_port) | Yes | None |
| [`registry_is_ecr`](#registry_is_ecr) | No | `false` |
| [`registry_ecr_aws_region`](#registry_ecr_aws_region) | Conditional | None |
| [`registry_prefix_redhat`](#registry_prefix_redhat) | No | `''` |
| [`registry_username`](#registry_username) | Conditional | None |
| [`registry_password`](#registry_password) | Conditional | None |

`registry_ecr_aws_region` is only required when `registry_is_ecr=true`; `registry_username` and `registry_password` are required unless mirroring to AWS ECR, where AWS credentials are used instead.

### Mirror Actions

#### mirror_mode
Mirroring operation mode for Red Hat content — `direct` (mirror directly from Red Hat registries to the target registry; fastest, requires network access to both), `to-filesystem` (mirror to the local filesystem for offline transfer, enabling air-gapped deployment), or `from-filesystem` (mirror from the local filesystem to the target registry, completing the air-gapped deployment).

- **Required**
- Environment Variable: `MIRROR_MODE`
- Default: None

!!! tip
    For air-gapped environments, use `to-filesystem` on a connected system, transfer the files, then use `from-filesystem` on the disconnected system.

#### mirror_working_dir
Working directory for mirroring operations — an absolute filesystem path (e.g. `/tmp/mirror`, `/mnt/mirror-storage`) used to store manifests, temporary files, and disk-based mirror archives. The directory is created if it doesn't exist.

- **Required**
- Environment Variable: `MIRROR_WORKING_DIR`
- Default: None

For `to-filesystem` mode, ensure the directory has sufficient space for all images — platform plus operator content can be hundreds of GB, and insufficient space will cause mirroring to fail. The directory structure is preserved for `from-filesystem` mode.

#### mirror_redhat_platform
Whether to mirror Red Hat OpenShift Container Platform release images — required for installing or upgrading OpenShift in disconnected environments.

- **Optional**
- Environment Variable: `MIRROR_REDHAT_PLATFORM`
- Default: `false`

Platform images are a large download (tens of GB) — only enable this if you need to install or upgrade OpenShift in a disconnected environment. The patch version range mirrored is controlled by [`ocp_min_version`](#ocp_min_version) and [`ocp_max_version`](#ocp_max_version) within [`ocp_release`](#ocp_release).

#### mirror_redhat_operators
Whether to mirror selected content from the Red Hat operator catalogs — only the operators directly used by MAS are mirrored (see the catalog list above), not entire catalogs.

- **Optional**
- Environment Variable: `MIRROR_REDHAT_OPERATORS`
- Default: `false`

When `true`, selected operators are mirrored from the certified, community, and redhat-operator-index catalogs; operator compatibility follows [`ocp_release`](#ocp_release).

#### redhat_pullsecret
Path to your Red Hat pull secret file, used to authenticate and pull images from Red Hat registries during mirroring — an absolute path to the pull secret JSON file (e.g. `~/pull-secret.json`, `/tmp/pull-secret.json`), obtained from the [Red Hat OpenShift Console](https://console.redhat.com/openshift/install/pull-secret).

- **Required**
- Environment Variable: `REDHAT_PULLSECRET`
- Default: None

The pull secret must be valid, non-expired, and associated with an active Red Hat account — without it, pulling Red Hat images fails and mirroring cannot proceed. Keep the file secure, as it contains authentication credentials.

### OpenShift Version

#### ocp_release
The Red Hat release you are mirroring content for — an OpenShift major.minor version (e.g. `4.22`, `4.21`, `4.20`, `4.19`, `4.18`, `4.17`, `4.16`) that must match the OpenShift version in your target environment.

- **Required**
- Environment Variable: `OCP_RELEASE`
- Default: None

Determines which platform images and operator versions are mirrored. Use the major.minor format (e.g. `4.22`, not the full version `4.22.2`) — the patch version range is controlled by [`ocp_min_version`](#ocp_min_version) and [`ocp_max_version`](#ocp_max_version).

#### ocp_min_version
The minimum version of the Red Hat release to mirror platform content for — a full OpenShift version (e.g. `4.19.10`, `4.19.15`).

- **Optional**
- Environment Variable: `OCP_MIN_VERSION`
- Default: None (mirrors all versions)

Only platform images for this version and newer are mirrored, reducing mirror size but limiting available versions. Only applies when [`mirror_redhat_platform`](#mirror_redhat_platform) is `true`, and only affects platform image mirroring, not operators.

#### ocp_max_version
The maximum version of the Red Hat release to mirror platform content for — a full OpenShift version (e.g. `4.19.20`, `4.19.25`).

- **Optional**
- Environment Variable: `OCP_MAX_VERSION`
- Default: None (mirrors all versions)

Only platform images for this version and older are mirrored, reducing mirror size but limiting available versions. Only applies when [`mirror_redhat_platform`](#mirror_redhat_platform) is `true`, and only affects platform image mirroring, not operators.

### Target Registry

#### registry_public_host
Target registry hostname for mirrored images — a valid hostname or IP address (e.g. `registry.example.com`, `10.0.0.100`), used for the `direct` and `from-filesystem` modes.

- **Required**
- Environment Variable: `REGISTRY_PUBLIC_HOST`
- Default: None

The registry must be accessible and have sufficient storage space for the Red Hat content (can be hundreds of GB).

#### registry_public_port
Target registry port for mirrored images — a valid port number, commonly `443` (HTTPS), `5000` (HTTP), or `32500` (NodePort).

- **Required**
- Environment Variable: `REGISTRY_PUBLIC_PORT`
- Default: None

Ensure the port is accessible from the mirroring system.

#### registry_is_ecr
Whether the target registry is AWS Elastic Container Registry (ECR), enabling ECR-specific authentication and configuration.

- **Optional**
- Environment Variable: `REGISTRY_IS_ECR`
- Default: `false`

When `true`, AWS credentials must be configured and [`registry_ecr_aws_region`](#registry_ecr_aws_region) set; standard registry authentication ([`registry_username`](#registry_username) / [`registry_password`](#registry_password)) is used otherwise.

#### registry_ecr_aws_region
AWS region where the ECR registry is located — a valid AWS region (e.g. `us-east-1`, `eu-west-1`, `ap-southeast-1`), required for ECR authentication and access.

- **Optional** (Required when `registry_is_ecr=true`)
- Environment Variable: `REGISTRY_ECR_AWS_REGION`
- Default: None

AWS credentials must have permissions to push images to ECR in the specified region.

#### registry_prefix_redhat
Optional path prefix in the target registry for Red Hat images — a valid registry path (e.g. `ocp419`, `redhat`, `openshift`) used to organize Red Hat images separately from IBM or other content.

- **Optional**
- Environment Variable: `REGISTRY_PREFIX_REDHAT`
- Default: `''`

When set, images are mirrored to `{host}[:{port}]/{prefix}/{reponame}`; when unset, they are mirrored to the registry root (`{host}[:{port}]/{reponame}`).

#### registry_username
Username for authenticating to the target registry, which is used to push images during mirroring — must have push permissions to the target registry.

- **Required** (unless mirroring to AWS ECR with AWS credentials)
- Environment Variable: `REGISTRY_USERNAME`
- Default: None

Without valid credentials the image push will fail. Keep credentials secure — use environment variables or secure vaults rather than hardcoding them in playbooks.

#### registry_password
Password for authenticating to the target registry, paired with [`registry_username`](#registry_username).

- **Required** (unless mirroring to AWS ECR with AWS credentials)
- Environment Variable: `REGISTRY_PASSWORD`
- Default: None

!!! warning
    Keep passwords secure. Never commit them to version control — use environment variables or secure vaults, and rotate them regularly.

## Example Playbook

```yaml
- hosts: localhost
  vars:
    registry_public_host: myregistry.mycompany.com
    registry_public_port: 5000
    registry_prefix_redhat: "ocp416"
    registry_username: user1
    registry_password: 8934jk77s862!  # Not a real password, don't worry security folks

    mirror_mode: direct
    mirror_working_dir: /tmp/mirror
    mirror_redhat_platform: false
    mirror_redhat_operators: true

    ocp_release: 4.22
    redhat_pullsecret: ~/pull-secret.json

  roles:
    - ibm.mas_devops.mirror_ocp
```

## License

EPL-2.0
