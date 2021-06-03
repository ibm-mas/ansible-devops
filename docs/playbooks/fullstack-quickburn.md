# Full Stack on IBM Cloud ROKS

This playbook is a master playbook that will drive the following playbooks in sequence:

- [Provision & setup Quickburn](ocp.md#quickburn) (25 minutes)
- [Install & configure MAS](mas.md#install-mas) (10 minutes)

All timings are estimates, see the individual pages for each of these playbooks for more information.  Due to the size limtations in QuickBurn a full stack is not possible.

## Required environment variables
- `FYRE_USERNAME`
- `FYRE_APIKEY`
- `FYRE_PRODUCT_ID`
- `CLUSTER_NAME`
- `OCP_VERSION`
- `MAS_INSTANCE_ID`
- `MAS_ENTITLEMENT_KEY`

## Optional environment variables
- `FYRE_CLUSTER_SIZE`
- `W3_USERNAME`
- `ARTIFACTORY_APIKEY`
- `MAS_CATALOG_SOURCE`
- `MAS_CHANNEL`
- `MAS_INSTANCE_ID`
- `MAS_ICR_CP`
- `MAS_ICR_CPOPEN`
- `MAS_ENTITLEMENT_USERNAME`
- `MAS_ENTITLEMENT_KEY`


## Release build

```bash
# Fyre credentials
export FYRE_USERNAME=xxx
export FYRE_APIKEY=xxx
export FYRE_PRODUCT_ID=225
# Cluster configuration
export CLUSTER_NAME=xxx
export OCP_VERSION=4.6.16

# MAS configuration
export MAS_INSTANCE_ID=xxx
export MAS_ENTITLEMENT_KEY=xxx

ansible-playbook playbooks/fullstack-quickburn.yml
```

!!! note
    Lookup your entitlement keys from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)


## Pre-release build

```bash
# Fyre credentials
export FYRE_USERNAME=xxx
export FYRE_APIKEY=xxx
export FYRE_PRODUCT_ID=225

# Cluster configuration
export CLUSTER_NAME=xxx
export OCP_VERSION=4.6.16

# Allow development catalogs to be installed
export W3_USERNAME=xxx
export ARTIFACTORY_APIKEY=xxx

# MAS configuration
export MAS_CATALOG_SOURCE=ibm-mas-operators
export MAS_CHANNEL=8.5.0-pre.m1dev85
export MAS_INSTANCE_ID=xxx

export MAS_ICR_CP=wiotp-docker-local.artifactory.swg-devops.com
export MAS_ICR_CPOPEN=wiotp-docker-local.artifactory.swg-devops.com
export MAS_ENTITLEMENT_USERNAME=$W3_USERNAME_LOWERCASE
export MAS_ENTITLEMENT_KEY=$ARTIFACTORY_APIKEY

ansible-playbook playbooks/fullstack-quickburn.yml
```
