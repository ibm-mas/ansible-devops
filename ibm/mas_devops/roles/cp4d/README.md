cp4d
====

This role installs [IBM Cloud Pak for Data](https://www.ibm.com/uk-en/products/cloud-pak-for-data) Operator in the target cluster.

The [cp4d_hack_worker_nodes](cp4d_hack_worker_nodes.md) role must have been executed during cluster set up to update the cluster's global image pull secret and reload all worker nodes.  Unfortunately Cloud Pak for data does not support using image pull secrets attached to service accounts in the namespace.

The role assumes that you have already installed the IBM Operator Catalog and configured IBM Cloud Pak Foundational services in the target cluster.  These actions are performed by the [ibm_catalogs](ibm_catalogs.md) [common_services](common_services.md) roles in this collection.

Cloud Pak for Data will be configured as a [specialized installation](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=planning-architecture#architecture__deployment-architecture)

!!! info
    A specialized installation allows a user with project administrator permissions to install the software after a cluster administrator completes the initial cluster setup.  A specialized installation also facilitates strict division between Red Hat OpenShift Container Platform projects (Kubernetes namespaces).

    In a specialized installation, the IBM Cloud Pak foundational services operators are installed in the ibm-common-services project and the Cloud Pak for Data operators are installed in a separate project (typically cpd-operators). Each project has a dedicated:

    - Operator group, which specifies the OwnNamespace installation mode
    - NamespaceScope Operator, which allows the operators in the project to manage operators and service workloads in specific projects

    In this way, you can specify different settings for the IBM Cloud Pak foundational services and for the Cloud Pak for Data operators.

Cloud Pak for Data is made up of many moving parts across multiple namespaces.

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


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cpd_primary_storage_class: ibmc-file-gold-gid
    cpd_metadata_storage_class: ibmc-block-gold
  roles:
    - ibm.mas_devops.cp4d
```

License
-------

EPL-2.0
