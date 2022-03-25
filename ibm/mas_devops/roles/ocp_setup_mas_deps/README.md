ocp_setup_mas_deps
==================

This role provides support to install operators that are required by MAS to work. The role will deploy Service Binding Operator in all namespaces and Cert Manager in the cert-manager namespace.  The role declares a dependency on `ocp_verify` to ensure that the RedHat Operator Catalog is installed and ready before we try to install the Service Binding Operator from that catalog.
In addition, this role updates cluster's internal image registry settings to increase storage to 400GB (needed only for ROKS Cluster to install full stack of services in CP4D) and to configure custom storage for the Prometheus monitoring service for both the k8s and User Workload (in namespace `openshift-user-workload-monitoring`) Prometheus instances.

For MAS 8.6 or earlier JetStack cert-manager v1.2 is installed into the `cert-manager` namespace.  When used for MAS 8.7+ this role will result in the following operators being installed in the ibm-common-services namespace:
- IBM Cert Manager
- IBM Cloud Pak Foundational Services
- IBM NamespaceScope Operator
- Operand Deployment Lifecycle Manager

For MAS 8.6 or earlier (or when running MAS 8.7 on OCP 4.6) Service Binding Operator v0.8 will be installed from the preview channel.  It is important not to upgrade to later preview builds as they are incompatible with MAS due to breaking API changes in SBO.  For MAS 8.7 or later the stable channel will be used instead, with automatic updates enabled.  In both cases, the operator will be installed in the `openshift-operators` namespace with cluster scope.


Role Variables
--------------
### artifactory_username
Use to enable the install of development catalog sources for pre-release installation.

- Environment Variable: `W3_USERNAME`
- Default Value: None

### artifactory_apikey
Use to enable the install of development catalog sources for pre-release installation.

- Environment Variable: `ARTIFACTORY_APIKEY`
- Default Value: None

### prometheus_retention_period
Adjust the retention period for Prometheus metrics, only used when both `prometheus_storage_class` and `prometheus_alertmgr_storage_class` are set.

- Environment Variable: `PROMETHEUS_RETENTION_PERIOD`
- Default Value: `15d`

### prometheus_storage_class
Declare the storage class for Prometheus' metrics data persistent volume.

- Environment Variable: `PROMETHEUS_STORAGE_CLASS`
- Default Value: None

### prometheus_storage_size
Adjust the size of the volume used to store metrics, only used when both `prometheus_storage_class` and `prometheus_alertmgr_storage_class` are set.

- Environment Variable: `PROMETHEUS_STORAGE_SIZE`
- Default Value: `300Gi`

### prometheus_alertmgr_storage_class
Declare the storage class for AlertManager's persistent volume.

- Environment Variable: `PROMETHEUS_ALERTMGR_STORAGE_CLASS`
- Default Value: None

### prometheus_alertmgr_storage_size
Adjust the size of the volume used by AlertManager, only used when both `prometheus_storage_class` and `prometheus_alertmgr_storage_class` are set.

- Environment Variable: `PROMETHEUS_ALERTMGR_STORAGE_SIZE`
- Default Value: `20Gi`

### prometheus_userworkload_retention_period
Adjust the retention period for User Workload Prometheus metrics, this parameter applies only to the User Workload Prometheus instance.

- Environment Variable: `PROMETHEUS_USERWORKLOAD_RETENTION_PERIOD`
- Default Value: `15d`

### prometheus_userworkload_storage_class
Declare the storage class for User Workload Prometheus' metrics data persistent volume.

- Environment Variable: `PROMETHEUS_USERWORKLOAD_STORAGE_CLASS`
- Default Value: `PROMETHEUS_STORAGE_CLASS`

### prometheus_userworkload_storage_size
Adjust the size of the volume used to store User Workload metrics.

- Environment Variable: `PROMETHEUS_USERWORKLOAD_STORAGE_SIZE`
- Default Value: `300Gi`

### mas_channel
Used to determine whether to install SBO stable channel and the IBM badged cert-manager.

- Environment Variable: `MAS_CHANNEL`
- Default Value: `8.x`


Example Playbook
----------------

```yaml
- hosts: localhost
  vars:
    cluster_type: roks
    prometheus_storage_class: "ibmc-block-gold"
    prometheus_alertmgr_storage_class: "ibmc-file-gold-gid"
  roles:
    - ibm.mas_devops.ocp_setup_mas_deps
```


License
-------

EPL-2.0
