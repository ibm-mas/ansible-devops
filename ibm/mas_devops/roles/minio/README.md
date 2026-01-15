# minio
This role deploys a MinIO object storage instance in OpenShift, which can be used for development and testing purposes with IBM Maximo Application Suite.

MinIO provides S3-compatible object storage and is deployed with a persistent volume for data storage. The role creates a namespace, deployment, service, and route to make MinIO accessible within the cluster.

!!! warning
    This MinIO deployment is intended for development and testing purposes only. For production environments, use enterprise-grade object storage solutions such as IBM Cloud Object Storage, AWS S3, or Azure Blob Storage.

## Role Variables

### General Variables

#### mas_instance_id
The instance ID of Maximo Application Suite. Used for labeling and organizing resources.

- **Optional**
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

#### mas_config_dir
Local directory to save generated configuration files.

- **Optional**
- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

### MinIO Configuration Variables

#### minio_namespace
The namespace where MinIO will be deployed.

- **Optional**
- Environment Variable: `MINIO_NAMESPACE`
- Default Value: `minio`

#### minio_instance_name
The name of the MinIO instance.

- **Optional**
- Environment Variable: `MINIO_INSTANCE_NAME`
- Default Value: `minio`

#### minio_root_user
The root username for MinIO access.

- **Optional**
- Environment Variable: `MINIO_ROOT_USER`
- Default Value: `minio`

#### minio_root_password
The root password for MinIO access. If not provided, a password will be auto-generated.

- **Optional**
- Environment Variable: `MINIO_ROOT_PASSWORD`
- Default Value: Auto-generated

#### minio_storage_class
The storage class to use for the MinIO persistent volume. If not specified, the default storage class will be used.

- **Optional**
- Environment Variable: `MINIO_STORAGE_CLASS`
- Default Value: Cluster default storage class

#### minio_storage_size
The size of the persistent volume for MinIO data storage.

- **Optional**
- Environment Variable: `MINIO_STORAGE_SIZE`
- Default Value: `20Gi`

### Container Registry Variables

#### mas_icr_cp
The container registry for entitled images.

- **Optional**
- Environment Variable: `MAS_ICR_CP`
- Default Value: `cp.icr.io/cp`

#### mas_icr_cpopen
The container registry for open images.

- **Optional**
- Environment Variable: `MAS_ICR_CPOPEN`
- Default Value: `icr.io/cpopen`

#### mas_entitlement_username
Username for the entitled registry.

- **Optional**
- Environment Variable: `MAS_ENTITLEMENT_USERNAME`
- Default Value: `cp`

#### mas_entitlement_key
API key for the entitled registry. Required to pull MinIO container images.

- **Optional**
- Environment Variable: `MAS_ENTITLEMENT_KEY`
- Default Value: None

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
