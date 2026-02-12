mirror_ocp
===============================================================================
This role supports mirroring the Red Hat Platform and **selected content from the Red Hat operator catalogs**.  Only content in the Red Hat catalogs directly used by IBM Maximo Application Suite is mirrored.

Four actions are supported:

- `direct` Directly mirror content to your target registry
- `to-filesystem` Mirror content to the local filesystem
- `from-filesystem` Mirror content from the local filesystem to your target registry

Three **Catalogs** are mirrored, containing the following content:

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
7. openshift-cert-manager-operator (required by ibm.mas_devops.cert_manager role)
8. lvms-operator (not directly used, but often used in SNO environments)

Requirements
-------------------------------------------------------------------------------
- `oc` tool must be installed
- `oc-mirror` plugin must be installed


Role Variables
-------------------------------------------------------------------------------
### mirror_mode
Mirroring operation mode for Red Hat content.

- **Required**
- Environment Variable: `MIRROR_MODE`
- Default: None

**Purpose**: Specifies the mode of operation for mirroring Red Hat OpenShift platform and operator catalog content. Controls the mirroring workflow.

**When to use**:
- Always required for Red Hat content mirroring
- Use `direct` for direct registry-to-registry mirroring (requires network access to both)
- Use `to-filesystem` to mirror to local disk (for air-gapped transfer)
- Use `from-filesystem` to mirror from local disk to target registry

**Valid values**: `direct`, `to-filesystem`, `from-filesystem`

**Impact**:
- `direct`: Mirrors directly from Red Hat registries to target registry (fastest, requires network access)
- `to-filesystem`: Mirrors to local filesystem for offline transfer (enables air-gapped deployment)
- `from-filesystem`: Mirrors from local filesystem to target registry (completes air-gapped deployment)

**Related variables**:
- `mirror_working_dir`: Working directory for all modes
- `mirror_redhat_platform`: Whether to mirror platform images
- `mirror_redhat_operators`: Whether to mirror operator catalogs

**Note**: For air-gapped environments, use `to-filesystem` on a connected system, transfer files, then use `from-filesystem` on the disconnected system.


Role Variables - Mirror Actions
-------------------------------------------------------------------------------
### mirror_working_dir
Working directory for mirroring operations.

- **Required**
- Environment Variable: `MIRROR_WORKING_DIR`
- Default: None

**Purpose**: Specifies the working directory for mirroring operations. Used to store manifests, temporary files, and disk-based mirror archives.

**When to use**:
- Always required for Red Hat content mirroring
- Must have sufficient disk space (especially for `to-filesystem` mode)
- Directory is created if it doesn't exist

**Valid values**: Absolute filesystem path (e.g., `/tmp/mirror`, `/mnt/mirror-storage`)

**Impact**: Determines where mirroring files are stored. Insufficient space will cause mirroring to fail.

**Related variables**:
- `mirror_mode`: Working directory used for all modes

**Note**: For `to-filesystem` mode, ensure the directory has sufficient space for all images (can be hundreds of GB for platform + operators). The directory structure is preserved for `from-filesystem` mode.

### mirror_redhat_platform
Enable mirroring of Red Hat OpenShift platform images.

- **Optional**
- Environment Variable: `MIRROR_REDHAT_PLATFORM`
- Default: `false`

**Purpose**: Controls whether to mirror Red Hat OpenShift Container Platform release images. Required for installing or upgrading OpenShift in disconnected environments.

**When to use**:
- Set to `true` to mirror OpenShift platform images
- Leave as `false` (default) to skip platform mirroring
- Enable when preparing for OpenShift installation or upgrades in air-gapped environments

**Valid values**: `true`, `false`

**Impact**:
- `true`: Mirrors OpenShift platform images (large download, required for OCP install/upgrade)
- `false`: Skips platform mirroring (only operators are mirrored if enabled)

**Related variables**:
- `ocp_release`: OpenShift version to mirror
- `ocp_min_version`, `ocp_max_version`: Version range to mirror

**Note**: Platform images are large (tens of GB). Only enable if you need to install or upgrade OpenShift in a disconnected environment.

### mirror_redhat_operators
Enable mirroring of selected Red Hat operator catalog content.

- **Optional**
- Environment Variable: `MIRROR_REDHAT_OPERATORS`
- Default: `false`

**Purpose**: Controls whether to mirror selected content from Red Hat operator catalogs. Only operators directly used by MAS are mirrored (see catalog list above).

**When to use**:
- Set to `true` to mirror Red Hat operator catalogs
- Leave as `false` (default) to skip operator mirroring
- Enable when preparing for MAS deployment in air-gapped environments

**Valid values**: `true`, `false`

**Impact**:
- `true`: Mirrors selected operators from certified, community, and redhat-operator-index catalogs
- `false`: Skips operator catalog mirroring

**Related variables**:
- `ocp_release`: OpenShift version for operator compatibility

**Note**: Only selected operators used by MAS are mirrored, not entire catalogs. See the catalog list at the top of this README for included operators.

### redhat_pullsecret
Path to Red Hat pull secret file.

