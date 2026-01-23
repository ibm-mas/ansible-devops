# cp4d

This role installs or upgrades [IBM Cloud Pak for Data](https://www.ibm.com/uk-en/products/cloud-pak-for-data) Operator in the target cluster.  It assumes that you have already installed the IBM Maximo Operator Catalog and configured Certificate Manager in the target cluster. These actions are performed by the [ibm_catalogs](ibm_catalogs.md) [cert_manager](cert_manager.md) roles in this collection.

Cloud Pak for Data will be configured as a [specialized installation](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=planning-architecture)

!!! info
    A specialized installation allows a user with project administrator permissions to install the software after a cluster administrator completes the initial cluster setup.  A specialized installation also facilitates strict division between Red Hat OpenShift Container Platform projects (Kubernetes namespaces).

    In a specialized installation, the IBM Cloud Pak foundational services operators are installed in the ibm-common-services project and the Cloud Pak for Data operators are installed in a separate project (typically cpd-operators). Each project has a dedicated:

    - Operator group, which specifies the OwnNamespace installation mode
    - NamespaceScope Operator, which allows the operators in the project to manage operators and service workloads in specific projects

    In this way, you can specify different settings for the IBM Cloud Pak foundational services and for the Cloud Pak for Data operators.

Currently supported Cloud Pak for Data release versions are:

  - 5.1.3
  - 5.2.0

!!! tip
    For more information about CPD versioning, see [IBM Cloud Pak for data Operator and operand versions 5.1.x](https://www.ibm.com/docs/en/software-hub/5.1.x?topic=planning-operator-operand-versions)


## Cloud Pak for Data Version Mapping
Users can choose to install a specific version of Cloud Pak for Data by setting `CPD_PRODUCT_VERSION` variable. However, by default, the version of Cloud Pak for Data will be determined by the version of the Maximo Operator Catalog that is installed in the cluster.  If `CPD_PRODUCT_VERSION` variable is not defined, and the role is not able to find the Maximo Operator Catalog, then the role will default to installing the Cloud Pak for Data version supported by the latest released MAS catalog.


## Upgrade
The role will automatically install or upgrade (if targeted to an existing CPD deployment) the corresponding Zen version associated to the chosen Cloud Pak for Data release, for example:

- Cloud Pak for Data release version `5.1.3` installs Zen/Control Plane version `6.1.1`
- Cloud Pak for Data release version `5.2.0` installs Zen/Control Plane version `6.2.0`

!!! tip
    For more information about IBM Cloud Pak for Data upgrade process, refer to the [Cloud Pak for Data official documentation](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=upgrading).


## Cloud Pak for Data Deployment Details
Cloud Pak for Data 5.x leverages Cloud Pak Foundational Services v4, which runs its deployments in isolated/dedicated scope model, that means that its dependencies will be grouped and installed within the Cloud Pak for Data related projects/namespaces. There are only two namespaces that will be used: CPD instance namespace (e.g `ibm-cpd`) and CPD operators namespace (e.g `ibm-cpd-operators`).

In the **ibm-cpd-operators** namespace:
```bash
oc -n ibm-cpd-operators get deployments

NAME                                            READY   UP-TO-DATE   AVAILABLE   AGE
cpd-platform-operator-manager                   1/1     1            1           17h
ibm-common-service-operator                     1/1     1            1           17h
ibm-namespace-scope-operator                    1/1     1            1           17h
ibm-zen-operator                                1/1     1            1           17h
meta-api-deploy                                 1/1     1            1           17h
operand-deployment-lifecycle-manager            1/1     1            1           17h
postgresql-operator-controller-manager-1-18-7   1/1     1            1           17h
```

In the **ibm-cpd** namespace:
```bash
oc -n ibm-cpd get zenservice,ibmcpd,deployments,sts,pvc

NAME                                 VERSION   STATUS      AGE
zenservice.zen.cpd.ibm.com/lite-cr   6.0.1     Completed   17h

NAME                           AGE
ibmcpd.cpd.ibm.com/ibmcpd-cr   17h

NAME                                READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/ibm-mcs-hubwork     1/1     1            1           17h
deployment.apps/ibm-mcs-placement   1/1     1            1           17h
deployment.apps/ibm-mcs-storage     1/1     1            1           17h
deployment.apps/ibm-nginx           3/3     3            3           16h
deployment.apps/ibm-nginx-tester    1/1     1            1           16h
deployment.apps/usermgmt            3/3     3            3           16h
deployment.apps/zen-audit           2/2     2            2           16h
deployment.apps/zen-core            3/3     3            3           16h
deployment.apps/zen-core-api        3/3     3            3           16h
deployment.apps/zen-watchdog        2/2     2            2           16h
deployment.apps/zen-watcher         1/1     1            1           16h

NAME                         READY   AGE
statefulset.apps/zen-minio   3/3     17h

NAME                                                   STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS      AGE
persistentvolumeclaim/export-zen-minio-0               Bound    pvc-b2a2a729-13c1-4e7f-b672-0b5efc6aa40a   20Gi       RWO            ibmc-block-gold   17h
persistentvolumeclaim/export-zen-minio-1               Bound    pvc-7e772a3a-8849-4291-8e14-501f49e79182   20Gi       RWO            ibmc-block-gold   17h
persistentvolumeclaim/export-zen-minio-2               Bound    pvc-e0dd31dc-916d-4b15-9d9c-351db0a2b47f   20Gi       RWO            ibmc-block-gold   17h
persistentvolumeclaim/ibm-cs-postgres-backup           Bound    pvc-ef788b99-784f-4531-a1b3-12611f112551   20Gi       RWO            ibmc-block-gold   16h
persistentvolumeclaim/ibm-zen-objectstore-backup-pvc   Bound    pvc-d5e61dcf-65a3-4930-9cbf-ab80d04dda00   20Gi       RWO            ibmc-block-gold   16h
persistentvolumeclaim/zen-metastore-edb-1              Bound    pvc-19d44f17-05ab-4dc0-bb5d-1b5f15ffd201   20Gi       RWO            ibmc-block-gold   17h
persistentvolumeclaim/zen-metastore-edb-2              Bound    pvc-741ea444-b6f0-44ff-a123-bb4615d97381   20Gi       RWO            ibmc-block-gold   17h
```

!!! tip
    You can retrieve the Initial Cloud Pak for Data password from the **admin-user-details** secret: `oc -n ibm-cpd get secret admin-user-details -o jsonpath="{.data.initial_admin_password}" | base64 -d`

## Role Variables

### Installation Variables

#### cpd_product_version
Cloud Pak for Data release version to install.

- **Required**
- Environment Variable: `CPD_PRODUCT_VERSION`
- Default: Determined by installed MAS catalog version

**Purpose**: Specifies which CP4D release version to install or upgrade to. The version determines which Zen/Control Plane version and features are available.

**When to use**:
- Set explicitly when you need a specific CP4D version
- Leave unset to use version matching the installed MAS catalog
- Required for reproducible deployments
- Must match supported versions (currently 5.1.3, 5.2.0)

**Valid values**: `5.1.3`, `5.2.0` (or other supported versions)

**Impact**: 
- `5.1.3`: Installs Zen/Control Plane 6.1.1
- `5.2.0`: Installs Zen/Control Plane 6.2.0
Different versions have different features and compatibility requirements.

**Related variables**:
- Determines compatible service versions
- Affects `cpd_scale_config` options

**Note**: If not set and MAS catalog is not found, defaults to CP4D version supported by latest MAS catalog. For version-specific details, see [CP4D Operator and operand versions](https://www.ibm.com/docs/en/software-hub/5.1.x?topic=planning-operator-operand-versions).

#### ibm_entitlement_key
IBM entitlement key for accessing container images.

- **Required**
- Environment Variable: `IBM_ENTITLEMENT_KEY`
- Default: None

**Purpose**: Provides authentication to IBM Container Registry for pulling CP4D container images. This key grants access to entitled software.

**When to use**:
- Always required for CP4D installation
- Obtain from [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)
- Must have valid entitlement for CP4D

**Valid values**: Valid IBM entitlement key string from your IBM account

**Impact**: Without a valid key, image pulls will fail and CP4D installation cannot proceed. Key must have CP4D entitlement.

**Related variables**:
- `cpd_entitlement_key`: CP4D-specific override (primarily for development)

**Note**: Keep this key secure and do not commit to source control. The key is tied to your IBM account and entitlements. Can be overridden by `cpd_entitlement_key` for CP4D-specific scenarios.

#### cpd_entitlement_key
CP4D-specific entitlement key override (primarily for development).

- **Optional**
- Environment Variable: `CPD_ENTITLEMENT_KEY`
- Default: None (uses `ibm_entitlement_key`)

**Purpose**: Provides a CP4D-specific entitlement key that overrides the general `ibm_entitlement_key`. Primarily used in development scenarios.

**When to use**:
- Leave unset for standard deployments (uses `ibm_entitlement_key`)
- Set when you need a different key specifically for CP4D
- Useful in development/testing with separate entitlements

**Valid values**: Valid IBM entitlement key string with CP4D entitlement

**Impact**: When set, this key is used instead of `ibm_entitlement_key` for CP4D image pulls. If not set, falls back to `ibm_entitlement_key`.

**Related variables**:
- `ibm_entitlement_key`: General entitlement key (used if this is not set)

**Note**: Most deployments should use `ibm_entitlement_key` only. This override is primarily for development scenarios where different keys are needed for different components.

#### cpd_primary_storage_class
Primary storage class for CP4D (must support ReadWriteMany).

- **Required** (if known storage classes not available)
- Environment Variable: `CPD_PRIMARY_STORAGE_CLASS`
- Default: `ibmc-file-gold-gid`, `ocs-storagecluster-cephfs`, or `azurefiles-premium` (if available)

**Purpose**: Specifies the storage class for CP4D primary storage, which requires ReadWriteMany (RWX) access mode for file storage.

**When to use**:
- Leave unset for automatic detection if known storage classes exist
- Set explicitly when using custom or non-standard storage classes
- Must support RWX access mode for shared file storage

**Valid values**: Storage class name supporting ReadWriteMany access mode

**Impact**: CP4D uses this for shared file storage across pods. Incorrect storage class or one not supporting RWX will cause deployment to fail.

**Related variables**:
- `cpd_metadata_storage_class`: Separate storage for metadata (RWO)

**Note**: Known supported classes: `ibmc-file-gold-gid` (IBM Cloud), `ocs-storagecluster-cephfs` (OCS), `azurefiles-premium` (Azure). See [CP4D Storage Considerations](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.6.x?topic=planning-storage-considerations) for details.

#### cpd_metadata_storage_class
Storage class for CP4D Zen metadata database (must support ReadWriteOnce).

- **Required** (if known storage classes not available)
- Environment Variable: `CPD_METADATA_STORAGE_CLASS`
- Default: `ibmc-block-gold`, `ocs-storagecluster-ceph-rbd`, or `managed-premium` (if available)

**Purpose**: Specifies the storage class for CP4D Zen metadata database, which requires ReadWriteOnce (RWO) access mode for block storage.

**When to use**:
- Leave unset for automatic detection if known storage classes exist
- Set explicitly when using custom or non-standard storage classes
- Must support RWO access mode for block storage

**Valid values**: Storage class name supporting ReadWriteOnce access mode

**Impact**: CP4D Zen metadata database uses this for persistent storage. Incorrect storage class or one not supporting RWO will cause deployment to fail.

**Related variables**:
- `cpd_primary_storage_class`: Separate storage for primary/file storage (RWX)

**Note**: Known supported classes: `ibmc-block-gold` (IBM Cloud), `ocs-storagecluster-ceph-rbd` (OCS), `managed-premium` (Azure). Block storage typically provides better performance for databases.

#### cpd_operators_namespace
Namespace for CP4D operators installation.

- **Optional**
- Environment Variable: `CPD_OPERATORS_NAMESPACE`
- Default: `ibm-cpd-operators`

**Purpose**: Specifies the namespace where CP4D operators will be installed. This follows the specialized installation model with separate operator and instance namespaces.

**When to use**:
- Use default (`ibm-cpd-operators`) for standard deployments
- Set custom namespace for specific organizational requirements
- Must be different from `cpd_instance_namespace`

**Valid values**: Valid Kubernetes namespace name

**Impact**: All CP4D operators (platform, zen, common services, etc.) are installed in this namespace. The namespace must not conflict with the instance namespace.

**Related variables**:
- `cpd_instance_namespace`: Separate namespace for CP4D instance workloads

**Note**: CP4D uses a specialized installation model with operators in one namespace (`ibm-cpd-operators`) and instance workloads in another (`ibm-cpd`). This provides better isolation and management.

#### cpd_instance_namespace
Namespace for CP4D instance workloads.

- **Optional**
- Environment Variable: `CPD_INSTANCE_NAMESPACE`
- Default: `ibm-cpd`

**Purpose**: Specifies the namespace where CP4D instance workloads (Zen, services, databases) will be deployed. Operators in `cpd_operators_namespace` watch and manage resources in this namespace.

**When to use**:
- Use default (`ibm-cpd`) for standard deployments
- Set custom namespace for specific organizational requirements
- Must be different from `cpd_operators_namespace`

**Valid values**: Valid Kubernetes namespace name

**Impact**: All CP4D instance workloads (Zen, MinIO, PostgreSQL, services) are deployed in this namespace. Operators watch this namespace for custom resources.

**Related variables**:
- `cpd_operators_namespace`: Separate namespace for CP4D operators

**Note**: CP4D uses a specialized installation model with operators in `ibm-cpd-operators` and instance workloads in `ibm-cpd`. This separation provides better isolation and follows CP4D best practices.

#### cpd_scale_config
Resource scaling configuration for CP4D instance.

- **Optional**
- Environment Variable: `CPD_SCALE_CONFIG`
- Default: `medium`

**Purpose**: Adjusts resource allocation (CPU, memory, replicas) for CP4D components to match workload requirements and increase processing capacity.

**When to use**:
- Use `medium` (default) for standard production deployments
- Use `small` for development/test environments
- Use `large` for high-capacity production environments
- Adjust based on expected workload and performance requirements

**Valid values**: `small`, `medium`, `large` (or other supported scale configurations)

**Impact**: Determines resource requests/limits and replica counts for CP4D components. Larger scales require more cluster resources but provide better performance and capacity.

**Related variables**:
- `cpd_product_version`: Available scale options may vary by version

**Note**: See [Managing resources](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=services-manually-scaling#reference_mkn_x4g_wpb__control-plane-scale) for detailed resource requirements per scale configuration. Ensure your cluster has sufficient resources for the selected scale.

#### cpd_admin_username
CP4D admin username for API authentication.

- **Optional**
- Environment Variable: `CPD_ADMIN_USERNAME`
- Default: `cpadmin`

**Purpose**: Specifies the CP4D admin username for authenticating with CP4D APIs. Used when the role needs to interact with CP4D services.

**When to use**:
- Leave as default (`cpadmin`) if you haven't changed the initial admin username
- Set explicitly if you changed the admin username after CP4D installation
- Required for API operations that need admin authentication

**Valid values**: Valid CP4D admin username string

**Impact**: Used for CP4D API authentication. Incorrect username will cause API operations to fail.

**Related variables**:
- `cpd_admin_password`: Password for this admin user

**Note**: The default `cpadmin` is the standard CP4D admin username. Only change if you've customized the admin username after installation.

#### cpd_admin_password
CP4D admin password for API authentication.

- **Optional**
- Environment Variable: `CPD_ADMIN_PASSWORD`
- Default: Retrieved from `admin-user-details` secret in `cpd_instance_namespace`

**Purpose**: Specifies the CP4D admin password for authenticating with CP4D APIs. Used when the role needs to interact with CP4D services.

**When to use**:
- Leave unset (recommended) to auto-retrieve from cluster secret
- Set explicitly if you changed the admin password after CP4D installation
- Required for API operations that need admin authentication

**Valid values**: Valid CP4D admin password string

**Impact**: Used for CP4D API authentication. If not set, the role retrieves the initial admin password from the cluster. Incorrect password will cause API operations to fail.

**Related variables**:
- `cpd_admin_username`: Username for this admin password
- `cpd_instance_namespace`: Namespace containing the password secret

**Note**: The role automatically retrieves the initial admin password from the `admin-user-details` secret if not provided. Only set this if you've changed the password after installation. Keep passwords secure and do not commit to source control.

## Example Playbook

### Install Cloud Pak for Data 5.1.3
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cpd_product_version: 5.1.3
    cpd_primary_storage_class: ibmc-file-gold-gid
    cpd_metadata_storage_class: ibmc-block-gold
  roles:
    - ibm.mas_devops.cp4d
```

### Install Cloud Pak for Data 5.2.0
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cpd_product_version: 5.2.0
    cpd_primary_storage_class: ibmc-file-gold-gid
    cpd_metadata_storage_class: ibmc-block-gold
  roles:
    - ibm.mas_devops.cp4d
```

## Run Role Playbook

```bash
export CPD_PRODUCT_VERSION=5.2.0
export CPD_PRIMARY_STORAGE_CLASS=ibmc-file-gold-gid
export CPD_METADATA_STORAGE_CLASS=ibmc-block-gold
export IBM_ENTITLEMENT_KEY=xxxxx
ansible-playbook ibm.mas_devops.run_role
```

## License

EPL-2.0
