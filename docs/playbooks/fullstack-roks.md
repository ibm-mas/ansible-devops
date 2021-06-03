# Full Stack on IBM Cloud ROKS

This playbook is a master playbook that will drive the following playbooks in sequence:

- [Provision & setup ROKS](ocp.md#roks) (25 minutes)
- Install dependencies:
    - [Install CP4D](cp4d.md#install-cp4d) (5 minutes)
    - [Install Db2](cp4d.md#install-db2) (2 hours)
    - Install MongoDb (coming soon)
    - Install Kafka (coming soon)
    - Install Cloud Object Storage (coming soon)
    - Install Spark (coming soon)
    - Install BAS (coming soon)
    - Install SLS (coming soon)
- [Install & configure MAS](mas.md#install-mas) (10 minutes)
- Install MAS Gen2 applications:
    - Install Manage (coming soon)
    - Install IoT (due 3Q)
    - Install Assist (due 3Q)
    - Install Predict (due 3Q)
    - Install Monitor (due 3Q)
    - Install Safety (due 3Q)
    - Install Visual Inspection (due 3Q)

All timings are estimates, see the individual pages for each of these playbooks for more information.  Gen1 applications will **not** be supported by this collection.

## Required environment variables
- `IBMCLOUD_APIKEY`
- `CLUSTER_NAME`
- `OCP_VERSION`
- `CPD_ENTITLEMENT_KEY`
- `MAS_INSTANCE_ID`
- `MAS_ENTITLEMENT_KEY`

## Optional environment variables
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
# IBM Cloud ROKS configuration
export IBMCLOUD_APIKEY=xxx
export CLUSTER_NAME=xxx
export OCP_VERSION=4.6.28_openshift

# CP4D configuration
export CPD_ENTITLEMENT_KEY=xxx

# MAS configuration
export MAS_INSTANCE_ID=xxx
export MAS_ENTITLEMENT_KEY=xxx

ansible-playbook playbooks/fullstack-roks.yml
```

!!! note
    Lookup your entitlement keys from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)


## Pre-release build

```bash
# IBM Cloud ROKS configuration
export IBMCLOUD_APIKEY=xxx
export CLUSTER_NAME=xxx
export OCP_VERSION=4.6.28_openshift

# CP4D configuration
export CPD_ENTITLEMENT_KEY=xxx

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

ansible-playbook playbooks/fullstack-roks.yml
```
