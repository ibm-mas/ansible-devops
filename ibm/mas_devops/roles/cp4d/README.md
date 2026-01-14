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
Defines the IBM Cloud Pak for Data release version to be installed.

- **Required**
- Environment Variable: `CPD_PRODUCT_VERSION`
- Default Value: Defined by the installed MAS catalog version

#### ibm_entitlement_key
Provide your [IBM entitlement key](https://myibm.ibm.com/products-services/containerlibrary).

- **Required**
- Environment Variable: `IBM_ENTITLEMENT_KEY`
- Default: None

#### cpd_entitlement_key
An IBM entitlement key specific for Cloud Pak for Data installation, primarily used to override `ibm_entitlement_key` in development.

- **Optional**
- Environment Variable: `CPD_ENTITLEMENT_KEY`
- Default: None

#### cpd_primary_storage_class
Primary storage class for Cloud Pak for Data. For more details please read the [Storage Considerations for IBM Cloud Pak for Data](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.6.x?topic=planning-storage-considerations).
According to the mentioned documentation, Cloud Pak for Data uses the following access modes for storage classes:
 - RWX file storage: ocs-storagecluster-cephfs
 - RWX file storage: ibmc-file-gold-gid

- **Required** if one of the known supported storage classes is not installed in the cluster.
- Environment Variable: `CPD_PRIMARY_STORAGE_CLASS`
- Default Value: `ibmc-file-gold-gid`, `ocs-storagecluster-cephfs`, `azurefiles-premium` (if available)

#### cpd_metadata_storage_class
Storage class for the Cloud Pak for Data Zen meta database. This must support ReadWriteOnce (RWO access) access mode.

- **Required** if one of the known supported storage classes is not installed in the cluster.
- Environment Variable: `CPD_METADATA_STORAGE_CLASS`
- Default Value: `ibmc-block-gold`, `ocs-storagecluster-ceph-rbd`, or `managed-premium` (if available)

#### cpd_operators_namespace
Namespace where Cloud Pak for Data operators will be installed.

- **Optional**
- Environment Variable: `CPD_OPERATORS_NAMESPACE`
- Default Value: `ibm-cpd-operators`

#### cpd_instance_namespace
Namespace that the Cloud Pak for Data operators will be configured to watch.

- Optional
- Environment Variable: `CPD_INSTANCE_NAMESPACE`
- Default Value: `ibm-cpd`

#### cpd_scale_config
Adjust and scale the resources for your Cloud Pak for Data instance to increase processing capacity. For more information, refer to [Managing resources](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=services-manually-scaling#reference_mkn_x4g_wpb__control-plane-scale) in IBM Cloud Pak for Data documentation.

- **Optional**
- Environment Variable: `CPD_SCALE_CONFIG`
- Default Value: `medium`

#### cpd_admin_username
The CP4D Admin username to authenticate with CP4D APIs. If you didn't change the initial admin username after installing CP4D then you don't need to provide this.

- Optional
- Environment Variable: `CPD_ADMIN_USERNAME`
- Default Value:
  - `cpadmin`

#### cpd_admin_password
The CP4D Admin User password to call CP4D API to provision Discovery Instance. If you didn't change the initial admin password after CP4D install, you don't need to provide it.  The initial admin user password for `admin` or `cpdamin` will be used.

- **Optional**
- Environment Variable: `CPD_ADMIN_PASSWORD`
- Default Value: Looked up from the `ibm-iam-bindinfo-platform-auth-idp-credentials` secret in the `cpd_instance_namespace` namespace

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
