# MAS Assist Service on DevIT Quickburn
(Deploy CP4D and watson discovery instance in this cluster)

This master playbook will drive the following playbooks in sequence:

- [Provision & setup Quickburn](ocp.md#quickburn) (25 minutes)
- [Prepare the OCS cluster ](../roles/ocp_setup_ocs.md) (10 minutes)
- Install MAS dependencies:
    - [Install MongoDb](dependencies.md#install-mongodb-ce) (10 minutes)
    - [Install SLS](dependencies.md#install-sls) (10 minutes)
- Install & configure MAS:
    - [Configure Cloud Internet Services integration](mas.md#cloud-internet-services-integration) (Optional, 1 minute)
    - Generate MAS Workspace Configuration (1 minute)
    - [Install & configure MAS](mas.md#install-mas) (15 minutes)
- [Configure and prepare object storage instance](../roles/cos_setup.md)
- Install and prepare discovery instance
    - [Install discovery Service](cp4d.md#install-services-discovery)
    - [Create Disocvery instance](cp4d.md#create-discovery-instance)
- Install Assist and Configure Assist Workspace
    - [Refer to Suite App Assist](../roles/suite_app_install.md) (20 Minutes)
    - [Refer to Suite App Configure](../roles/suite_app_configure.md)  (10 Minutes)
  

All timings are estimates, see the individual pages for each of these playbooks for more information.  Due to the size limtations of QuickBurn clusters a full MAS stack is not possible.

## Preparation
Before you run the playbook you need to configure a few things in your `MAS_CONFIG_DIR`:

### Prepare your entitlement license key file
First, set `SLS_LICENSE_ID` to the correct ID (a 12 character hex string) from your entitlement file, then set `SLS_LICENSE_FILE` to the location of the MAS license key file that you obtained from Rational License Key Server (thie will typically be called `entitlement.lic`).  During the installation of SLS this license file will be automatically bootstrapped into the system.

!!! tip
    If you do not already have an entitlement file, create a random 12 character hex string and use this as the license ID when requesting your entitlement file from Rational License Key Server.

## Required environment variables
- `FYRE_USERNAME`
- `FYRE_APIKEY`
- `FYRE_PRODUCT_ID`
- `CLUSTER_NAME` The name to assign to the new Quickburn cluster
- `CLUSTER_TYPE` The cluster type. Should be set to `quickburn`
- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `MAS_ENTITLEMENT_KEY` Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)
- `MAS_CONFIG_DIR` Directory where generated config files will be saved (you may also provide pre-generated config files here)
- `SLS_LICENSE_ID` The license ID must match the license file available in `SLS_LICENSE_FILE`
- `SLS_LICENSE_FILE` The path to the location of the license file.
- `SLS_ENTITLEMENT_KEY` Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)

## Optional environment variables
Refer to the role documentation for full details of all configuration options available in this playbook:

1. [ocp_provision](../roles/ocp_provision.md)
2. [ocp_setup_ocs](../roles/ocp_setup_ocs.md)
3. [ocp_setup_mas_deps](../roles/ocp_setup_mas_deps.md)
4. [mongodb](../roles/mongodb.md)
5. [sls_install](../roles/sls_install.md)
6. [gencfg_sls](../roles/gencfg_sls.md)
7. [gencfg_workspace](../roles/gencfg_workspace.md)
8. [suite_dns](../roles/suite_dns.md)
9. [suite_install](../roles/suite_install.md)
10. [suite_config](../roles/suite_config.md)
11. [suite_verify](../roles/suite_verify.md)
12. [cos_setup](../roles/cos_setup.md)
13. [cp4d_install](../roles/cos_setup.md)
14. [cp4d_install_servicesl](../roles/cp4d_install_services.md)
15. [cp4d_wds](../roles/cp4d_wds.md)
16. [suite_app_install](../roles/suite_app_install.md)
17. [suite_app_configure](../roles/suite_app_configure.md)

## Release build

```bash
# Fyre credentials
export FYRE_USERNAME=xxx
export FYRE_APIKEY=xxx
export FYRE_PRODUCT_ID=225
# Cluster configuration
export CLUSTER_NAME=xxx
export CLUSTER_TYPE=quickburn
export OCP_VERSION=4.8.35

# ocs version
export OCP_RELEASE=4.8

# SLS configuration
export SLS_ENTITLEMENT_KEY=xxx
export SLS_LICENSE_ID=xxx
export SLS_LICENSE_FILE=xxx

# MAS configuration
export MAS_INSTANCE_ID=xxx
export MAS_ENTITLEMENT_KEY=xxx

export MAS_CONFIG_DIR=~/masconfig

ansible-playbook playbooks/lite-assist-quickburn.yml
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
export CLUSTER_TYPE=quickburn
export OCP_VERSION=4.8.35

# ocs version
export OCP_RELEASE=4.8

# SLS configuration
export SLS_ENTITLEMENT_KEY=xxx
export SLS_LICENSE_ID=xxx
export SLS_LICENSE_FILE=xxx

# Allow development catalogs to be installed
export W3_USERNAME=xxx
export W3_USERNAME_LOWERCASE=xxx
export ARTIFACTORY_APIKEY=xxx

# MAS configuration
export MAS_CATALOG_SOURCE=ibm-mas-operators
export MAS_CHANNEL=8.5.0-pre.m2dev85
export MAS_INSTANCE_ID=xxx

export MAS_ICR_CP=wiotp-docker-local.artifactory.swg-devops.com
export MAS_ICR_CPOPEN=wiotp-docker-local.artifactory.swg-devops.com
export MAS_ENTITLEMENT_USERNAME=$W3_USERNAME_LOWERCASE
export MAS_ENTITLEMENT_KEY=$ARTIFACTORY_APIKEY

export MAS_CONFIG_DIR=~/masconfig

# Assist Configure
export MAS_APP_CHANNEL=m1dev88
export MAS_APP_CATALOG_SOURCE=ibm-mas-assist-operators


ansible-playbook playbooks/lite-assist-quickburn.yml
```
