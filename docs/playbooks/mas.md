# MAS Playbooks

## Install MAS
Before you use this playbook you will likely want to edit the `mas_config` variable to supply your own configurtation, instead of the sample data provided.

### Required environment variables
- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `MAS_ENTITLEMENT_KEY` Provide your IBM entitlement key

### Optional environment variables
- `MAS_CATALOG_SOURCE` Set to `ibm-mas-operators` if you want to deploy pre-release development builds
- `MAS_CHANNEL` Override the default release channel (8.x)
- `MAS_ICR_CP` Override the registry source for all container images deployed by the MAS operator
- `MAS_ICR_CPOPEN` Override the registry source for all container images deployed by the MAS operator
- `MAS_ENTITLEMENT_USERNAME` Override the default entitlement username (cp)


### Example usage: release build

```bash
export MAS_INSTANCE_ID=xxx
export MAS_ENTITLEMENT_KEY=xxx

ansible-playbook playbooks/mas/install-suite.yml
```

!!! note
    Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)


### Example usage: pre-release build

```bash
export MAS_CATALOG_SOURCE=ibm-mas-operators
export MAS_CHANNEL=8.5.0-pre.m2dev85
export MAS_INSTANCE_ID=xxx

export MAS_ICR_CP=wiotp-docker-local.artifactory.swg-devops.com
export MAS_ICR_CPOPEN=wiotp-docker-local.artifactory.swg-devops.com
export MAS_ENTITLEMENT_USERNAME=$W3_USERNAME_LOWERCASE
export MAS_ENTITLEMENT_KEY=$ARTIFACTORY_APIKEY

ansible-playbook playbooks/mas/install-suite.yml
```

!!! important
    You must have already installed the development (pre-release) catalogs, pre-release builds are not available directly from the IBM Operator Catalog.
