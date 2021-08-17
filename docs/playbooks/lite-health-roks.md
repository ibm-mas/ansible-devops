# MAS Core with Health on IBM Cloud

This master playbook will drive the following playbooks in sequence:

- [Provision & setup OCP on IBM Cloud](ocp.md#provision) (20-30 minutes)
- Install dependencies:
    - [Install MongoDb (Community Edition)](dependencies.md#install-mongodb-ce) (15 minutes)
    - [Install Cloud Pak for Data Operator](cp4d.md#install-cp4d) (2 minutes)
    - Install Cloud Pak for Data Services
        - [Db2 Warehouse](cp4d.md#db2-install) with [Db2 Management Console](cp4d.md#db2-install) (1-2 hours)
    - [Create Db2 Warehouse Cluster](cp4d.md#install-db2) (60 minutes)
    - [Additional Db2 configuration for Manage](mas.md#manage-db2-hack)
    - [Install BAS](bas.md#install-bas)(30 minutes)
    - [Install SLS](sls.md#install-sls)
- Install & configure MAS:
    - [Configure Cloud Internet Services integration](mas.md#cloud-internet-services-integration) (Optional, 1 minute)
    - [Install & configure MAS](mas.md#install-mas) (20 minutes)
- Install Health
    - [Install application](mas.md#install-mas-application)
    - [Configure workspace](mas.md#configure-mas-application)

All timings are estimates, see the individual pages for each of these playbooks for more information.

!!! warning
    Db2 in CP4D is currently broken, the db2u pod will never start due to an incorrectly set `tty` setting.  See this [Slack thread](https://ibm-analytics.slack.com/archives/C019EJ0QH4Y/p1625244478403600) for more details.

    Depending how long the CP4D team takes to resolve this problem, we may need to automate the workaround (patch the pod to set tty to false, but only after it reaches a certain point in it's processing).  In the meantime, you must manually intervene, otherwise the playbook will timeout waiting for the Db2 cluster to be ready.

## Required environment variables
- `IBMCLOUD_APIKEY`
- `CLUSTER_NAME`
- `OCP_VERSION`
- `CPD_ENTITLEMENT_KEY` Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)
- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `MAS_ENTITLEMENT_KEY` Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)
- `MAS_CONFIG_DIR` Directory where generated config files will be saved (you may also provide pre-generated config files here)

## Optional environment variables
- `IBMCLOUD_RESOURCEGROUP` creates an IBM Cloud resource group to be used, if none are passed, `Default` resource group will be used.
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
export OCP_VERSION=4.6.34_openshift

# CP4D configuration
export CPD_ENTITLEMENT_KEY=xxx

# MAS configuration
export MAS_INSTANCE_ID=xxx
export MAS_ENTITLEMENT_KEY=xxx

export MAS_CONFIG_DIR=~/masconfig

ansible-playbook playbooks/lite-health-roks.yml
```


## Pre-release build

```bash
# IBM Cloud ROKS configuration
export IBMCLOUD_APIKEY=xxx
export CLUSTER_NAME=xxx
export OCP_VERSION=4.6.34_openshift
export IBMCLOUD_RESOURCEGROUP=your-ibmcloud-resourcegroup

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

ansible-playbook playbooks/lite-health-roks.yml
```


## AirGap Support
This sample playbook supports AirGap install of MAS itself, but not the dependency stack for MAS; everything else will be installed normally.  Refer to [The MAS playbook documentation](mas.md#airgap-install) for full details of how to enable AirGap mode.
