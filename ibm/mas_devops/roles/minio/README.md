# minio

Deploy a MinIO object storage instance in OpenShift for development and testing with IBM Maximo Application Suite.

MinIO provides S3-compatible object storage and is deployed with persistent volume for data storage. The role creates a namespace, persistent volume claim, deployment, service, and route to make MinIO accessible within the cluster. The MinIO container image (`quay.io/ibmmas/minio`) and its digest are selected based on the MAS catalog.

!!! warning "Development and Testing Only"
    This MinIO deployment is intended for **development and testing purposes only**. For production environments, use enterprise-grade object storage solutions such as IBM Cloud Object Storage, AWS S3, or Azure Blob Storage.

## Features

- **S3-Compatible API**: Full compatibility with Amazon S3 API
- **Persistent Storage**: Data stored on persistent volumes
- **Web Console**: Built-in web interface for management, exposed via an edge-terminated route
- **OpenShift Integration**: Deployed as native OpenShift resources

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`minio_namespace`](#minio_namespace) | No | `minio` |
| [`minio_instance_name`](#minio_instance_name) | No | `minio` |
| [`minio_root_user`](#minio_root_user) | No | `minio` |
| [`minio_root_password`](#minio_root_password) | No | None |
| [`primary_storage_class`](#primary_storage_class) | No | Cluster default RWX storage class |
| [`ocp_enable_ipv6`](#ocp_enable_ipv6) | No | `false` |

### MinIO Deployment

#### minio_namespace

OpenShift namespace where MinIO is deployed — a valid Kubernetes namespace name; the namespace is created if it does not exist.

- **Optional**
- Environment Variable: `MINIO_NAMESPACE`
- Default: `minio`

All MinIO resources (namespace, PVC, deployment, service, and route) are created in this namespace. Use different namespaces when deploying multiple MinIO instances.

#### minio_instance_name

Name for the MinIO deployment and associated resources — a valid Kubernetes resource name (lowercase alphanumeric with hyphens).

- **Optional**
- Environment Variable: `MINIO_INSTANCE_NAME`
- Default: `minio`

Used in the deployment name and the service selector. Use descriptive names for multiple instances (e.g. `minio-dev`, `minio-test`).

#### minio_root_user

Root username for MinIO console and S3 API access — an alphanumeric string (minimum 3 characters).

- **Optional**
- Environment Variable: `MINIO_ROOT_USER`
- Default: `minio`

The root user has full administrative access to MinIO. The default is acceptable for development and testing only.

#### minio_root_password

Root password for MinIO console and S3 API access — MinIO requires a password of at least 8 characters.

- **Optional**
- Environment Variable: `MINIO_ROOT_PASSWORD`
- Default: None

The role does not generate a password — set it explicitly and store it securely for future access.

### Storage

#### primary_storage_class

Storage class for the MinIO persistent volume claim — a valid storage class name available in the cluster.

- **Optional**
- Environment Variable: None
- Default: Cluster's default RWX storage class (auto-detected)

The PVC (`minio-pvc`) requests 40Gi with ReadWriteOnce access mode using this storage class. Verify available storage classes with `oc get storageclass`; consider the performance characteristics of the storage class when selecting it.

### Networking

#### ocp_enable_ipv6

Configure MinIO to use IPv6 addressing — `true` or `false`.

- **Optional**
- Environment Variable: `OCP_ENABLE_IPV6`
- Default: `false`

When `true`, the service is configured as SingleStack IPv6 and the MinIO server binds to IPv6 addresses for both the API (port 9000) and console (port 9090).

## Example Playbook

After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    minio_namespace: minio
    minio_instance_name: minio-dev
    minio_root_user: admin
    minio_root_password: mySecurePassword123
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
ROLE_NAME=minio ansible-playbook ibm.mas_devops.run_role
```

## License

EPL-2.0
