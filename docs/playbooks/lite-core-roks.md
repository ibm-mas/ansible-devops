# MAS Core Service on IBM Cloud ROKS

This master playbook will drive the following actions:

- [Provision & setup OCP on IBM Cloud](ocp.md#provision) (20-30 minutes)
- Install dependencies:
    - [Install MongoDb (Community Edition)](dependencies.md#install-mongodb-ce) (10 minutes)
    - [Install SLS](dependencies.md#install-sls) (10 minutes)
    - [Install UDS](dependencies.md#install-uds) (35 minutes)
- Install & configure MAS:
    - Generate MAS Workspace Configuration (1 minute)
    - [Configure Cloud Internet Services integration](mas.md#cloud-internet-services-integration) (Optional, 1 minute)
    - [Install & configure MAS](mas.md#install-mas) (15 minutes)

All timings are estimates, see the individual pages for each of these playbooks for more information.

## Preparation
Before you run the playbook you **must** prepare the entitlement license key file that will be used during the playbook run.

Copy the MAS license key file that you obtained from Rational License Key Server to `$MAS_CONFIG_DIR/entitlement.lic` (the file must have this exact name).  During the installation of SLS this license file will be automatically bootstrapped into the system.

!!! tip
    If you do not already have an entitlement file, create a random 12 character hex string and use this as the license ID when requesting your entitlement file from Rational License Key Server.


## Required environment variables

- `IBMCLOUD_APIKEY` The API key that will be used to create a new ROKS cluster in IBMCloud
- `CLUSTER_NAME` The name to assign to the new ROKS cluster
- `CLUSTER_TYPE` The cluster type. Should be set to `roks`
- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `MAS_ENTITLEMENT_KEY` Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)
- `MAS_CONFIG_DIR` Directory where generated config files will be saved (you may also provide pre-generated config files here)
- `SLS_LICENSE_ID` The license ID must match the license file available in `$MAS_CONFIG_DIR/entitlement.lic`
- `SLS_ENTITLEMENT_KEY` Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)
- `UDS_CONTACT_EMAIL` Defines the email for person to contact for UDS
- `UDS_CONTACT_FIRSTNAME` Defines the first name of the person to contact for UDS
- `UDS_CONTACT_LASTNAME` Defines the last name of the person to contact for UDS


## Optional environment variables
Refer to the role documentation for full details of all configuration options available in this playbook:

1. [ocp_provision](../roles/ocp_provision.md)
2. [ocp_setup_mas_deps](../roles/ocp_setup_mas_deps.md)
3. [mongodb](../roles/mongodb.md)
4. [sls_install](../roles/sls_install.md)
5. [gencfg_sls](../roles/gencfg_sls.md)
6. [uds_install](../roles/uds_install.md)
7. [gencfg_workspace](../roles/gencfg_workspace.md)
8. [suite_dns](../roles/suite_dns.md)
9. [suite_install](../roles/suite_install.md)
10. [suite_config](../roles/suite_config.md)
11. [suite_verify](../roles/suite_verify.md)


## Release build
The simplest configuration to deploy a release build of IBM Maximo Application Suite (core only) with dependencies is:
```bash
# IBM Cloud ROKS configuration
export IBMCLOUD_APIKEY=xxx
export CLUSTER_NAME=xxx
export CLUSTER_TYPE=roks

# MAS configuration
export MAS_INSTANCE_ID=$CLUSTER_NAME
export MAS_ENTITLEMENT_KEY=xxx

export MAS_CONFIG_DIR=~/masconfig

# SLS configuration
export SLS_LICENSE_ID=xxx
export SLS_ENTITLEMENT_KEY=xxx

# UDS configuration
export UDS_CONTACT_EMAIL=xxx@xxx.com
export UDS_CONTACT_FIRSTNAME=xxx
export UDS_CONTACT_LASTNAME=xxx

ansible-playbook playbooks/lite-core-roks.yml
```


## Pre-release build
The simplest configuration to deploy a pre-release build (only available to IBM employees) of IBM Maximo Application Suite (core only) with dependencies is:

```bash
# IBM Cloud ROKS configuration
export IBMCLOUD_APIKEY=xxx
export CLUSTER_NAME=xxx
export CLUSTER_TYPE=roks

# Allow development catalogs to be installed
export W3_USERNAME=xxx
export ARTIFACTORY_APIKEY=xxx

# MAS configuration
export MAS_INSTANCE_ID=$CLUSTER_NAME
export MAS_CATALOG_SOURCE=ibm-mas-operators
export MAS_CHANNEL=m2dev88

export MAS_ICR_CP=wiotp-docker-local.artifactory.swg-devops.com
export MAS_ICR_CPOPEN=wiotp-docker-local.artifactory.swg-devops.com
export MAS_ENTITLEMENT_USERNAME=$W3_USERNAME_LOWERCASE
export MAS_ENTITLEMENT_KEY=$ARTIFACTORY_APIKEY

export MAS_CONFIG_DIR=~/masconfig

# SLS configuration
export SLS_LICENSE_ID=xxx
export SLS_ENTITLEMENT_KEY=xxx

# UDS configuration
export UDS_CONTACT_EMAIL=xxx@xxx.com
export UDS_CONTACT_FIRSTNAME=xxx
export UDS_CONTACT_LASTNAME=xxx

ansible-playbook playbooks/lite-core-roks.yml
```

## Locating the playbook
After you have installed the ibm.mas_devops collection you will be able to find the playbook on your system as part of that installation.

For example, if you installed the collection to `/home/david/.ansible/collections/ansible_collections` the path to this playbook will be `/home/david/.ansible/collections/ansible_collections/ibm/mas_devops/playbooks/lite-core-roks.yml`

Alternatively:

- You can download the playbook from GitHub, but make sure to download the version of the playbook that corresponds to the version of the ibm.mas_devops Ansible collection that you have installed.
- You can close the repository from GitHub, but make sure to use the branch/tag corresponding to the version of the ibm.mas_devops Ansible colleciton that you have installed.
