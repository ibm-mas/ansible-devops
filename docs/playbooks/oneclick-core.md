# OneClick Install for MAS Core

This playbook will install and configure IBM Maximo Application Suite Core along with all necessary dependencies.  This can be ran against any OCP cluster regardless of it's type, whether it's running in IBM Cloud, Azure, AWS, or your local datacenter.

## Actions
- Install dependencies:
    - Install MongoDb (Community Edition) (10 minutes)
    - Install IBM SLS (10 minutes)
    - Install IBM UDS (35 minutes)
- Install & configure MAS:
    - Generate MAS Workspace Configuration (1 minute)
    - Configure Cloud Internet Services integration (Optional, 1 minute)
    - Install & configure MAS (15 minutes)

All timings are estimates, see the individual pages for each of these roles for more information.

## Preparation
Before you run the playbook you **must** prepare the entitlement license key file that will be used during the playbook run.

Copy the MAS license key file that you obtained from Rational License Key Server to a local path and set `SLS_LICENSE_FILE` to point to this location.  During the installation of SLS this license file will be automatically bootstrapped into the system.

!!! tip
    If you do not already have an entitlement file, create a random 12 character hex string and use this as the license ID when requesting your entitlement file from Rational License Key Server.


## Required environment variables

- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `MAS_ENTITLEMENT_KEY` Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)
- `MAS_CONFIG_DIR` Directory where generated config files will be saved (you may also provide pre-generated config files here)
- `SLS_LICENSE_ID` The license ID must match the license file available in `SLS_LICENSE_FILE`
- `SLS_LICENSE_FILE` The path to the location of the license file.
- `SLS_ENTITLEMENT_KEY` Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)
- `UDS_CONTACT_EMAIL` Defines the email for person to contact for UDS
- `UDS_CONTACT_FIRSTNAME` Defines the first name of the person to contact for UDS
- `UDS_CONTACT_LASTNAME` Defines the last name of the person to contact for UDS


## Optional environment variables
Refer to the role documentation for full details of all configuration options available in this playbook:
1. [ocp_setup_mas_deps](../roles/ocp_setup_mas_deps.md)
2. [ocp_setup_cluster_monitoring](../roles/ocp_setup_cluster_monitoring.md)
3. [mongodb](../roles/mongodb.md)
4. [sls](../roles/sls.md)
5. [uds_install](../roles/uds_install.md)
6. [gencfg_uds](../roles/gencfg_uds.md)
7. [gencfg_workspace](../roles/gencfg_workspace.md)
8. [suite_dns](../roles/suite_dns.md)
9. [suite_install](../roles/suite_install.md)
10. [suite_config](../roles/suite_config.md)
11. [suite_verify](../roles/suite_verify.md)


## Release build
The simplest configuration to deploy a release build of IBM Maximo Application Suite (core only) with dependencies is:
```bash
# MAS configuration
export MAS_INSTANCE_ID=inst1
export MAS_ENTITLEMENT_KEY=xxx

export MAS_CONFIG_DIR=~/masconfig

# SLS configuration
export SLS_LICENSE_ID=xxx
export SLS_LICENSE_FILE=/path/to/entitlement.lic
export SLS_ENTITLEMENT_KEY=xxx

# UDS configuration
export UDS_CONTACT_EMAIL=xxx@xxx.com
export UDS_CONTACT_FIRSTNAME=xxx
export UDS_CONTACT_LASTNAME=xxx

ansible-playbook ibm.mas_devops.oneclick_core
```


## Pre-release build
The simplest configuration to deploy a pre-release build (only available to IBM employees) of IBM Maximo Application Suite (core only) with dependencies is:

```bash
# Allow development catalogs to be installed
export W3_USERNAME=xxx
export ARTIFACTORY_APIKEY=xxx

# MAS configuration
export MAS_INSTANCE_ID=inst1
export MAS_CATALOG_SOURCE=ibm-mas-operators
export MAS_CHANNEL=m4dev88

export MAS_ICR_CP=wiotp-docker-local.artifactory.swg-devops.com
export MAS_ICR_CPOPEN=wiotp-docker-local.artifactory.swg-devops.com
export MAS_ENTITLEMENT_USERNAME=$W3_USERNAME_LOWERCASE
export MAS_ENTITLEMENT_KEY=$ARTIFACTORY_APIKEY

export MAS_CONFIG_DIR=~/masconfig

# SLS configuration
export SLS_LICENSE_ID=xxx
export SLS_LICENSE_FILE=/path/to/entitlement.lic
export SLS_ENTITLEMENT_KEY=xxx
export SLS_ENTITLEMENT_FILE=xxx

# UDS configuration
export UDS_CONTACT_EMAIL=xxx@xxx.com
export UDS_CONTACT_FIRSTNAME=xxx
export UDS_CONTACT_LASTNAME=xxx

ansible-playbook ibm.mas_devops.oneclick_core
```
