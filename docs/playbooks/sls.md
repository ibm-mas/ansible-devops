# SLS Playbooks

## Install sls
Before you use this playbook you will likely want to edit the `mas_config_dir` variable to supply your own configuration, instead of the sample data provided.

### Required environment variables
- `SLS_ENTITLEMENT_KEY` Provide your IBM entitlement key

### Optional environment variables
- `SLS_CATALOG_SOURCE` Set to `ibm-sls-operators` if you want to deploy pre-release development builds
- `SLS_CHANNEL` Override the default release channel (3.x)
- `SLS_ICR_CP` Override the registry source for all container images deployed by the SLS operator
- `SLS_ICR_CPOPEN` Override the registry source for all container images deployed by the SLS operator
- `SLS_ENTITLEMENT_USERNAME` Override the default entitlement username (cp)
- `SLS_NAMESPACE` Override the default entitlement username (ibm-sls)
- `SLS_STORAGE_CLASS` Defines Storage Class to be used by SLS Persistent Volumes
- `SLS_LICENSE_ID` Must be set to the license id specified in the license file when one is provided
- `SLS_REGISTRATION_KEY` optional var when you want to install sls using a registration key you have.

### Example usage: release build

```bash
export SLS_INSTANCE_ID=xxx
export SLS_ENTITLEMENT_KEY=xxx
export SLS_STORAGE_CLASS=xxx

ansible-playbook playbooks/sls/install-sls.yml
```

!!! note
    Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)


### Example usage: pre-release build

```bash
export SLS_CATALOG_SOURCE=ibm-sls-operators
export SLS_CHANNEL=3.1.0-pre.stable
export SLS_INSTANCE_ID=xxx

export SLS_ICR_CP=wiotp-docker-local.artifactory.swg-devops.com
export SLS_ICR_CPOPEN=wiotp-docker-local.artifactory.swg-devops.com
export SLS_ENTITLEMENT_USERNAME=$W3_USERNAME_LOWERCASE
export SLS_ENTITLEMENT_KEY=$ARTIFACTORY_APIKEY
export SLS_STORAGE_CLASS=xxx


ansible-playbook playbooks/sls/install-sls.yml
```

!!! important
    You must have already installed the development (pre-release) catalogs, pre-release builds are not available directly from the IBM Operator Catalog.