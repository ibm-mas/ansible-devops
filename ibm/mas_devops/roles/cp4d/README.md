# cp4d

This role installs or upgrades [IBM Cloud Pak for Data](https://www.ibm.com/uk-en/products/cloud-pak-for-data) Operator in the target cluster. It assumes that you have already installed the IBM Maximo Operator Catalog and configured Certificate Manager in the target cluster. These actions are performed by the [ibm_catalogs](ibm_catalogs.md) [cert_manager](cert_manager.md) roles in this collection.

!!! warning "Maximo tailored installation"
    This role performs a **Maximo tailored installation** of Cloud Pak for Data that matches the configuration the Maximo team use internally.  It does not support further post-install configuration beyond the configuration supported by the role, and it does not support every possible way to configure Cloud Pak for Data — it sets the platform up in a very specific way (namespaces, storage classes, Zen control plane sizing, licensing, and the set of CPD services supported by the [cp4d_service](cp4d_service.md) role).

    Customers who need direct control over customizing their Cloud Pak for Data installation can choose to install and manage Cloud Pak for Data themselves; the MAS applications will work against any correctly configured CPD instance.  When installing and managing CPD yourself, you are responsible for the CPD lifecycle (installation, upgrades, and any configuration you apply).

Cloud Pak for Data will be configured as a [specialized installation](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=planning-architecture)

!!! info
    A specialized installation allows a user with project administrator permissions to install the software after a cluster administrator completes the initial cluster setup.  A specialized installation also facilitates strict division between Red Hat OpenShift Container Platform projects (Kubernetes namespaces).

    In a specialized installation, the IBM Cloud Pak foundational services operators are installed in the ibm-common-services project and the Cloud Pak for Data operators are installed in a separate project (typically cpd-operators). Each project has a dedicated:

    - Operator group, which specifies the OwnNamespace installation mode
    - NamespaceScope Operator, which allows the operators in the project to manage operators and service workloads in specific projects

    In this way, you can specify different settings for the IBM Cloud Pak foundational services and for the Cloud Pak for Data operators.

Currently supported Cloud Pak for Data release versions are:

- 5.2.0 (installed via OLM)
- 5.3.1 (platform installed via OLM, services installed via Helm)
- 5.4.0 (installed via Helm)

!!! tip
    For more information about CPD versioning, see [IBM Cloud Pak for data Operator and operand versions](https://www.ibm.com/docs/en/software-hub/5.2.x?topic=planning-operator-operand-versions)

## Cloud Pak for Data Version Mapping
Users can choose to install a specific version of Cloud Pak for Data by setting `CPD_PRODUCT_VERSION` variable. However, by default, the version of Cloud Pak for Data will be determined by the version of the Maximo Operator Catalog that is installed in the cluster. If `CPD_PRODUCT_VERSION` variable is not defined, and the role is not able to find the Maximo Operator Catalog, then the role will default to installing the Cloud Pak for Data version supported by the latest released MAS catalog.

## Upgrade
The role will automatically install or upgrade (if targeted to an existing CPD deployment) the corresponding Zen version associated to the chosen Cloud Pak for Data release, for example:

- Cloud Pak for Data release version `5.2.0` installs Zen/Control Plane version `6.2.0`
- Cloud Pak for Data release version `5.3.1` installs Zen/Control Plane version `6.4.0`
- Cloud Pak for Data release version `5.4.0` installs Zen/Control Plane version `6.10.0`

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
persistentvolumeclaim/export-zen-minio-2               Bound    pvc-e0dd1dc-916d-4b15-9d9c-351db0a2b47f   20Gi       RWO            ibmc-block-gold   17h
persistentvolumeclaim/ibm-cs-postgres-backup           Bound    pvc-ef788b99-784f-4531-a1b3-12611f112551   20Gi       RWO            ibmc-block-gold   16h
persistentvolumeclaim/ibm-zen-objectstore-backup-pvc   Bound    pvc-d5e61dcf-65a3-4930-9cbf-ab80d04dda00   20Gi       RWO            ibmc-block-gold   16h
persistentvolumeclaim/zen-metastore-edb-1              Bound    pvc-19d44f17-05ab-4dc0-bb5d-1b5f15ffd201   20Gi       RWO            ibmc-block-gold   17h
persistentvolumeclaim/zen-metastore-edb-2              Bound    pvc-741ea444-b6f0-44ff-a123-bb4615d97381   20Gi       RWO            ibmc-block-gold   17h
```

!!! tip
    You can retrieve the Initial Cloud Pak for Data password from the **admin-user-details** secret: `oc -n ibm-cpd get secret admin-user-details -o jsonpath="{.data.initial_admin_password}" | base64 -d`. After installation the role automatically looks up the CPD admin username and password from the cluster secrets (`ibm-iam-bindinfo-platform-auth-idp-credentials` for CPD 4.8+, `admin-user-details` for CPD 4.6) — they are resolved by the role rather than set through its variables.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`cpd_product_version`](#cpd_product_version) | No | Determined by installed MAS catalog version |
| [`ibm_entitlement_key`](#ibm_entitlement_key) | Yes | None |
| [`cpd_entitlement_key`](#cpd_entitlement_key) | No | Value of `ibm_entitlement_key` |
| [`cpd_primary_storage_class`](#cpd_primary_storage_class) | Conditional | Auto-detected |
| [`cpd_metadata_storage_class`](#cpd_metadata_storage_class) | Conditional | Auto-detected |
| [`cpd_operators_namespace`](#cpd_operators_namespace) | No | `ibm-cpd-operators` |
| [`cpd_instance_namespace`](#cpd_instance_namespace) | No | `ibm-cpd` |
| [`cpd_scale_config`](#cpd_scale_config) | No | `medium` |

The storage class variables are only required when auto-detection does not find a known storage class; for production deployments we recommend always setting them explicitly.

### Installation

#### cpd_product_version

Cloud Pak for Data release version to install — `5.2.0` (OLM), `5.3.1` (platform via OLM, services via Helm), or `5.4.0` (Helm). The version determines the Zen/Control Plane version and the features and compatibility requirements.

- **Optional**
- Environment Variable: `CPD_PRODUCT_VERSION`
- Default: Determined by installed MAS catalog version

If not set, the version is determined by the installed Maximo Operator Catalog, or the CP4D version supported by the latest released MAS catalog when the catalog cannot be found. It also determines the compatible CPD service versions and the available `cpd_scale_config` options; see [CP4D Operator and operand versions](https://www.ibm.com/docs/en/software-hub/5.2.x?topic=planning-operator-operand-versions) for version-specific details.

#### ibm_entitlement_key

IBM entitlement key for accessing container images — obtain from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary); it must have valid entitlement for CP4D.

- **Required**
- Environment Variable: `IBM_ENTITLEMENT_KEY`
- Default: None

Provides authentication to IBM Container Registry for pulling CP4D container images; without a valid key, image pulls will fail and CP4D installation cannot proceed. Keep the key secure and do not commit it to source control — it can be overridden for CP4D-specific scenarios with `cpd_entitlement_key`.

#### cpd_entitlement_key

CP4D-specific entitlement key override (primarily for development).

- **Optional**
- Environment Variable: `CPD_ENTITLEMENT_KEY`
- Default: Value of `ibm_entitlement_key`

When set, this key is used instead of `ibm_entitlement_key` for CP4D image pulls. Most deployments should use `ibm_entitlement_key` only; this override is primarily for development scenarios where different keys are needed for different components.

### Storage

#### cpd_primary_storage_class

Primary storage class for CP4D — must support ReadWriteMany (RWX) access mode for shared file storage.

- **Required** when auto-detection does not find a known storage class
- Environment Variable: `CPD_PRIMARY_STORAGE_CLASS`
- Default: Auto-detected (`ibmc-file-gold-gid`, `ocs-storagecluster-cephfs`, or `azurefiles-premium`)

CP4D uses this for shared file storage across pods; a storage class that does not support RWX will cause the deployment to fail. See [CP4D Storage Considerations](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.6.x?topic=planning-storage-considerations) for details.

#### cpd_metadata_storage_class

Storage class for the CP4D Zen metadata database — must support ReadWriteOnce (RWO) access mode for block storage, which typically provides better performance for databases.

- **Required** when auto-detection does not find a known storage class
- Environment Variable: `CPD_METADATA_STORAGE_CLASS`
- Default: Auto-detected (`ibmc-block-gold`, `ocs-storagecluster-ceph-rbd`, or `managed-premium`)

The Zen metadata database uses this for persistent storage; a storage class that does not support RWO will cause the deployment to fail.

### Namespaces

#### cpd_operators_namespace

Namespace for the CP4D operators installation — any valid Kubernetes namespace name, and must be different from `cpd_instance_namespace`.

- **Optional**
- Environment Variable: `CPD_OPERATORS_NAMESPACE`
- Default: `ibm-cpd-operators`

All CP4D operators (platform, zen, common services, etc.) are installed in this namespace. CP4D uses a specialized installation model with operators in one namespace and instance workloads in another, which provides better isolation and management.

#### cpd_instance_namespace

Namespace for the CP4D instance workloads (Zen, MinIO, PostgreSQL, services) — any valid Kubernetes namespace name, and must be different from `cpd_operators_namespace`.

- **Optional**
- Environment Variable: `CPD_INSTANCE_NAMESPACE`
- Default: `ibm-cpd`

Operators in `cpd_operators_namespace` watch and manage resources in this namespace. This separation provides better isolation and follows CP4D best practices.

### Sizing

#### cpd_scale_config

Resource scaling configuration for the CP4D instance — `small` (development/test environments), `medium` (standard production deployments, default), or `large` (high-capacity production environments).

- **Optional**
- Environment Variable: `CPD_SCALE_CONFIG`
- Default: `medium`

Determines resource requests/limits and replica counts for CP4D components; larger scales require more cluster resources but provide better performance and capacity. Available scale options may vary by `cpd_product_version` — see [Managing resources](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=services-manually-scaling#reference_mkn_x4g_wpb__control-plane-scale) for detailed resource requirements per scale configuration, and ensure your cluster has sufficient resources.

## Example Playbook

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
