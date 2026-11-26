Install Cloud Pak for Data
===============================================================================

Overview
-------------------------------------------------------------------------------
This sample playbook will install **Cloud Pak for Data** on OpenShift. It can also install additional CP4D services.

Required environment variables
-------------------------------------------------------------------------------

- `CPD_ENTITLEMENT_KEY` Your IBM Entitlement key to access the IBM Container Registry
- `CPD_ENTITLEMENT_USERNAME` Your user name to access the IBM Container Registry

Optional environment variables
-------------------------------------------------------------------------------

- `CPD_INSTALL_PLATFORM` True/False - If you HAVE CP4D already installed in your cluster, then set it to "false"
- `CPD_INSTALL_WSL` True/False - Set to true to install Watson Studio
- `CPD_INSTALL_WML` True/False - Set to true to install Watson Machine Learning
- `CPD_INSTALL_SPARK` True/False - Set to true to install Analytics Engine "Spark"
- `CPD_PRIMARY_STORAGE_CLASS` Storage class (ReadWriteMany) to use for CP4D primary/file storage
- `CPD_METADATA_STORAGE_CLASS` Storage class (ReadWriteOnce) to use for CP4D Zen metadata storage
- `CPD_SERVICE_STORAGE_CLASS` Storage class (ReadWriteMany) to use for CP4D service file storage
- `CPD_SERVICE_BLOCK_STORAGE_CLASS` Storage class (ReadWriteOnce) to use for CP4D service block storage

!!! note
    The storage class variables are only needed for fresh installs, or to override what the roles would resolve themselves: when the CP4D platform or a service is already installed, the roles read the storage classes already in use back from the existing custom resources, falling back to cluster auto-detection when none are found.

See the [cp4d](../roles/cp4d.md) and [cp4d_service](../roles/cp4d_service.md) role documentation for the full set of supported environment variables.

Usage
-------------------------------------------------------------------------------
### Install CPD Platform and Watson Studio Local
```bash
export MAS_CATALOG_VERSION=@@MAS_LATEST_CATALOG@@
export CPD_ENTITLEMENT_KEY=xxx
export CPD_ENTITLEMENT_USERNAME=cp
export CPD_INSTALL_PLATFORM="true"
export CPD_INSTALL_WSL="true"

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.cp4d
```

!!! tip
    If you do not want to set up all the dependencies on your local system, you can run the install inside our docker image as well: `docker run -ti --pull always quay.io/ibmmas/cli`
