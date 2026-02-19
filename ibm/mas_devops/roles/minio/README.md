minio
===============================================================================

Deploy a MinIO object storage instance in OpenShift for development and testing with IBM Maximo Application Suite.

MinIO provides S3-compatible object storage and is deployed with persistent volume for data storage. The role creates a namespace, deployment, service, and route to make MinIO accessible within the cluster.

!!! warning "Development and Testing Only"
    This MinIO deployment is intended for **development and testing purposes only**. For production environments, use enterprise-grade object storage solutions such as IBM Cloud Object Storage, AWS S3, or Azure Blob Storage.

## Features

- **S3-Compatible API**: Full compatibility with Amazon S3 API
- **Persistent Storage**: Data stored on persistent volumes
- **Web Console**: Built-in web interface for management
- **OpenShift Integration**: Deployed as native OpenShift resources
- **Auto-Configuration**: Automatic credential generation and setup


Role Variables
-------------------------------------------------------------------------------

### General Variables

#### mas_instance_id
MAS instance identifier for resource labeling.

- **Optional**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Provides the MAS instance ID for labeling and organizing MinIO resources.

**When to use**: Set when deploying MinIO for a specific MAS instance to enable proper resource tracking and organization.

**Valid values**: Valid MAS instance ID (3-12 lowercase alphanumeric characters)

**Impact**: Used to label MinIO resources for identification and management.