- **Required**
- Environment Variable: `REDHAT_PULLSECRET`
- Default: None

**Purpose**: Specifies the path to your Red Hat pull secret file. Required to authenticate and pull images from Red Hat registries during mirroring.

**When to use**:
- Always required for Red Hat content mirroring
- Obtain from [Red Hat OpenShift Console](https://console.redhat.com/openshift/install/pull-secret)
- Must be a valid, non-expired pull secret

**Valid values**: Absolute path to pull secret JSON file (e.g., `~/pull-secret.json`, `/tmp/pull-secret.json`)

**Impact**: Without a valid pull secret, pulling Red Hat images will fail and mirroring cannot proceed.

**Related variables**:
- None

**Note**: Download your pull secret from the Red Hat OpenShift Console. Keep the file secure as it contains authentication credentials. The pull secret must be valid and associated with an active Red Hat account.


Role Variables - OpenShift Version
-------------------------------------------------------------------------------
### ocp_release
<<<<<<< update-260226
The Red Hat release you are mirroring content for, e.g. `4.20`.
=======
OpenShift release version to mirror.
>>>>>>> master

- **Required**
- Environment Variable: `OCP_RELEASE`
- Default: None

**Purpose**: Specifies the major.minor version of OpenShift Container Platform to mirror content for. Determines which platform images and operator versions are mirrored.

**When to use**:
- Always required for Red Hat content mirroring
- Must match the OpenShift version in your target environment
- Use format: `4.19`, `4.18`, `4.17`

**Valid values**: OpenShift major.minor version (e.g., `4.19`, `4.18`, `4.17`, `4.16`)

**Impact**: Determines which OpenShift version's images and operators are mirrored. Must match your target cluster version.

**Related variables**:
- `ocp_min_version`: Minimum patch version to mirror
- `ocp_max_version`: Maximum patch version to mirror
- `mirror_redhat_platform`: Whether to mirror platform images for this version

**Note**: Use the major.minor version format (e.g., `4.19`), not full version (e.g., `4.19.10`). Use `ocp_min_version` and `ocp_max_version` to control patch version range.

### ocp_min_version
<<<<<<< update-260226
The minimum version of the Red Hat release to mirror platform content for, e.g. `4.20.8`.
=======
Minimum OpenShift patch version to mirror.
>>>>>>> master

- **Optional**
- Environment Variable: `OCP_MIN_VERSION`
- Default: None (mirrors all versions)

**Purpose**: Specifies the minimum patch version of OpenShift platform images to mirror. Limits the version range to reduce mirror size.

**When to use**:
- Leave unset to mirror all available patch versions for the release
- Set to mirror only specific patch versions and newer
- Only applies when `mirror_redhat_platform=true`

**Valid values**: Full OpenShift version (e.g., `4.19.10`, `4.19.15`)

**Impact**: Only platform images for this version and newer are mirrored. Reduces mirror size but limits available versions.

**Related variables**:
- `ocp_release`: Major.minor version (must match)
- `ocp_max_version`: Maximum version to mirror
- `mirror_redhat_platform`: Must be `true` for this to apply

**Note**: Only affects platform image mirroring, not operators. Use to limit mirror size when you know the specific OpenShift versions you need.

### ocp_max_version
<<<<<<< update-260226
The maximimum version of the Red Hat release to mirror platform content for, e.g. `4.20.8`.
=======
Maximum OpenShift patch version to mirror.
>>>>>>> master

- **Optional**
- Environment Variable: `OCP_MAX_VERSION`
- Default: None (mirrors all versions)

**Purpose**: Specifies the maximum patch version of OpenShift platform images to mirror. Limits the version range to reduce mirror size.

**When to use**:
- Leave unset to mirror all available patch versions for the release
- Set to mirror only specific patch versions and older
- Only applies when `mirror_redhat_platform=true`

**Valid values**: Full OpenShift version (e.g., `4.19.20`, `4.19.25`)

**Impact**: Only platform images for this version and older are mirrored. Reduces mirror size but limits available versions.

**Related variables**:
- `ocp_release`: Major.minor version (must match)
- `ocp_min_version`: Minimum version to mirror
- `mirror_redhat_platform`: Must be `true` for this to apply

**Note**: Only affects platform image mirroring, not operators. Use to limit mirror size when you know the specific OpenShift versions you need.


Role Variables - Target Registry
-------------------------------------------------------------------------------
### registry_public_host
Target registry hostname for mirrored images.

- **Required**
- Environment Variable: `REGISTRY_PUBLIC_HOST`
- Default: None

**Purpose**: Specifies the hostname of the target container registry where Red Hat images will be mirrored.

**When to use**:
- Always required for Red Hat content mirroring
- Must be the hostname of your disconnected/private registry
- Used for `direct` and `from-filesystem` modes

**Valid values**: Valid hostname or IP address (e.g., `registry.example.com`, `10.0.0.100`)

**Impact**: Determines the target registry for image mirroring. Images are pushed to this registry.

**Related variables**:
- `registry_public_port`: Port for this registry
- `registry_prefix_redhat`: Optional path prefix in registry

**Note**: Registry must be accessible and have sufficient storage space for Red Hat content (can be hundreds of GB).

### registry_public_port
Target registry port for mirrored images.

- **Required**
- Environment Variable: `REGISTRY_PUBLIC_PORT`
- Default: None

**Purpose**: Specifies the port of the target container registry where Red Hat images will be mirrored.

**When to use**:
- Always required for Red Hat content mirroring
- Must be the port where your registry is accessible
- Common values: `443` (HTTPS), `5000` (HTTP), `32500` (NodePort)

**Valid values**: Valid port number (e.g., `443`, `5000`, `32500`)

**Impact**: Determines the target registry port for image mirroring. Images are pushed to this port.

**Related variables**:
- `registry_public_host`: Hostname for this registry

**Note**: Ensure the port is accessible from the mirroring system.

### registry_is_ecr
Enable AWS Elastic Container Registry (ECR) support.

- **Optional**
- Environment Variable: `REGISTRY_IS_ECR`
- Default: `false`

**Purpose**: Indicates whether the target registry is AWS Elastic Container Registry. Enables ECR-specific authentication and configuration.

**When to use**:
- Set to `true` when mirroring to AWS ECR
- Leave as `false` (default) for other registry types
- Requires AWS credentials and ECR region configuration

**Valid values**: `true`, `false`

**Impact**:
- `true`: Uses ECR-specific authentication and configuration
- `false`: Uses standard registry authentication

**Related variables**:
- `registry_ecr_aws_region`: AWS region for ECR (required when `true`)

**Note**: When using ECR, ensure AWS credentials are configured and the ECR region is specified.

### registry_ecr_aws_region
AWS region for Elastic Container Registry.

- **Optional** (Required when `registry_is_ecr=true`)
- Environment Variable: `REGISTRY_ECR_AWS_REGION`
- Default: None

**Purpose**: Specifies the AWS region where the ECR registry is located. Required for ECR authentication and access.

**When to use**:
- Only applies when `registry_is_ecr=true`
- Must match the region where your ECR registry exists
- Required for ECR authentication

**Valid values**: Valid AWS region (e.g., `us-east-1`, `eu-west-1`, `ap-southeast-1`)

**Impact**: Determines which AWS region is used for ECR authentication and access.

**Related variables**:
- `registry_is_ecr`: Must be `true` for this to apply

**Note**: Ensure AWS credentials have permissions to push images to ECR in the specified region.

### registry_prefix_redhat
Path prefix in target registry for Red Hat images.

- **Optional**
- Environment Variable: `REGISTRY_PREFIX_REDHAT`
- Default: None

**Purpose**: Specifies an optional path prefix in the target registry for Red Hat images. Images are mirrored to `{host}[:{port}]/{prefix}/{reponame}` format.

**When to use**:
- Leave unset if images should be at registry root
- Set to organize Red Hat images under a specific path (e.g., `ocp419`, `redhat`)
- Useful for organizing different content types or versions

**Valid values**: Valid registry path (e.g., `ocp419`, `redhat`, `openshift`)

**Impact**:
- When set: Images mirrored to `{host}:{port}/{prefix}/{reponame}`
- When unset: Images mirrored to `{host}:{port}/{reponame}`

**Related variables**:
- `registry_public_host`: Registry hostname
- `registry_public_port`: Registry port

**Note**: The prefix helps organize Red Hat images separately from IBM or other content in the registry.

### registry_username
Username for target registry authentication.

- **Required**
- Environment Variable: `REGISTRY_USERNAME`
- Default: None

**Purpose**: Provides the username for authenticating to the target container registry. Required to push images during mirroring.

**When to use**:
- Always required for Red Hat content mirroring (unless using ECR with AWS credentials)
- Must have push permissions to the target registry
- Obtain from your registry administrator

**Valid values**: Valid username for the target registry

**Impact**: Used to authenticate to the target registry. Without valid credentials, image push will fail.

**Related variables**:
- `registry_password`: Password paired with this username

**Note**: Keep credentials secure. Use environment variables or secure vaults rather than hardcoding in playbooks.

### registry_password
Password for target registry authentication.

- **Required**
- Environment Variable: `REGISTRY_PASSWORD`
- Default: None

**Purpose**: Provides the password for authenticating to the target container registry. Required to push images during mirroring.

**When to use**:
- Always required for Red Hat content mirroring (unless using ECR with AWS credentials)
- Must correspond to the provided username
- Keep secure and rotate regularly

**Valid values**: Valid password for the target registry

**Impact**: Used to authenticate to the target registry. Without valid credentials, image push will fail.

**Related variables**:
- `registry_username`: Username paired with this password

**Note**: Keep passwords secure. Never commit to version control. Use environment variables or secure vaults.


Example Playbook
-------------------------------------------------------------------------------

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

    ocp_release: 4.20
    redhat_pullsecret: ~/pull-secret.json

  roles:
    - ibm.mas_devops.mirror_ocp
```


License
-------------------------------------------------------------------------------

EPL-2.0
