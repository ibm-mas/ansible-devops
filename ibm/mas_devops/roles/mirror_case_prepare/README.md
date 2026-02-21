# mirror_case_prepare
This role generates a mirror manifest file suitable for use with the `oc mirror` command (or the `ibm.mas_devops.mirror_images` role) from an IBM CASE bundle.

## Requirements
The [ibm-pak plugin](https://github.com/IBM/ibm-pak-plugin) must be installed.


## Role Variables - General
### case_name
Name of the IBM CASE bundle to prepare for mirroring.

- **Required**
- Environment Variable: `CASE_NAME`
- Default: None

**Purpose**: Specifies which IBM Cloud Pak Application Software Entitlement (CASE) bundle to download and prepare for mirroring to a disconnected registry.

**When to use**:
- Always required for CASE bundle mirroring preparation
- Must match an available CASE bundle name
- Common values: `ibm-mas`, `ibm-sls`, `ibm-cp4d`

**Valid values**: Valid IBM CASE bundle name (e.g., `ibm-mas`, `ibm-sls`, `ibm-cp4d`)

**Impact**: Determines which CASE bundle is downloaded and processed. Incorrect name will cause download to fail.

**Related variables**:
- `case_version`: Version of this CASE bundle to download
- `ibmpak_skip_dependencies`: Whether to include CASE dependencies

**Note**: CASE bundles contain metadata about container images and operators. Use `oc ibm-pak list` to see available CASE bundles.

### case_version
Version of the IBM CASE bundle to prepare for mirroring.

- **Required**
- Environment Variable: `CASE_VERSION`
- Default: None

**Purpose**: Specifies which version of the CASE bundle to download and prepare for mirroring. Different versions contain different image sets.

**When to use**:
- Always required for CASE bundle mirroring preparation
- Must match an available version for the specified CASE bundle
- Use specific version for production (e.g., `8.8.1`, `9.0.0`)

**Valid values**: Valid version number for the CASE bundle (e.g., `8.8.1`, `9.0.0`, `3.8.0`)

**Impact**: Determines which version of images are included in the mirror manifest. Version must exist for the specified CASE bundle.

**Related variables**:
- `case_name`: CASE bundle for this version

**Note**: Use `oc ibm-pak list <case_name>` to see available versions. Underscores in version are automatically converted to dots (e.g., `8_8_1` becomes `8.8.1`).

### registry_public_host
Target registry hostname for mirrored images.

- **Required**
- Environment Variable: `REGISTRY_PUBLIC_HOST`
- Default: None

**Purpose**: Specifies the hostname of the target container registry where images will be mirrored. Used to generate the mirror manifest with correct destination paths.

**When to use**:
- Always required for mirror manifest preparation
- Must be the hostname of your disconnected/private registry
- Images are not mirrored yet, but manifest needs target destination

**Valid values**: Valid hostname or IP address (e.g., `registry.example.com`, `10.0.0.100`)

**Impact**: Determines the target registry in the generated mirror manifest. All image paths will reference this host.

**Related variables**:
- `registry_public_port`: Port for this registry
- `registry_prefix`: Optional path prefix in registry

**Note**: Images are not mirrored during this role execution. This role only prepares the manifest. Use `mirror_images` role to perform actual mirroring.

### registry_public_port
Target registry port for mirrored images.

- **Required**
- Environment Variable: `REGISTRY_PUBLIC_PORT`
- Default: None

**Purpose**: Specifies the port of the target container registry where images will be mirrored. Used to generate the mirror manifest with correct destination paths.

**When to use**:
- Always required for mirror manifest preparation
- Must be the port where your registry is accessible
- Common values: `443` (HTTPS), `5000` (HTTP), `32500` (NodePort)

**Valid values**: Valid port number (e.g., `443`, `5000`, `32500`)

**Impact**: Determines the target registry port in the generated mirror manifest. All image paths will include this port.

**Related variables**:
- `registry_public_host`: Hostname for this registry
- `registry_prefix`: Optional path prefix in registry

**Note**: Images are not mirrored during this role execution. This role only prepares the manifest with the target destination.

### registry_prefix
Path prefix in target registry for mirrored images.

- **Optional**
- Environment Variable: `REGISTRY_PREFIX`
- Default: None

**Purpose**: Specifies an optional path prefix in the target registry. Images will be mirrored to `{host}:{port}/{prefix}/{reponame}` format.

**When to use**:
- Leave unset if images should be at registry root
- Set to organize images under a specific path (e.g., project name, namespace)
- Useful for multi-tenant registries

**Valid values**: Valid registry path (e.g., `mas-mirror`, `production`, `project-name`)

**Impact**:
- When set: Images mirrored to `{host}:{port}/{prefix}/{reponame}`
- When unset: Images mirrored to `{host}:{port}/{reponame}`

**Related variables**:
- `registry_public_host`: Registry hostname
- `registry_public_port`: Registry port

**Note**: The prefix helps organize images in the registry. Example: with prefix `mas-mirror`, images go to `registry.example.com:5000/mas-mirror/ibm-mas-operator`.

### exclude_images
List of child CASE bundles to exclude from mirroring.

- **Optional**
- Environment Variable: None (must be set in playbook)
- Default: None

**Purpose**: Specifies which child CASE bundles (dependencies) to exclude from the mirror manifest. Reduces mirror size by excluding unwanted components.

**When to use**:
- Leave unset to include all CASE bundle dependencies
- Set to exclude specific MAS applications or components you don't need
- Useful for reducing mirror size and time

**Valid values**: List of CASE bundle names (e.g., `['ibm-sls', 'ibm-mas-assist', 'ibm-mas-iot']`)

**Impact**: Excluded CASE bundles and their images are not included in the mirror manifest. Reduces mirror size but those components won't be available.

**Related variables**:
- `case_name`: Parent CASE bundle
- `ibmpak_skip_dependencies`: Skip all dependencies (different from selective exclusion)

**Note**: Use this to exclude MAS applications you don't need (e.g., exclude Assist, IoT, Manage if only using Monitor). Cannot be set via environment variable; must be set in playbook vars.


## Role Variables - IBM Pak
### ibmpak_skip_verify
Skip certificate verification when downloading CASE bundles.

- **Optional**
- Environment Variable: `IBMPAK_SKIP_VERIFY`
- Default: `false`

**Purpose**: Controls whether to skip certificate verification when downloading CASE bundles with `oc ibm-pak get`. Useful for environments with self-signed certificates.

**When to use**:
- Leave as `false` (default) for production with valid certificates
- Set to `true` only in development/testing with self-signed certificates
- Use when certificate verification causes download failures

**Valid values**: `true`, `false`

**Impact**:
- `true`: Skips certificate verification (less secure, allows self-signed certs)
- `false`: Verifies certificates (more secure, requires valid certs)

**Related variables**:
- `ibmpak_insecure`: Skip TLS/SSL verification (related but different)

**Note**: Only use `true` in development/testing environments. Production should use valid certificates and keep this `false`.

### ibmpak_skip_dependencies
Skip downloading CASE bundle dependencies.

- **Optional**
- Environment Variable: `IBMPAK_SKIP_DEPENDENCIES`
- Default: `false`

**Purpose**: Controls whether to skip downloading dependent CASE bundles. When enabled, only the specified CASE bundle is downloaded, not its dependencies.

**When to use**:
- Leave as `false` (default) to include all dependencies (recommended)
- Set to `true` to download only the specified CASE bundle
- Use when dependencies are already downloaded or not needed

**Valid values**: `true`, `false`

**Impact**:
- `true`: Only specified CASE bundle is downloaded (may miss required dependencies)
- `false`: All dependent CASE bundles are downloaded (complete set)

**Related variables**:
- `exclude_images`: Selective exclusion of specific dependencies (more granular)

**Note**: Skipping dependencies may result in incomplete mirror. Use `exclude_images` for selective exclusion instead of skipping all dependencies.

### ibmpak_insecure
Skip TLS/SSL verification when downloading CASE bundles.

- **Optional**
- Environment Variable: `IBMPAK_INSECURE`
- Default: `false`

**Purpose**: Controls whether to skip TLS/SSL verification when downloading CASE bundles with `oc ibm-pak get`. Useful for environments with self-signed certificates or TLS issues.

**When to use**:
- Leave as `false` (default) for production with valid TLS certificates
- Set to `true` only in development/testing with TLS issues
- Use when TLS verification causes download failures

**Valid values**: `true`, `false`

**Impact**:
- `true`: Skips TLS/SSL verification (less secure, allows self-signed certs)
- `false`: Verifies TLS/SSL (more secure, requires valid certificates)

**Related variables**:
- `ibmpak_skip_verify`: Skip certificate verification (related but different)

**Note**: Only use `true` in development/testing environments. Production should use valid TLS certificates and keep this `false`.


## Example Playbook

```yaml
- hosts: localhost
  vars:
    case_name: ibm-mas
    case_version: 8.8.1

    exclude_images:
      - ibm-truststore-mgr
      - ibm-sls
      - ibm-mas-assist
      - ibm-mas-iot
      - ibm-mas-manage

    registry_public_host: myregistry.com
    registry_public_port: 32500
    registry_prefix: projectName

  roles:
    - ibm.mas_devops.mirror_case_prepare
```


## License

EPL-2.0
