mirror_images
===============================================================================
This role supports mirroring container images to a target mirror registry using the `oc mirror` command. It performs the actual image mirroring operation using manifests prepared by `mirror_case_prepare` or `mirror_extras_prepare` roles.


Role Variables
-------------------------------------------------------------------------------

### Registry Configuration

#### registry_public_host
Target registry hostname for mirrored images.

- **Required**
- Environment Variable: `REGISTRY_PUBLIC_HOST`
- Default: None

**Purpose**: Specifies the hostname of the target container registry where images will be mirrored. This is the actual destination for the mirroring operation.

**When to use**:
- Always required for image mirroring
- Must be the hostname of your disconnected/private registry
- Must match the registry specified in the mirror manifest

**Valid values**: Valid hostname or IP address (e.g., `registry.example.com`, `10.0.0.100`)

**Impact**: Determines the target registry for image mirroring. Images are pushed to this registry.

**Related variables**:
- `registry_public_port`: Port for this registry
- `registry_prefix`: Optional path prefix in registry
- `registry_username`, `registry_password`: Authentication credentials

**Note**: Must match the registry specified when preparing the mirror manifest. Registry must be accessible and have sufficient storage space.

#### registry_public_port
Target registry port for mirrored images.

- **Required**
- Environment Variable: `REGISTRY_PUBLIC_PORT`
- Default: None

**Purpose**: Specifies the port of the target container registry where images will be mirrored.

**When to use**:
- Always required for image mirroring
- Must be the port where your registry is accessible
- Common values: `443` (HTTPS), `5000` (HTTP), `32500` (NodePort)

**Valid values**: Valid port number (e.g., `443`, `5000`, `32500`)

**Impact**: Determines the target registry port for image mirroring. Images are pushed to this port.

**Related variables**:
- `registry_public_host`: Hostname for this registry
- `registry_prefix`: Optional path prefix in registry

**Note**: Must match the port specified when preparing the mirror manifest. Ensure the port is accessible from the mirroring system.

#### registry_prefix
Path prefix in target registry for mirrored images.

- **Optional**
- Environment Variable: `REGISTRY_PREFIX`
- Default: None

**Purpose**: Specifies an optional path prefix in the target registry. Images are mirrored to `{host}:{port}/{prefix}/{reponame}` format.

**When to use**:
- Leave unset if images should be at registry root
- Set to organize images under a specific path (e.g., project name, namespace)
- Must match the prefix used when preparing the mirror manifest

**Valid values**: Valid registry path (e.g., `mas-mirror`, `production`, `project-name`)

**Impact**:
- When set: Images mirrored to `{host}:{port}/{prefix}/{reponame}`
- When unset: Images mirrored to `{host}:{port}/{reponame}`

**Related variables**:
- `registry_public_host`: Registry hostname
- `registry_public_port`: Registry port

**Note**: Must match the prefix specified when preparing the mirror manifest. The prefix helps organize images in the registry.

#### registry_is_ecr
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

#### registry_ecr_aws_region
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


### Authentication

#### registry_username
Username for target registry authentication.

- **Required**
- Environment Variable: `REGISTRY_USERNAME`
- Default: None

**Purpose**: Provides the username for authenticating to the target container registry. Required to push images during mirroring.

**When to use**:
- Always required for image mirroring (unless using ECR with AWS credentials)
- Must have push permissions to the target registry
- Obtain from your registry administrator

**Valid values**: Valid username for the target registry

**Impact**: Used to authenticate to the target registry. Without valid credentials, image push will fail.

**Related variables**:
- `registry_password`: Password paired with this username

**Note**: Keep credentials secure. Use environment variables or secure vaults rather than hardcoding in playbooks.

#### registry_password
Password for target registry authentication.

- **Required**
- Environment Variable: `REGISTRY_PASSWORD`
- Default: None

**Purpose**: Provides the password for authenticating to the target container registry. Required to push images during mirroring.

**When to use**:
- Always required for image mirroring (unless using ECR with AWS credentials)
- Must correspond to the provided username
- Keep secure and rotate regularly

**Valid values**: Valid password for the target registry

**Impact**: Used to authenticate to the target registry. Without valid credentials, image push will fail.

**Related variables**:
- `registry_username`: Username paired with this password

**Note**: Keep passwords secure. Never commit to version control. Use environment variables or secure vaults.

#### ibm_entitlement_key
IBM entitlement key for accessing source images.

- **Required** (for IBM images)
- Environment Variable: `IBM_ENTITLEMENT_KEY`
- Default: None

**Purpose**: Authenticates access to IBM's entitled container registry to pull source images during mirroring. Required when mirroring IBM product images.

**When to use**:
- Required when mirroring IBM product images (MAS, Db2, etc.)
- Obtain from IBM Container Library at https://myibm.ibm.com/products-services/containerlibrary
- Must be a valid, non-expired key with appropriate entitlements

**Valid values**: IBM entitlement key string (typically starts with "eyJ...")

