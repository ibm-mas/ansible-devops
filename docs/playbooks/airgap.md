# Airgap Installation Playbooks

## Airgap Install

This playbook performs all necessary steps to allow an Airgap Installation. The following playbooks are invoked

- [Setup Simulated Airgap](airgap.md#setup-simulated-airgap) (5 Minutes):
- [Prepare CASE](airgap.md#prepare-case) (1 minute)
- [Setup Images](airgap.md#setup-images) (around 2 Hours)
- [Install CASE Operator](airgap.md#install-case-operator) (5 Minutes)

All timings are estimates, see the individual pages for each of these playbooks for more information.

### Required environment variables
- `CLUSTER_NAME`
- `FYRE_USERNAME`
- `FYRE_APIKEY`
- `CASE_NAME` - the name of the CASE bundle to be installed
- `CASE_BUNDLE_DIR` - the location of the CASE bundle to be installed
- `CASE_INV_NAME` - the name of the Setup inventory within the CASE bundle 
- `CP_ICR_ENTITLEMENT_KEY` to mirror images from ICR - lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)
- `MAS_ENTITLEMENT_KEY` creates entitlement secret, either `CP_ICR_ENTITLEMENT_KEY` or `ARTIFACTORY_APIKEY` 

### Optional environment variables
- `CASE_SOURCE` the URL of the case bundle archive - must be a .tgz format
- `W3_USERNAME` to enable access to pre-release images
- `ARTIFACTORY_APIKEY`  to enable access to pre-release images
- `DEV_AIRGAP_CHANGES` a directory containing modified case files with development changes 

### Release build

```bash
# Cluster configuration
export CLUSTER_NAME=xxx
# Fyre credentials
export FYRE_USERNAME=xxx
export FYRE_APIKEY=xxx
# MAS CASE details
export CASE_NAME=ibm-mas
export CASE_BUNDLE_DIR=XXX/ibm-mas-case/stable/ibm-mas-bundle/
export CASE_INV_NAME=ibmMasSetup
# MAS configuration
export CP_ICR_ENTITLEMENT_KEY=XXX
export MAS_ENTITLEMENT_KEY=$CP_ICR_ENTITLEMENT_KEY
# Enable Airgap Installation, without this the script will not change
export AIRGAP_INSTALL=true
export CASE_SOURCE=https://github.com/IBM/cloud-pak/blob/master/repo/case/ibm-mas/8.5.0/ibm-mas-8.5.0.tgz?raw=true

ansible-playbook playbooks/airgap-full-quickburn.yml
```

!!! note
    Lookup your entitlement keys from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)


### Pre-release build

```bash
# Cluster configuration
export CLUSTER_NAME=xxx
# Fyre credentials
export FYRE_USERNAME=xxx
export FYRE_APIKEY=xxx
# MAS CASE details
export CASE_NAME=ibm-mas
export CASE_BUNDLE_DIR=XXX/ibm-mas-case/stable/ibm-mas-bundle/
export CASE_INV_NAME=ibmMasSetup
# MAS configuration
export MAS_ICR_CP=wiotp-docker-local.artifactory.swg-devops.com
export MAS_ICR_CPOPEN=wiotp-docker-local.artifactory.swg-devops.com
export MAS_ENTITLEMENT_USERNAME=$W3_USERNAME_LOWERCASE
export MAS_ENTITLEMENT_KEY=$ARTIFACTORY_APIKEY
# Enable Airgap Installation, without this the script will not change
export AIRGAP_INSTALL=true

# Allow development builds to be tested
export DEV_AIRGAP_CHANGES=XXX/ibm-mas-case/dev-airgap-changes 

ansible-playbook playbooks/airgap-full-quickburn.yml
```

**!!! IMPORTANT**
The contents of the directory specified by $DEV_AIRGAP_CHANGES are copied over the $CASE_BUNDLE_DIR, so the sub-directory structure of the two should match. e.g.
```bash
$ tree $DEV_AIRGAP_CHANGES
/Users/paulstone/GitHub/ibm-mas-case/dev-airgap-changes
├── archive
│   ├── ibm-mas-8.5.0-pre.issue-7078a-test-images.csv
│   └── ibm-truststore-mgr-1.0.0-images.csv
└── case
    └── ibm-mas
        └── inventory
            └── ibmMasSetup
                └── files
                    └── image-map.yaml
```

## Setup Simulated Airgap
This playbook configures an OCP environment to simulate an airgapped cluster, allowing testing of airgap installations
This includes disabling network access to public image repositories and setting up the OCP Internal Registry in preparation for image mirroring.

### Required environment variables
- `CLUSTER_NAME`
- `FYRE_USERNAME` - to login to the cluster
- `FYRE_APIKEY` - to login to the cluster

### Example usage:

```bash
# Fyre credentials
export FYRE_USERNAME=xxx
export FYRE_APIKEY=xxx
# Cluster configuration
export CLUSTER_NAME=xxx

ansible-playbook playbooks/airgap/setup-simulated-airgap-cluster.yml
```

## Prepare CASE
This playbook prepares the specified CASE bundle for airgap installation. It can download the CASE bundle from an internet archive or take a case bundle in a local directory.

### Required environment variables
- `CASE_NAME` - the name of the CASE bundle to be installed
- `CASE_BUNDLE_DIR` - the location of the CASE bundle to be installed
- `CASE_INV_NAME` - the name of the Setup inventory within the CASE bundle 

### Optional environment variables
- `CASE_SOURCE` - the URL of the case bundle archive - must be a .tgz format

### Example usage:

```bash
# MAS CASE details
export CASE_NAME=ibm-mas
export CASE_BUNDLE_DIR=XXX/ibm-mas-case/stable/ibm-mas-bundle/
export CASE_INV_NAME=ibmMasSetup
export CASE_SOURCE=https://github.com/IBM/cloud-pak/blob/master/repo/case/ibm-mas/8.5.0/ibm-mas-8.5.0.tgz?raw=true

ansible-playbook playbooks/airgap/prepare-case.yml
```

## Setup Images
This playbook uses the mas CASE bundle to mirror container images to a mirror registry and configure the cluster to pull images from this mirror

### Required environment variables
- `CLUSTER_NAME`
- `FYRE_USERNAME` - to login to the cluster
- `FYRE_APIKEY` - to login to the cluster
- `CASE_NAME` - the name of the CASE bundle to be installed
- `CASE_BUNDLE_DIR` - the location of the CASE bundle to be installed
- `CASE_INV_NAME` - the name of the Setup inventory within the CASE bundle 
- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `CP_ICR_ENTITLEMENT_KEY` Provide your IBM entitlement key for mirroring container images

### Optional environment variables
- `DEV_AIRGAP_CHANGES` - a directory containing modified case files with development changes
The following registry variables are not required if the [Setup Simulated Airgap](airgap.md#setup-simulated-airgap) playbook is called first as this defines ansible variable with the registry configuration.
- `REGISTRY_PUBLIC_HOST` - the publicly accessible host name of the mirror registry
- `REGISTRY_FROM_CLUSTER` - the host name of the mirror registry as accessed from the cluster
- `REGISTRY_USERNAME` - credentials for the mirror registry
- `REGISTRY_PASSWORD` - credentials for the mirror registry

### Example usage: release build

```bash
# Fyre credentials
export FYRE_USERNAME=xxx
export FYRE_APIKEY=xxx
# Cluster configuration
export CLUSTER_NAME=xxx
export OCP_VERSION=4.6.16
# MAS CASE details
export CASE_NAME=ibm-mas
export CASE_BUNDLE_DIR=XXX/ibm-mas-case/stable/ibm-mas-bundle/
export CASE_INV_NAME=ibmMasSetup
# MAS configuration
export MAS_INSTANCE_ID=xxx
export CP_ICR_ENTITLEMENT_KEY=XXX

ansible-playbook playbooks/airgap/setup-airgap-images.yml
```

!!! note
    Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)


### Example usage: pre-release build

```bash
# Fyre credentials
export FYRE_USERNAME=xxx
export FYRE_APIKEY=xxx
# Cluster configuration
export CLUSTER_NAME=xxx
export OCP_VERSION=4.6.16
# MAS CASE details
export CASE_NAME=ibm-mas
export CASE_BUNDLE_DIR=XXX/ibm-mas-case/stable/ibm-mas-bundle/
export CASE_INV_NAME=ibmMasSetup
# MAS configuration
export MAS_INSTANCE_ID=xxx
export CP_ICR_ENTITLEMENT_KEY=XXX
# Development CASE changes
export DEV_AIRGAP_CHANGES=XXX/ibm-mas-case/dev-airgap-changes

ansible-playbook playbooks/airgap/setup-airgap-images.yml
```

**!!! IMPORTANT**
The contents of the directory specified by $DEV_AIRGAP_CHANGES are copied over the $CASE_BUNDLE_DIR, so the sub-directory structure of the two should match. e.g.
```bash
$ tree $DEV_AIRGAP_CHANGES
/Users/paulstone/GitHub/ibm-mas-case/dev-airgap-changes
├── archive
│   ├── ibm-mas-8.5.0-pre.issue-7078a-test-images.csv
│   └── ibm-truststore-mgr-1.0.0-images.csv
└── case
    └── ibm-mas
        └── inventory
            └── ibmMasSetup
                └── files
                    └── image-map.yaml
```


## Install CASE Operator
This playbook uses a CASE bundle and the `cloudctl` tool to run the airgap installation of the CASE operator. Note that this may or may not fully install the operator, depending on what is defined in the CASE. 

### Prereqs
- `cloudctl` tool must be installed

### Required environment variables
- `CLUSTER_NAME`
- `FYRE_USERNAME` - to login to the cluster
- `FYRE_APIKEY` - to login to the cluster
- `CASE_NAME` - the name of the CASE bundle to be installed
- `CASE_BUNDLE_DIR` - the location of the CASE bundle to be installed
- `CASE_INV_NAME` - the name of the Setup inventory within the CASE bundle 
- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install

### Optional environment variables
none

### Example usage: 

```bash
# Fyre credentials
export FYRE_USERNAME=xxx
export FYRE_APIKEY=xxx
# Cluster configuration
export CLUSTER_NAME=xxx
export OCP_VERSION=4.6.16
# MAS CASE details
export CASE_NAME=ibm-mas
export CASE_BUNDLE_DIR=XXX/ibm-mas-case/stable/ibm-mas-bundle/
export CASE_INV_NAME=ibmMasSetup
# MAS configuration
export MAS_INSTANCE_ID=xxx

ansible-playbook playbooks/airgap/install-case-operator.yml
```

