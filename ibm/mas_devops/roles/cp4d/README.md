cp4d
====

This role installs or upgrades [IBM Cloud Pak for Data](https://www.ibm.com/uk-en/products/cloud-pak-for-data) Operator in the target cluster.

Currently supported Cloud Pak for Data release versions are:

  - 4.6.0
  - 4.6.3
  - 4.6.4
  - 4.6.6
  - 4.8.0

The role will automatically install or upgrade (if targeted to an existing CPD deployment) the corresponding Zen version associated to the chosen Cloud Pak for Data release, for example:

- Cloud Pak for Data release version `4.6.0` installs Zen/Control Plane version [`4.8.0`](https://github.ibm.com/PrivateCloud/olm-utils/blob/master/ansible-play/config-vars/release-4.6.0.yml#L65).
- Cloud Pak for Data release version `4.6.3` installs Zen/Control Plane version [`4.8.1`](https://github.ibm.com/PrivateCloud/olm-utils/blob/master/ansible-play/config-vars/release-4.6.3.yml#L65).
- Cloud Pak for Data release version `4.6.4` installs Zen/Control Plane version [`4.8.2`](https://github.ibm.com/PrivateCloud/olm-utils/blob/master/ansible-play/config-vars/release-4.6.4.yml#L65).
- Cloud Pak for Data release version `4.6.6` installs Zen/Control Plane version [`4.8.2`](https://github.ibm.com/PrivateCloud/olm-utils/blob/master/ansible-play/config-vars/release-4.6.4.yml#L65).
- Cloud Pak for Data release version `4.8.0` installs Zen/Control Plane version [`5.1.0`](https://github.ibm.com/PrivateCloud/olm-utils/blob/4.8.x/ansible-play/config-vars/release-4.8.0.yml)

For more information about CPD versioning, see [IBM Cloud Pak for Data Operator and operand versions](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=planning-operator-operand-versions)

Cloud Pak for Data version mapping to MAS Catalog
====

Introduced with 4.8.x support, users can still choose to install an specific version of Cloud Pak for Data by setting `CPD_PRODUCT_VERSION` variable. However, by default, now it will possible to install an specific version of Cloud Pak for Data that is compatible with an specific version of MAS catalog (ibm-operator-catalog).
If `CPD_PRODUCT_VERSION` variable is not defined, then the automation will try to find the installed MAS catalog (ibm-operator-catalog) in the target cluster, and lookup the corresponding default Cloud Pak for Data version that is mapped with the retrieved MAS catalog version. If still not able to find the MAS catalog, then by default, the Cloud Pak for Data version will be defined by the version supported by the latest released MAS catalog.

Upgrade
------------------
This role also supports seamlessly CPD control plane (or also called `Zen` service) minor version upgrades (CPD 4.6.x > CPD 4.8.x), and patch version upgrades (i.e CPD 4.8.0 -> CPD 4.8.1).
All you need to do is to define `cpd_product_version` variable to the version you target to upgrade and run this role against an existing CPD instance.

For more information about IBM Cloud Pak for Data upgrade process, refer to the [Cloud Pak for Data official documentation](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=upgrading).

The role assumes that you have already installed the IBM Operator Catalog and configured IBM Cloud Pak Foundational services (only a must have if installing CPD 4.6.x) in the target cluster. These actions are performed by the [ibm_catalogs](ibm_catalogs.md) [common_services](common_services.md) roles in this collection.

Cloud Pak for Data will be configured as a [specialized installation](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=planning-architecture)

!!! info
    A specialized installation allows a user with project administrator permissions to install the software after a cluster administrator completes the initial cluster setup.  A specialized installation also facilitates strict division between Red Hat OpenShift Container Platform projects (Kubernetes namespaces).

    In a specialized installation, the IBM Cloud Pak foundational services operators are installed in the ibm-common-services project and the Cloud Pak for Data operators are installed in a separate project (typically cpd-operators). Each project has a dedicated:

    - Operator group, which specifies the OwnNamespace installation mode
    - NamespaceScope Operator, which allows the operators in the project to manage operators and service workloads in specific projects

    In this way, you can specify different settings for the IBM Cloud Pak foundational services and for the Cloud Pak for Data operators.

Cloud Pak for Data deployment details
------------------

### 4.8.x version:

Cloud Pak for Data 4.8.x leverages Cloud Pak Foundational Services v4, which runs its deployments in isolated/dedicated scope model, that means that its dependencies will be grouped and installed within the Cloud Pak for Data related projects/namespaces. Differently from CPD 4.6.x, there are only two namespaces that will be used: CPD instance namespace (e.g `ibm-cpd`) and CPD operators namespace (e.g `ibm-cpd-operators`).

In the **ibm-cpd-operators** namespace:
```bash
oc -n ibm-cpd-operators get deployments
NAME                                                   READY   UP-TO-DATE   AVAILABLE   AGE
cpd-platform-operator-manager                          1/1     1            1           39d
ibm-common-service-operator                            1/1     1            1           39d
ibm-commonui-operator                                  1/1     1            1           39d
ibm-iam-operator                                       1/1     1            1           39d
ibm-mongodb-operator                                   1/1     1            1           39d
ibm-namespace-scope-operator                           1/1     1            1           39d
ibm-zen-operator                                       1/1     1            1           39d
meta-api-deploy                                        1/1     1            1           39d
operand-deployment-lifecycle-manager                   1/1     1            1           39d
postgresql-operator-controller-manager-1-18-7          1/1     1            1           39d
```

In the **ibm-cpd** namespace:
```
oc -n ibm-cpd get zenservice,ibmcpd,deployments,sts,pvc

NAME                                 STATUS      AGE
zenservice.zen.cpd.ibm.com/lite-cr  Completed   39d

NAME                           AGE
ibmcpd.cpd.ibm.com/ibmcpd-cr   39d

NAME                                                                    READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/common-web-ui                                           1/1     1            1           39d
deployment.apps/ibm-nginx                                               2/2     2            2           39d
deployment.apps/ibm-nginx-tester                                        1/1     1            1           39d
deployment.apps/platform-auth-service                                   1/1     1            1           39d
deployment.apps/platform-identity-management                            1/1     1            1           39d
deployment.apps/platform-identity-provider                              1/1     1            1           39d
deployment.apps/usermgmt                                                2/2     2            2           39d
deployment.apps/zen-audit                                               1/1     1            1           39d
deployment.apps/zen-core                                                2/2     2            2           39d
deployment.apps/zen-core-api                                            2/2     2            2           39d
deployment.apps/zen-watchdog                                            1/1     1            1           39d
deployment.apps/zen-watcher                                             1/1     1            1           39d

NAME                                                         READY   AGE
statefulset.apps/icp-mongodb                                 3/3     39d
statefulset.apps/zen-minio                                   3/3     39d

NAME                                                                     STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS                  AGE
persistentvolumeclaim/ibm-zen-cs-mongo-backup                            Bound    pvc-bdba4bb2-dff5-43cb-a4b6-3540955ccb92   20Gi       RWO            ocs-storagecluster-ceph-rbd   39d
persistentvolumeclaim/ibm-zen-objectstore-backup-pvc                     Bound    pvc-46595a1b-2629-4c62-9e16-6b9553635738   20Gi       RWO            ocs-storagecluster-ceph-rbd   39d
persistentvolumeclaim/mongodbdir-icp-mongodb-0                           Bound    pvc-1d3f7ee5-b2ef-4ca0-8b95-8db79bc88b19   20Gi       RWO            ocs-storagecluster-ceph-rbd   39d
persistentvolumeclaim/mongodbdir-icp-mongodb-1                           Bound    pvc-9dada920-c6be-40f2-b4e2-56c989935a16   20Gi       RWO            ocs-storagecluster-ceph-rbd   39d
persistentvolumeclaim/mongodbdir-icp-mongodb-2                           Bound    pvc-27713ee7-4d57-49e2-94ce-6955bbcd74f4   20Gi       RWO            ocs-storagecluster-ceph-rbd   39d
persistentvolumeclaim/zen-metastore-edb-1                                Bound    pvc-34319e6e-ef9b-40cf-adf4-d70a1ab94321   10Gi       RWO            ocs-storagecluster-ceph-rbd   39d
persistentvolumeclaim/zen-metastore-edb-2                                Bound    pvc-d9a5c1f3-a423-44b0-a7af-601359cbc5cd   10Gi       RWO            ocs-storagecluster-ceph-rbd   39d
```

!!! tip
    You can retrieve the Cloud Pak for Data password from the **ibm-iam-bindinfo-platform-auth-idp-credentials** secret: `oc -n ibm-cpd get secret ibm-iam-bindinfo-platform-auth-idp-credentials -o jsonpath="{.data.admin_password}" | base64 -d`

### 4.6.x version:

Cloud Pak for Data 4.6.x is made up of many moving parts across multiple namespaces.

In the **ibm-common-services** namespace:
```bash
oc -n ibm-common-services get deployments
NAME                                   READY   UP-TO-DATE   AVAILABLE   AGE
cert-manager-cainjector                1/1     1            1           85m
cert-manager-controller                1/1     1            1           85m
cert-manager-webhook                   1/1     1            1           85m
configmap-watcher                      1/1     1            1           85m
ibm-cert-manager-operator              1/1     1            1           87m
ibm-common-service-operator            1/1     1            1           92m
ibm-common-service-webhook             1/1     1            1           91m
ibm-namespace-scope-operator           1/1     1            1           91m
ibm-zen-operator                       1/1     1            1           87m
meta-api-deploy                        1/1     1            1           86m
operand-deployment-lifecycle-manager   1/1     1            1           90m
secretshare                            1/1     1            1           91m
```

In the **ibm-cpd-operators** namespace:
```bash
oc -n ibm-cpd-operators get deployments
NAME                            READY   UP-TO-DATE   AVAILABLE   AGE
cpd-platform-operator-manager   1/1     1            1           87m
ibm-common-service-operator     1/1     1            1           87m
ibm-namespace-scope-operator    1/1     1            1           87m
```

In the **ibm-cpd** namespace:
```
oc -n ibm-cpd get zenservice,ibmcpd,deployments,sts
NAME                                 AGE
zenservice.zen.cpd.ibm.com/lite-cr   81m

NAME                        AGE
ibmcpd.cpd.ibm.com/ibmcpd   85m

NAME                                READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/ibm-nginx           3/3     3            3           62m
deployment.apps/usermgmt            3/3     3            3           64m
deployment.apps/zen-audit           1/1     1            1           56m
deployment.apps/zen-core            3/3     3            3           55m
deployment.apps/zen-core-api        3/3     3            3           55m
deployment.apps/zen-data-sorcerer   2/2     2            2           48m
deployment.apps/zen-watchdog        1/1     1            1           48m
deployment.apps/zen-watcher         1/1     1            1           55m

NAME                               READY   AGE
statefulset.apps/dsx-influxdb      1/1     51m
statefulset.apps/zen-metastoredb   3/3     68m
```

!!! tip
    You can retrieve the Cloud Pak for Data password from the **admin-user-details** secret: `oc -n ibm-cpd get secret admin-user-details -o jsonpath="{.data.initial_admin_password}" | base64 -d`




Role Variables
--------------
### cpd_product_version
Defines the IBM Cloud Pak for Data release version to be installed.

- **Required**
- Environment Variable: `CPD_PRODUCT_VERSION`
- Default Value: Defined by the installed MAS catalog version

### ibm_entitlement_key
Provide your [IBM entitlement key](https://myibm.ibm.com/products-services/containerlibrary).

- **Required**
- Environment Variable: `IBM_ENTITLEMENT_KEY`
- Default: None

### cpd_entitlement_key
An IBM entitlement key specific for Cloud Pak for Data installation, primarily used to override `ibm_entitlement_key` in development.

- Optional
- Environment Variable: `CPD_ENTITLEMENT_KEY`
- Default: None

### cpd_primary_storage_class
Primary storage class for Cloud Pak for Data.

- **Required** if one of the known supported storage classes is not installed in the cluster.
- Environment Variable: `CPD_PRIMARY_STORAGE_CLASS`
- Default Value: `ibmc-file-gold-gid`, `ocs-storagecluster-cephfs`, `azurefiles-premium` (if available)

### cpd_metadata_storage_class
Storage class for the Cloud Pak for Data Zen meta database.

- **Required** if one of the known supported storage classes is not installed in the cluster.
- Environment Variable: `CPD_METADATA_STORAGE_CLASS`
- Default Value: `ibmc-block-gold`, `ocs-storagecluster-ceph-rbd`, or `managed-premium` (if available)

### cpd_operators_namespace
Namespace where Cloud Pak for Data operators will be installed.

- Optional
- Environment Variable: `CPD_OPERATORS_NAMESPACE`
- Default Value: `ibm-cpd-operators`

### cpd_instance_namespace
Namespace that the Cloud Pak for Data operators will be configured to watch.

- Optional
- Environment Variable: `CPD_INSTANCE_NAMESPACE`
- Default Value: `ibm-cpd`

### cpd_scale_config
Adjust and scale the resources for your Cloud Pak for Data instance to increase processing capacity.
For more information, refer to [Managing resources](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=services-manually-scaling#reference_mkn_x4g_wpb__control-plane-scale) in IBM Cloud Pak for Data documentation.

- Optional
- Environment Variable: `CPD_SCALE_CONFIG`
- Default Value: `medium`

### cpd_admin_username
The CP4D Admin username to authenticate with CP4D APIs. If you didn't change the initial admin username after installing CP4D then you don't need to provide this.

- Optional
- Environment Variable: `CPD_ADMIN_USERNAME`
- Default Value: 
  - `admin` (CPD 4.6)
  - `cpadmin` (CPD 4.8) 

### cpd_admin_password
The CP4D Admin User password to call CP4D API to provision Discovery Instance. If you didn't change the initial admin password after CP4D install, you don't need to provide it.  The initial admin user password for `admin` or `cpdamin` will be used.

- Optional
- Environment Variable: `CPD_ADMIN_PASSWORD`
- Default Value: 
    - CPD 4.6: Looked up from the `admin-user-details` secret in the `cpd_instance_namespace` namespace
    - CPD 4.8: Looked up from the `ibm-iam-bindinfo-platform-auth-idp-credentials` secret in the `cpd_instance_namespace` namespace

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cpd_product_version: 4.8.0
    cpd_primary_storage_class: ibmc-file-gold-gid
    cpd_metadata_storage_class: ibmc-block-gold
  roles:
    - ibm.mas_devops.cp4d
```

License
-------

EPL-2.0
