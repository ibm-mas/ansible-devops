# OneClick Install for MAS Core

This playbook will install and configure IBM Maximo Application Suite Core along with all necessary dependencies.  This can be ran against any OCP cluster regardless of it's type, whether it's running in IBM Cloud, Azure, AWS, or your local datacenter.  It will take approximately 90 minutes to set up MAS core services and all of it's dependencies, at the end of the process you will be able to login to the MAS admin dashboard to install any applications that you wish to use, or you can use our other playbooks to automate the installation of those applications (including any additional dependencies)

## Playbook Content
1. [Install IBM Operator Catalogs](../roles/ibm_catalogs.md) (1 minute)
2. [Install IBM Common Services](../roles/common_services.md) (3 minutes)
3. [Install Certificate Manager Operator](../roles/cert_manager.md) (3 minutes)
4. [Install Service Binding Operator](../roles/sbo.md) (2 minutes)
5. [Configure Cluster Monitoring](../roles/cluster_monitoring.md) (1 minute)
6. [Install Mongodb Operator and Create a Cluster](../roles/mongodb.md) (10 minutes)
7. [Install and bootstrap IBM Suite License Service](../roles/sls.md) (10 minutes)
8. [Install IBM User Data Services](../roles/uds.md) (30 minutes)
9. [Generate a MAS Workspace Configuration](../roles/gencfg_workspace.md) (1 minute)
10. [Configure Cloud Internet Services Integration for Maximo Application Suite](../roles/suite_dns.md) (Optional, 1 minute)
11. [Install Maximo Application Suite Core Services](../roles/suite_install.md) (1 minute)
12. [Configure Maximo Application Suite](../roles/suite_config.md) (1 minute)
13. [Verify the Install and Configuration of Maximo Application Suite](../roles/suite_verify.md) (25 minutes)

All timings are estimates, see the individual pages for each of these roles for more information and full details of all configuration options available in this playbook.

## Preparation
Before you run the playbook you **must** prepare the entitlement license key file that will be used during the playbook run.

Copy the MAS license key file that you obtained from Rational License Key Server to a local path and set `SLS_LICENSE_FILE` to point to this location.  During the installation of SLS this license file will be automatically bootstrapped into the system.

!!! tip
    If you do not already have an entitlement file, create a random 12 character hex string and use this as the license ID when requesting your entitlement file from Rational License Key Service.


## Usage

### Required environment variables

- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `MAS_ENTITLEMENT_KEY` Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)
- `MAS_CONFIG_DIR` Directory where generated config files will be saved (you may also provide pre-generated config files here)
- `SLS_LICENSE_ID` The license ID must match the license file available in `SLS_LICENSE_FILE`
- `SLS_LICENSE_FILE` The path to the location of the license file.
- `SLS_ENTITLEMENT_KEY` Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)
- `UDS_CONTACT_EMAIL` Defines the email for person to contact for UDS
- `UDS_CONTACT_FIRSTNAME` Defines the first name of the person to contact for UDS
- `UDS_CONTACT_LASTNAME` Defines the last name of the person to contact for UDS


### Release build
The simplest configuration to deploy a release build of IBM Maximo Application Suite (core only) with dependencies is:
```bash
export MAS_INSTANCE_ID=inst1
export MAS_ENTITLEMENT_KEY=xxx
export MAS_CONFIG_DIR=~/masconfig
export SLS_LICENSE_ID=xxx
export SLS_LICENSE_FILE=/path/to/entitlement.lic
export SLS_ENTITLEMENT_KEY=x
export UDS_CONTACT_EMAIL=xxx@xxx.com
export UDS_CONTACT_FIRSTNAME=xxx
export UDS_CONTACT_LASTNAME=xxx

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_core
```

!!! tip
    If you do not want to set up all the dependencies on your local system, you can run the install inside our docker image as well: `docker run -ti quay.io/ibmmas/ansible-devops:10.0.4 bash`



### Pre-release build
To deploy a pre-release build of IBM Maximo Application Suite (core only) with dependencies a number of additional parameters are required, note that pre-release builds are only available to IBM employees:

```bash
export ARTIFACTORY_USERNAME=$W3_USERNAME_LOWERCASE
export ARTIFACTORY_APIKEY=xxx
export MAS_INSTANCE_ID=inst1
export MAS_CATALOG_SOURCE=ibm-mas-operators
export MAS_CHANNEL=m4dev88
export MAS_ICR_CP=wiotp-docker-local.artifactory.swg-devops.com
export MAS_ICR_CPOPEN=wiotp-docker-local.artifactory.swg-devops.com
export MAS_ENTITLEMENT_USERNAME=$W3_USERNAME_LOWERCASE
export MAS_ENTITLEMENT_KEY=$ARTIFACTORY_APIKEY
export MAS_CONFIG_DIR=~/masconfig
export SLS_LICENSE_ID=xxx
export SLS_LICENSE_FILE=/path/to/entitlement.lic
export SLS_ENTITLEMENT_KEY=xxx
export SLS_ENTITLEMENT_FILE=xxx
export UDS_CONTACT_EMAIL=xxx@xxx.com
export UDS_CONTACT_FIRSTNAME=xxx
export UDS_CONTACT_LASTNAME=xxx

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_core
```

!!! tip
    If you do not want to set up all the dependencies on your local system, you can run the install inside our docker image as well: `docker run -ti quay.io/ibmmas/ansible-devops:10.0.4 bash`

