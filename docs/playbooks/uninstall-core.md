Uninstall for MAS Core
===============================================================================

This playbook will remove MAS Core Platform and its dependencies from your cluster.  If you have installed any MAS applications you should uninstall them first.  This playbook will effectively undo everything done in the [oneclick-core](oneclick-core.md) playbook.

The following will be removed from the cluster.
- MAS Core Platform for the specified instance ID
- IBM Suite Licensing Service
- MongoDb
- IBM User Data Services
- IBM Certificate Manager
- IBM Cloud Pak Foundational Services
- IBM Maximo Operator Catalog
- Cluster Monitoring (including Grafana)

When using this playbook be sure that nothing else in your cluster is using any of the dependencies that will be removed.  If you wish to skip the removal of one or more dependencies use the optional environment variables documented below to control exactly what is uninstalled.


Usage
-------------------------------------------------------------------------------
### Required environment variables

- `MAS_INSTANCE_ID` Declare the instance ID of MAS to remove

### Required environment variables
Any of these environment variables can be set to `none` to skip the uninstall of the associated dependency, this can be useful if you have multiple MAS instances installed on a single cluster for example.

- `CLUSTER_MONITORING_ACTION`
- `SLS_ACTION`
- `MONGODB_ACTION`
- `UDS_ACTION`
- `CERT_MANAGER_ACTION`
- `COMMON_SERVICES_ACTION`
- `IBM_CATALOGS_ACTION`

!!! warning
    Although you could set the actions to `install` and run the playbook it is strongly recommended not to as it runs through the dependencies in the reverse order that they need to be installed in; use the [oneclick-core](oneclick-core.md) playbook to repair a MAS Core installation.


Example
-------------------------------------------------------------------------------

```bash
export MAS_INSTANCE_ID=inst1

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.uninstall_core
```

!!! tip
    If you do not want to set up all the dependencies on your local system, you can run the install inside our docker image as well: `docker run -ti --pull always quay.io/ibmmas/cli`
