# mirror_extras_prepare
This role generates a mirror manifest file suitable for use with the `oc mirror` command (or the `ibm.mas_devops.mirror_images` role) for a specific set of extra images.

Available Extras

| Extra        | Versions     | Description                                                                                    |
| ------------ | ------------ | ---------------------------------------------------------------------------------------------- |
| catalog      | N/A          | Special extra package for mirroring the IBM Maximo Operator Catalog                            |
| db2u         | 1.0.0, 1.0.1 | Extra container images missing from the ibm-db2operator CASE bundle                            |
| mongoce      | 4.2.6, 4.2.23, 4.4.21 | Package containing all images required to use MongoCE Operator in the disconnected environment |
| wd           | 5.3.1        | Extra container images missing from the ibm-watson-discovery CASE bundle                       |
| odf          | 4.15         | Extra images needed for ODF 4.15                                                               |


## Role Variables
### extras_name
Name of the extras package to prepare for mirroring.

- **Required**
- Environment Variable: `EXTRAS_NAME`
- Default: None

**Purpose**: Specifies which extras package to prepare for mirroring. Extras packages contain additional container images not included in standard CASE bundles but required for MAS deployments.

**When to use**:
- Always required for extras package mirroring preparation
- Must match an available extras package name
- See "Available Extras" table above for valid packages

**Valid values**: `catalog`, `db2u`, `mongoce`, `wd`, `odf`
- `catalog`: IBM Maximo Operator Catalog images
- `db2u`: Extra Db2 images missing from ibm-db2operator CASE
- `mongoce`: MongoDB Community Edition Operator images
- `wd`: Extra Watson Discovery images missing from CASE
- `odf`: OpenShift Data Foundation extra images

**Impact**: Determines which extras package is downloaded and processed. Incorrect name will cause preparation to fail.

**Related variables**:
- `extras_version`: Version of this extras package to prepare

**Note**: Extras packages fill gaps in CASE bundles, providing images needed for disconnected environments. Each package addresses specific missing images for different components.

### extras_version
Version of the extras package to prepare for mirroring.

- **Required**
- Environment Variable: `EXTRAS_VERSION`
- Default: None

**Purpose**: Specifies which version of the extras package to prepare for mirroring. Different versions contain different image sets or versions.

**When to use**:
- Always required for extras package mirroring preparation
- Must match an available version for the specified extras package
- See "Available Extras" table above for valid versions per package

**Valid values**: Version depends on extras package:
- `catalog`: N/A (no version required)
- `db2u`: `1.0.0`, `1.0.1`
- `mongoce`: `4.2.6`, `4.2.23`, `4.4.21`
- `wd`: `5.3.1`
- `odf`: `4.15`

**Impact**: Determines which version of images are included in the mirror manifest. Version must exist for the specified extras package.

**Related variables**:
- `extras_name`: Extras package for this version

**Note**: Not all extras packages have versions (e.g., `catalog`). Refer to the "Available Extras" table for valid version combinations.

### registry_public_host
Target registry hostname for mirrored images.

- **Required**
- Environment Variable: `REGISTRY_PUBLIC_HOST`
- Default: None

**Purpose**: Specifies the hostname of the target container registry where extras images will be mirrored. Used to generate the mirror manifest with correct destination paths.

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

**Purpose**: Specifies the port of the target container registry where extras images will be mirrored. Used to generate the mirror manifest with correct destination paths.

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

**Purpose**: Specifies an optional path prefix in the target registry. Extras images will be mirrored to `{host}:{port}/{prefix}/{reponame}` format.

**When to use**:
- Leave unset if images should be at registry root
- Set to organize images under a specific path (e.g., project name, namespace)
- Useful for multi-tenant registries or organizing extras separately

**Valid values**: Valid registry path (e.g., `mas-extras`, `production`, `project-name`)

**Impact**:
- When set: Images mirrored to `{host}:{port}/{prefix}/{reponame}`
- When unset: Images mirrored to `{host}:{port}/{reponame}`

**Related variables**:
- `registry_public_host`: Registry hostname
- `registry_public_port`: Registry port

**Note**: The prefix helps organize images in the registry. Example: with prefix `mas-extras`, images go to `registry.example.com:5000/mas-extras/mongodb-community-operator`.


## Example Playbook

```yaml
- hosts: localhost
  vars:
    extras_name: mongoce
    extras_version: 4.2.6

    registry_public_host: myocp-5f1320191125833da1cac8216c06779e-0000.us-south.containers.appdomain.cloud
    registry_public_port: 32500
    registry_prefix: projectName

  roles:
    - ibm.mas_devops.mirror_extras_prepare
```


## License
EPL-2.0