**Related variables**: [`mas_config_dir`](#mas_config_dir)

**Notes**:
- Optional but recommended for multi-instance environments
- Helps identify which MAS instance uses this MinIO deployment
- Used in resource labels and metadata

#### mas_config_dir
Local directory for generated configuration files.

- **Optional**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

**Purpose**: Specifies where to save generated MinIO configuration files and credentials.

**When to use**: Set when you want to save MinIO connection details and credentials for later use or documentation.

**Valid values**: Valid local filesystem path (e.g., `~/masconfig`, `/opt/mas/config`)

**Impact**: MinIO configuration and credentials will be saved to this directory.

**Related variables**: [`mas_instance_id`](#mas_instance_id)

**Notes**:
- Optional - only needed if you want to save configuration files
- Useful for documenting MinIO endpoints and credentials
- Can be used for manual MAS configuration

### MinIO Configuration Variables

#### minio_namespace
Namespace for MinIO deployment.

- **Optional**
- Environment Variable: `MINIO_NAMESPACE`
- Default: `minio`

**Purpose**: Specifies the OpenShift namespace where MinIO will be deployed.

**When to use**: Use default unless you have specific namespace requirements or multiple MinIO instances.

**Valid values**: Valid Kubernetes namespace name (lowercase alphanumeric with hyphens)

**Impact**: All MinIO resources (deployment, service, route, PVC) will be created in this namespace.

**Related variables**: [`minio_instance_name`](#minio_instance_name)

**Notes**:
- Default `minio` namespace is suitable for most deployments
- Namespace will be created if it doesn't exist
- Use different namespaces for multiple MinIO instances

#### minio_instance_name
Name for the MinIO instance.

- **Optional**
- Environment Variable: `MINIO_INSTANCE_NAME`
- Default: `minio`

**Purpose**: Provides a name for the MinIO deployment and associated resources.

**When to use**: Customize when deploying multiple MinIO instances or when you want descriptive names.

**Valid values**: Valid Kubernetes resource name (lowercase alphanumeric with hyphens)

**Impact**: Used in deployment name, service name, and route hostname.

**Related variables**: [`minio_namespace`](#minio_namespace)

**Notes**:
- Default `minio` is suitable for single-instance deployments
- Use descriptive names for multiple instances (e.g., `minio-dev`, `minio-test`)
- Route will be accessible at `{instance-name}-{namespace}.{cluster-domain}`

#### minio_root_user
Root username for MinIO access.

- **Optional**
- Environment Variable: `MINIO_ROOT_USER`
- Default: `minio`

**Purpose**: Specifies the root/admin username for MinIO console and API access.

**When to use**: Customize for security or organizational naming conventions. Default is suitable for development.

**Valid values**: Alphanumeric string (minimum 3 characters)

**Impact**: This username is required for MinIO console login and S3 API access.

**Related variables**: [`minio_root_password`](#minio_root_password)

**Notes**:
- Root user has full administrative access to MinIO
- Store credentials securely
- Default `minio` is acceptable for development/testing only

#### minio_root_password
Root password for MinIO access.

- **Optional**
- Environment Variable: `MINIO_ROOT_PASSWORD`
- Default: Auto-generated secure password

**Purpose**: Specifies the root/admin password for MinIO console and API access.

**When to use**: Provide a specific password or let the role auto-generate a secure one.

**Valid values**: String (minimum 8 characters recommended)

**Impact**: This password is required for MinIO console login and S3 API access.

**Related variables**: [`minio_root_user`](#minio_root_user)

**Notes**:
- Auto-generation is recommended for security
- If auto-generated, password will be displayed in Ansible output
- Store password securely for future access
- Change default password in production-like environments

#### minio_storage_class
Storage class for MinIO persistent volume.

- **Optional**
- Environment Variable: `MINIO_STORAGE_CLASS`
- Default: Cluster default storage class

**Purpose**: Specifies which storage class to use for MinIO's persistent volume.

**When to use**: Set when you need to use a specific storage class instead of the cluster default.

**Valid values**: Valid storage class name available in the cluster

**Impact**: Determines the type and performance characteristics of MinIO's storage.

**Related variables**: [`minio_storage_size`](#minio_storage_size)

**Notes**:
- Uses cluster default storage class if not specified
- Verify storage class exists: `oc get storageclass`
- Consider performance requirements when selecting storage class
- RWO (ReadWriteOnce) access mode is sufficient for MinIO

#### minio_storage_size
Size of MinIO persistent volume.

- **Optional**
- Environment Variable: `MINIO_STORAGE_SIZE`
- Default: `20Gi`

**Purpose**: Specifies the size of the persistent volume for MinIO data storage.

**When to use**: Adjust based on expected data volume. Default 20Gi is suitable for development/testing.

**Valid values**: Valid Kubernetes storage size (e.g., `10Gi`, `50Gi`, `100Gi`)

**Impact**: Determines how much data MinIO can store.

**Related variables**: [`minio_storage_class`](#minio_storage_class)

**Notes**:
- Default 20Gi is suitable for development and testing
- Increase for larger datasets or longer retention
- Ensure cluster has sufficient storage capacity
- PVC cannot be easily resized after creation in some storage classes

### Container Registry Variables

#### mas_icr_cp
Container registry for entitled images.

- **Optional**
- Environment Variable: `MAS_ICR_CP`
- Default: `cp.icr.io/cp`

**Purpose**: Specifies the container registry for IBM entitled container images.

**When to use**: Use default for standard deployments. Override for air-gapped environments or custom registries.

**Valid values**: Valid container registry URL

**Impact**: MinIO images will be pulled from this registry.

**Related variables**: [`mas_entitlement_key`](#mas_entitlement_key), [`mas_entitlement_username`](#mas_entitlement_username)

**Notes**:
- Default points to IBM's entitled registry
- For air-gapped deployments, mirror images to internal registry
- Requires valid entitlement credentials

#### mas_icr_cpopen
Container registry for open images.

- **Optional**
- Environment Variable: `MAS_ICR_CPOPEN`
- Default: `icr.io/cpopen`

**Purpose**: Specifies the container registry for IBM open-source container images.

**When to use**: Use default for standard deployments. Override for air-gapped environments.

**Valid values**: Valid container registry URL

**Impact**: Open-source component images will be pulled from this registry.

**Related variables**: [`mas_icr_cp`](#mas_icr_cp)

**Notes**:
- Default points to IBM's public registry
- No authentication required for open images
- For air-gapped deployments, mirror to internal registry

#### mas_entitlement_username
Username for entitled registry authentication.

- **Optional**
- Environment Variable: `MAS_ENTITLEMENT_USERNAME`
- Default: `cp`

**Purpose**: Provides the username for authenticating to IBM's entitled container registry.

**When to use**: Use default `cp` for IBM entitled registry. Change only for custom registries.

**Valid values**: Valid registry username

**Impact**: Used to create image pull secret for accessing entitled images.

**Related variables**: [`mas_entitlement_key`](#mas_entitlement_key), [`mas_icr_cp`](#mas_icr_cp)

**Notes**:
- Default `cp` is standard for IBM entitled registry
- Only change if using custom registry
- Used with entitlement key for authentication

#### mas_entitlement_key
API key for entitled registry access.

- **Optional**
- Environment Variable: `MAS_ENTITLEMENT_KEY`
- Default: None

**Purpose**: Provides the IBM entitlement key for pulling MinIO container images from IBM's entitled registry.

**When to use**: Required when pulling images from IBM entitled registry. Obtain from [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary).

**Valid values**: Valid IBM entitlement key

**Impact**: Enables pulling MinIO images from IBM's entitled registry.

**Related variables**: [`mas_entitlement_username`](#mas_entitlement_username), [`mas_icr_cp`](#mas_icr_cp)

**Notes**:
- Obtain from IBM Container Library
- Store securely, never commit to version control
- Required for accessing IBM entitled images
- Not needed if images are already mirrored to accessible registry

## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    minio_namespace: minio
    minio_instance_name: minio-dev
    minio_root_user: admin
    minio_root_password: mySecurePassword123
    minio_storage_size: 50Gi
  roles:
    - ibm.mas_devops.minio
```

## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export MINIO_NAMESPACE=minio
export MINIO_INSTANCE_NAME=minio-dev
export MINIO_ROOT_USER=admin
export MINIO_ROOT_PASSWORD=mySecurePassword123
export MINIO_STORAGE_SIZE=50Gi
ROLE_NAME=minio ansible-playbook ibm.mas_devops.run_role
```

## License
EPL-2.0