**Impact**: Without a valid key, pulling IBM source images will fail and mirroring cannot proceed.

**Related variables**:
- None

**Note**: Keep entitlement keys secure. Keys are tied to your IBM Cloud account and product entitlements. Verify key has entitlements for the products being mirrored.


### Mirroring Configuration

#### mirror_mode
Mirroring operation mode.

- **Optional**
- Environment Variable: `MIRROR_MODE`
- Default: None

**Purpose**: Specifies the mode of operation for the mirroring process. Controls whether to perform direct mirroring or use disk-based mirroring.

**When to use**:
- Set based on your mirroring workflow requirements
- Use `direct` for direct registry-to-registry mirroring
- Use `to-disk` or `from-disk` for disk-based mirroring workflows

**Valid values**: `direct`, `to-disk`, `from-disk`

**Impact**: Determines the mirroring workflow. Direct mode requires network access to both source and target registries. Disk-based mode allows offline transfer.

**Related variables**:
- `mirror_working_dir`: Working directory for disk-based mirroring

**Note**: Disk-based mirroring is useful for air-gapped environments where direct registry access is not possible.

#### mirror_working_dir
Working directory for mirroring operations.

- **Optional**
- Environment Variable: `MIRROR_WORKING_DIR`
- Default: None

**Purpose**: Specifies the working directory for mirroring operations. Used to store manifests, temporary files, and disk-based mirror archives.

**When to use**:
- Set to specify a custom working directory
- Leave unset to use default location
- Ensure directory has sufficient disk space for disk-based mirroring

**Valid values**: Absolute filesystem path

**Impact**: Determines where mirroring files are stored. Insufficient space will cause mirroring to fail.

**Related variables**:
- `mirror_mode`: Working directory used for disk-based modes

**Note**: For disk-based mirroring, ensure the directory has sufficient space for all images (can be hundreds of GB).

#### manifest_name
Name of the mirror manifest to use.

- **Optional**
- Environment Variable: `MANIFEST_NAME`
- Default: None

**Purpose**: Specifies the name of the mirror manifest file to use for the mirroring operation. Manifest defines which images to mirror.

**When to use**:
- Set to use a specific manifest file
- Leave unset to use default manifest discovery
- Manifest should be prepared by `mirror_case_prepare` or `mirror_extras_prepare` roles

**Valid values**: Manifest filename (e.g., `ibm-mas`, `mongoce`)

**Impact**: Determines which manifest is used for mirroring. Incorrect name will cause mirroring to fail.

**Related variables**:
- `manifest_version`: Version of the manifest
- `mirror_working_dir`: Directory containing manifests

**Note**: Manifests are typically prepared by the `mirror_case_prepare` or `mirror_extras_prepare` roles before running this role.

#### manifest_version
Version of the mirror manifest to use.

- **Optional**
- Environment Variable: `MANIFEST_VERSION`
- Default: None

**Purpose**: Specifies the version of the mirror manifest file to use for the mirroring operation.

**When to use**:
- Set to use a specific manifest version
- Leave unset to use default version discovery
- Must match a manifest prepared earlier

**Valid values**: Version string (e.g., `8.8.1`, `9.0.0`)

**Impact**: Determines which manifest version is used for mirroring. Incorrect version will cause mirroring to fail.

**Related variables**:
- `manifest_name`: Name of the manifest

**Note**: Underscores in version are automatically converted to dots (e.g., `8_8_1` becomes `8.8.1`).

#### mirror_single_arch
Mirror only a single architecture.

- **Optional**
- Environment Variable: `MIRROR_SINGLE_ARCH`
- Default: `amd64`

**Purpose**: Specifies whether to mirror only a single architecture instead of all available architectures. Reduces mirror size and time.

**When to use**:
- Use default (`amd64`) for x86_64 clusters (most common)
- Set to `arm64` for ARM-based clusters
- Set to empty string to mirror all architectures

**Valid values**: `amd64`, `arm64`, or empty string for all architectures

**Impact**:
- `amd64`: Mirrors only x86_64 images (smaller, faster)
- `arm64`: Mirrors only ARM images
- Empty: Mirrors all architectures (larger, slower)

**Related variables**:
- None

**Note**: Most OpenShift clusters use amd64 architecture. Only change if you have specific architecture requirements.


Example Playbook
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  vars:
    # Target registry
    registry_public_host: registry.example.com
    registry_public_port: 5000
    registry_prefix: mas-mirror

    # Registry authentication
    registry_username: admin
    registry_password: "{{ lookup('env', 'REGISTRY_PASSWORD') }}"

    # IBM authentication
    ibm_entitlement_key: "{{ lookup('env', 'IBM_ENTITLEMENT_KEY') }}"

    # Mirroring configuration
    manifest_name: ibm-mas
    manifest_version: 8.8.1
    mirror_mode: direct

  roles:
    - ibm.mas_devops.mirror_images
```


License
-------

EPL-2.0