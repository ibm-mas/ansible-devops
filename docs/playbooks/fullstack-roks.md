# Full Stack on IBM Cloud

This master playbook will drive the following playbooks in sequence:

- [Provision & setup OCP on IBM Cloud](ocp.md#provision) (20-30 minutes)
- Install dependencies:
    - [Install MongoDb (Community Edition)](dependencies.md#install-mongodb-ce) (10 minutes)
    - [Install Kafka (AMQ Streams)](dependencies.md#install-amq-streams) (10 minutes)
    - [Install SLS](dependencies.md#install-sls) (10 minutes)
    - [Install UDS](dependencies.md#install-uds) (35 minutes)
    - [Install NVIDIA](dependencies.md#install-nvidia) (7 minutes)
    - [Install Cloud Pak for Data Operator](cp4d.md#install-cp4d) (2 minutes)
    - [Install AppConnect](dependencies.md#install-appconnect) (?)
    - Install Cloud Pak for Data Services:
        - [Db2 Warehouse](cp4d.md#db2-install) (1 hour)
        - [Watson Studio](cp4d.md#watson-studio-install) with [Apache Spark](cp4d.md#watson-studio-install), [Watson Machine Learning](cp4d.md#watson-studio-install), & [Watson AI OpenScale](cp4d.md#watson-studio-install) (4-5 hours)
    - [Create Db2 Warehouse Cluster](cp4d.md#install-db2) (45 minutes)
    - [Additional Db2 configuration for Manage](mas.md#manage-db2-hack) (5 minutes)
- Install & configure MAS:
    - [Configure Cloud Internet Services integration](mas.md#cloud-internet-services-integration) (Optional, 1 minute)
    - Generate MAS Workspace Configuration (1 minute)
    - [Install & configure MAS](mas.md#install-mas) (15 minutes)
- Install applications:
    - [Install & configure Manage](mas.md#install-mas-application) (10 minute install + 2 hours configure)
    - [Install & configure IoT](mas.md#install-mas-application) (25 minute install + 5 minutes configure)
    - [Install & configure Monitor](mas.md#install-mas-application) (10 minute install + ? configure)
    - [Install & configure Predict](mas.md#install-mas-application) (10 minute install + 5 minutes configure)
    - [Install & configure Safety](mas.md#install-mas-application) (? minute install + ? configure)
    - [Install & configure Maximo Scheduler Optmization](mas.md#install-mas-application) (10 minute install + ? configure)
    - [Install & configure Health & Predict Utilities](mas.md#install-mas-application) (10 minute install + ? configure)

All timings are estimates, see the individual pages for each of these playbooks for more information.

!!! warning
    The install time for Cloud Pak for Data with all the services supported by MAS enabled is considerable.  Unfortunately this is out of our control, plan accordingly!

    Also note that Cloud Pak for Data requires approximately 40 PVCs.  You may need to contact IBM to increase the quota assigned to your IBM Cloud account if you see PVCs stuck in pending state and this error message: "Your order will exceed the maximum number of storage volumes allowed. Please contact Sales"


## Preparation
Before you run the playbook you need to configure a few things in your `MAS_CONFIG_DIR`:

### Copy your entitlement license key file
Copy the MAS license key file that you obtained from Rational License Key Server to a local path and set `SLS_LICENSE_FILE` to point to this file location. During the installation of SLS this license file will be automatically bootstrapped into the system.

!!! important
    Make sure you set `SLS_LICENSE_ID` to the correct value.  For full details on what configuration options are available with the SLS install refer to the [Install SLS](dependencies.md#install-sls) topic.


## Required environment variables
- `IBMCLOUD_APIKEY` The API key that will be used to create a new ROKS cluster in IBMCloud
- `CLUSTER_NAME` The name to assign to the new ROKS cluster
- `CLUSTER_TYPE` The cluster type. Should be set to `roks`
- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `MAS_ENTITLEMENT_KEY` Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)
- `MAS_CONFIG_DIR` Directory where generated config files will be saved (you may also provide pre-generated config files here)
- `SLS_LICENSE_ID` The license ID must match the license file available in `SLS_LICENSE_FILE`
- `SLS_LICENSE_FILE` The path to the location of the license file.
- `SLS_ENTITLEMENT_KEY` Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)
- `UDS_CONTACT_EMAIL` Defines the email for person to contact for BAS
- `UDS_CONTACT_FIRSTNAME` Defines the first name of the person to contact for BAS
- `UDS_CONTACT_LASTNAME` Defines the last name of the person to contact for BAS
- `CPD_ENTITLEMENT_KEY` Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/


## Optional environment variables
- `IBMCLOUD_RESOURCEGROUP` creates an IBM Cloud resource group to be used, if none are passed, `Default` resource group will be used.
- `OCP_VERSION` to override the default version of OCP to use (latest 4.6 release)
- `W3_USERNAME` to enable access to pre-release development builds of MAS
- `ARTIFACTORY_APIKEY`  to enable access to pre-release development builds of MAS
- `KAFKA_CLUSTER_SIZE` to override the default configuration used (small)
- `MONGODB_NAMESPACE` overrides the Kubernetes namespace where the MongoDb CE operator will be installed, this will default to `mongoce`
- `MAS_CATALOG_SOURCE` to override the use of the IBM Operator Catalog as the catalog source
- `MAS_CHANNEL` to override the use of the `8.x` channel
- `MAS_DOMAIN` to set a custom domain for the MAS installation
- `MAS_UPGRADE_STRATEGY` to override the use of Manual upgrade strategy.
- `MAS_ICR_CP` to override the value MAS uses for the IBM Entitled Registry (`cp.icr.io/cp`)
- `MAS_ICR_CPOPEN` to override the value MAS uses for the IBM Open Registry (`icr.io/cpopen`)
- `MAS_ENTITLEMENT_USERNAME` to override the username MAS uses to access content in the IBM Entitled Registry
- `CIS_CRN` to enable integration with IBM Cloud Internet Services (CIS) for DNS & certificate management
- `CIS_SUBDOMAIN` if you want to use a subdomain within your CIS instance
- `CPD_WSL_PROJECT_ID` to set a Watson Studio project id to be passed to HP Utilities application during its deployment and configuration. If not set, a new project will be created in Watson Studio automatically to configure HP Utilities application in the MAS instance created by this playbook
- `CPD_WSL_PROJECT_NAME` to set a Watson Studio project name, if not set a default project name will be used
- `CPD_WSL_PROJECT_DESCRIPTION` - to set a Watson Studio project description, if not set a default project description will be used

!!! tip
    `MAS_ICR_CP`, `MAS_ICR_CPOPEN`, & `MAS_ENTITLEMENT_USERNAME` are primarily used when working with pre-release builds in conjunction with `W3_USERNAME`, `ARTIFACTORY_APIKEY` and the `MAS_CATALOG_SOURCE` environment variables.

## Release build

```bash
# IBM Cloud ROKS configuration
export IBMCLOUD_APIKEY=xxx
export CLUSTER_NAME=xxx
export CLUSTER_TYPE=roks

# CP4D configuration
export CPD_ENTITLEMENT_KEY=xxx

# MAS configuration
export MAS_INSTANCE_ID=xxx
export MAS_ENTITLEMENT_KEY=xxx

export MAS_CONFIG_DIR=~/masconfig

# SLS configuration
export SLS_ENTITLEMENT_KEY=xxx
export SLS_LICENSE_ID=xxx

# BAS configuration
export UDS_CONTACT_EMAIL=xxx@xxx.com
export UDS_CONTACT_FIRSTNAME=xxx
export UDS_CONTACT_LASTNAME=xxx

ansible-playbook playbooks/fullstack-roks.yml
```

!!! note
    Lookup your entitlement keys from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)


## Pre-release build

```bash
# IBM Cloud ROKS configuration
export IBMCLOUD_APIKEY=xxx
export CLUSTER_NAME=xxx
export CLUSTER_TYPE=roks

# CP4D configuration
export CPD_ENTITLEMENT_KEY=xxx

# Allow development catalogs to be installed
export W3_USERNAME=xxx
export ARTIFACTORY_APIKEY=xxx

# MAS configuration
export MAS_CATALOG_SOURCE=ibm-mas-operators
export MAS_CHANNEL=m1dev87
export MAS_INSTANCE_ID=$CLUSTER_NAME

export MAS_ICR_CP=wiotp-docker-local.artifactory.swg-devops.com
export MAS_ICR_CPOPEN=wiotp-docker-local.artifactory.swg-devops.com
export MAS_ENTITLEMENT_USERNAME=$W3_USERNAME_LOWERCASE
export MAS_ENTITLEMENT_KEY=$ARTIFACTORY_APIKEY

export MAS_CONFIG_DIR=~/masconfig

# SLS configuration
export SLS_ENTITLEMENT_KEY=xxx
export SLS_LICENSE_ID=xxx

# BAS configuration
export UDS_CONTACT_EMAIL=xxx@xxx.com
export UDS_CONTACT_FIRSTNAME=xxx
export UDS_CONTACT_LASTNAME=xxx

ansible-playbook playbooks/fullstack-roks.yml
```
