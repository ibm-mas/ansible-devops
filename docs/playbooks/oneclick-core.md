# OneClick Install for MAS Core

This playbook will install and configure IBM Maximo Application Suite Core along with all necessary dependencies.  This can be ran against any OCP cluster regardless of its type, whether it's running in IBM Cloud, Azure, AWS, or your local datacenter.  It will take approximately 90 minutes to set up MAS core services and all of its dependencies, at the end of the process you will be able to login to the MAS admin dashboard to install any applications that you wish to use, or you can use our other playbooks to automate the installation of those applications (including any additional dependencies)

## Playbook Content
1. [Install IBM Operator Catalogs](../roles/ibm_catalogs.md) (1 minute)
2. [Install IBM Common Services](../roles/common_services.md) (3 minutes)
3. [Install Certificate Manager Operator](../roles/cert_manager.md) (3 minutes)
4. [Configure Cluster Monitoring](../roles/cluster_monitoring.md) (1 minute)
5. [Install Mongodb Operator and Create a Cluster](../roles/mongodb.md) (10 minutes)
6. [Install and bootstrap IBM Suite License Service](../roles/sls.md) (10 minutes)
7. [Install IBM User Data Services](../roles/uds.md) (30 minutes)
8. [Generate a MAS Workspace Configuration](../roles/gencfg_workspace.md) (1 minute)
9. [Configure Cloud Internet Services Integration for Maximo Application Suite](../roles/suite_dns.md) (Optional, 1 minute)
10. [Install Maximo Application Suite Core Services](../roles/suite_install.md) (1 minute)
11. [Configure Maximo Application Suite](../roles/suite_config.md) (1 minute)
12. [Verify the Install and Configuration of Maximo Application Suite](../roles/suite_verify.md) (25 minutes)

All timings are estimates, see the individual pages for each of these roles for more information and full details of all configuration options available in this playbook.


## Preparation

### 1. IBM Entitlement key
Access [Container Software Library](https://myibm.ibm.com/products-services/containerlibrary) using your IBMId to access your entitlement key

### 2. MAS License File
Access [IBM License Key Center](https://licensing.subscribenet.com/control/ibmr/login), on the **Get Keys** menu select **IBM AppPoint Suites**.  Select `IBM MAXIMO APPLICATION SUITE AppPOINT LIC` and on the next page fill in the information as below:

| Field            | Content                                           |
| ---------------- | ------------------------------------------------- |
| Number of Keys   | How many AppPoints to assign to the license file  |
| Host ID Type     | Set to **Ethernet Address**                       |
| Host ID          | Enter any 12 digit hexadecimal string             |
| Hostname         | Set to the hostname of your OCP instance          |
| Port             | Set to **27000**                                  |


The other values can be left at their defaults.  Finally, click **Generate** and download the license file to your home directory as `entitlement.lic`, set `SLS_LICENSE_FILE` to point to this location.


## Usage

### Required environment variables

- `IBM_ENTITLEMENT_KEY` Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)
- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `MAS_CONFIG_DIR` Directory where generated config files will be saved (you may also provide pre-generated config files here)
- `SLS_LICENSE_ID` The license ID must match the license file available in `SLS_LICENSE_FILE`
- `SLS_LICENSE_FILE` The path to the location of the license file.
- `UDS_CONTACT_EMAIL` Defines the email for person to contact for UDS
- `UDS_CONTACT_FIRSTNAME` Defines the first name of the person to contact for UDS
- `UDS_CONTACT_LASTNAME` Defines the last name of the person to contact for UDS

### Storage Class Configuraton
Storage class configuration is built into the collection and the playbook will auto-select the appropriate storage classes when it detects the presence of certain storage classes in your cluster (IBM Cloud Storage or OpenShift Container Storage).  If you are running the install on a cluster that does not have these storage classes then you will also must configure the following environment variables:

#### ReadWriteMany Access Mode
Usually fulfilled by block storage classes:

- `PROMETHEUS_ALERTMGR_STORAGE_CLASS`

#### ReadWriteOnce Access Mode
Usually fulfilled by file storage classes:

- `PROMETHEUS_STORAGE_CLASS`
- `PROMETHEUS_USERWORKLOAD_STORAGE_CLASS`
- `GRAFANA_INSTANCE_STORAGE_CLASS`
- `MONGODB_STORAGE_CLASS`
- `UDS_STORAGE_CLASS`


## Examples

### Release build
The simplest configuration to deploy a release build of IBM Maximo Application Suite (core only) with dependencies is:
```bash
export IBM_ENTITLEMENT_KEY=xxx

export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig

export SLS_LICENSE_ID=xxx
export SLS_LICENSE_FILE=/path/to/entitlement.lic

export UDS_CONTACT_EMAIL=xxx@xxx.com
export UDS_CONTACT_FIRSTNAME=xxx
export UDS_CONTACT_LASTNAME=xxx

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_core
```

!!! tip
    If you do not want to set up all the dependencies on your local system, you can run the install inside our docker image as well: `docker run -ti --pull always quay.io/ibmmas/cli`


### Pre-release build
To deploy a pre-release build of IBM Maximo Application Suite (core only) with dependencies a number of additional parameters are required, note that pre-release builds are only available to IBM employees:

```bash
export IBM_ENTITLEMENT_KEY=xxx

export ARTIFACTORY_USERNAME=$W3_USERNAME_LOWERCASE
export ARTIFACTORY_TOKEN=xxx
export MAS_ICR_CP=docker-na-public.artifactory.swg-devops.com/wiotp-docker-local
export MAS_ICR_CPOPEN=docker-na-public.artifactory.swg-devops.com/wiotp-docker-local
export MAS_ENTITLEMENT_USERNAME=$W3_USERNAME_LOWERCASE
export MAS_ENTITLEMENT_KEY=$ARTIFACTORY_TOKEN

export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig
export MAS_CATALOG_SOURCE=ibm-operator-catalog
export MAS_CHANNEL=rp1dev88

export SLS_LICENSE_ID=xxx
export SLS_LICENSE_FILE=/path/to/entitlement.lic

export UDS_CONTACT_EMAIL=xxx@xxx.com
export UDS_CONTACT_FIRSTNAME=xxx
export UDS_CONTACT_LASTNAME=xxx

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_core
```

!!! tip
    If you do not want to set up all the dependencies on your local system, you can run the install inside our docker image as well: `docker run -ti --pull always quay.io/ibmmas/cli`
