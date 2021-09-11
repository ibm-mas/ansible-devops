# MAS Core Service on IBM Cloud ROKS

This master playbook will drive the following playbooks in sequence:

- [Provision & setup OCP on IBM Cloud](ocp.md#provision) (20-30 minutes)
- Install dependencies:
    - [Install MongoDb (Community Edition)](dependencies.md#install-mongodb-ce) (15 minutes)
    - [Install BAS](bas.md#install-bas) (coming soon)
    - [Install SLS](sls.md#install-sls) (10 minutes)
- Install & configure MAS:
    - [Configure Cloud Internet Services integration](mas.md#cloud-internet-services-integration) (Optional, 1 minute)
    - [Install & configure MAS](mas.md#install-mas) (25 minutes)

All timings are estimates, see the individual pages for each of these playbooks for more information.

## Required environment variables
- `IBMCLOUD_APIKEY`
- `CLUSTER_NAME`
- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `MAS_ENTITLEMENT_KEY` Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)
- `MAS_CONFIG_DIR` Directory where generated config files will be saved (you may also provide pre-generated config files here)

## Optional environment variables
- `IBMCLOUD_RESOURCEGROUP` creates an IBM Cloud resource group to be used, if none are passed, `Default` resource group will be used.
- `OCP_VERSION` to override the default version of OCP to use (latest 4.6 release)
- `W3_USERNAME` to enable access to pre-release development builds of MAS
- `ARTIFACTORY_APIKEY`  to enable access to pre-release development builds of MAS
- `MONGODB_NAMESPACE` overrides the Kubernetes namespace where the MongoDb CE operator will be installed, this will default to `mongoce`
- `MAS_CATALOG_SOURCE` to override the use of the IBM Operator Catalog as the catalog source
- `MAS_CHANNEL` to override the use of the `8.x` channel
- `MAS_DOMAIN` to set a custom domain for the MAS installation
- `MAS_ICR_CP` to override the value MAS uses for the IBM Entitled Registry (`cp.icr.io/cp`)
- `MAS_ICR_CPOPEN` to override the value MAS uses for the IBM Open Registry (`icr.io/cpopen`)
- `MAS_ENTITLEMENT_USERNAME` to override the username MAS uses to access content in the IBM Entitled Registry
- `CIS_CRN` to enable integration with IBM Cloud Internet Services (CIS) for DNS & certificate management
- `CIS_SUBDOMAIN` if you want to use a subdomain within your CIS instance

!!! tip
    `MAS_ICR_CP`, `MAS_ICR_CPOPEN`, & `MAS_ENTITLEMENT_USERNAME` are primarily used when working with pre-release builds in conjunction with `W3_USERNAME`, `ARTIFACTORY_APIKEY` and the `MAS_CATALOG_SOURCE` environment variables.


## Release build

```bash
# IBM Cloud ROKS configuration
export IBMCLOUD_APIKEY=xxx
export CLUSTER_NAME=xxx

# MAS configuration
export MAS_INSTANCE_ID=xxx
export MAS_ENTITLEMENT_KEY=xxx

export MAS_CONFIG_DIR=~/masconfig

ansible-playbook playbooks/only-manage-roks.yml
```


## Pre-release build

```bash
# IBM Cloud ROKS configuration
export IBMCLOUD_APIKEY=xxx
export CLUSTER_NAME=xxx

# CP4D configuration
export CPD_ENTITLEMENT_KEY=xxx

# Allow development catalogs to be installed
export W3_USERNAME=xxx
export ARTIFACTORY_APIKEY=xxx

# MAS configuration
export MAS_CATALOG_SOURCE=ibm-mas-operators
export MAS_CHANNEL=8.5.0-pre.m2dev85
export MAS_INSTANCE_ID=$CLUSTER_NAME

export MAS_ICR_CP=wiotp-docker-local.artifactory.swg-devops.com
export MAS_ICR_CPOPEN=wiotp-docker-local.artifactory.swg-devops.com
export MAS_ENTITLEMENT_USERNAME=$W3_USERNAME_LOWERCASE
export MAS_ENTITLEMENT_KEY=$ARTIFACTORY_APIKEY

export MAS_CONFIG_DIR=~/masconfig

ansible-playbook playbooks/only-manageroks.yml
```
