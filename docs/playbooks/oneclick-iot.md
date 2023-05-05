# Install IoT Application

## Prerequisites
You will need a RedHat OpenShift v4.8 cluster with IBM Maximo Application Suite Core v8.7 already be installed, the [oneclick-core](oneclick-core.md) playbook can be used to set this up.

## Overview
This playbook will add **Maximo IoT v8.4** to an existing IBM Maximo Application Suite Core installation.  It will also creatie an in-cluster Db2 instance and Kafka cluster, both of which will be automatically set up as system-level configurations in MAS.  IoT will be configured to accept automatic security updates and bug fixes, but not new feature releases.

This playbook can be ran against any OpenShift cluster regardless of its type; whether it's running in IBM Cloud, Azure, AWS, or your local datacenter.

- Install dependencies:
    - Install IBM Db2 Universal Operator (2 minutes)
    - Create Db2 Warehouse Instance (45 minutes)
    - Install RedHat AMQ Streams Operator (2 minutes)
    - Create Apache Kafka Cluster (15 minutes)
- Configure Maximo Application Suite:
    - Set up Db2 instance as the system-level JDBC datasource
    - Set up Kafka cluster as the system-level Kafka
- Install Maximo IoT application:
    - Install application (90 minutes)
    - Configure workspace (5 minutes)

All timings are estimates, see the individual pages for each of these playbooks for more information.  Use this sample playbook as a starting point for installing any MAS application, just customize the application install and configure stages at the end of the playbook.


### Storage Class Configuraton
A persistent volume storage class is required for the FPL component. Storage class configuration is built into the collection and the playbook will auto-select the appropriate storage classes when it detects the presence of certain storage classes in your cluster (IBM Cloud Storage or OpenShift Container Storage).  If you are running the install on a cluster that does not have these storage classes then you will also must configure the following environment variables:

#### ReadWriteOnce Access Mode
Usually fulfilled by block storage classes:

- `MAS_APP_SETTINGS_IOT_FPL_PVC_STORAGE_CLASS`

## Required environment variables
- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `MAS_CONFIG_DIR` Directory where generated config files will be saved (you may also provide pre-generated config files here)
- `IBM_ENTITLEMENT_KEY` Your IBM Entitlement key to access the IBM Container Registry

## Optional environment variables
- `MAS_APP_SETTINGS_IOT_DEPLOYMENT_SIZE` Define the IoT deployment size, one of `dev`,
 `small` or `large`. Defaults to `small`.

## Usage
```bash
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=/home/david/masconfig
export IBM_ENTITLEMENT_KEY=xxx

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_add_iot
```

!!! tip
    If you do not want to set up all the dependencies on your local system, you can run the install inside our docker image as well: `docker run -ti --pull always quay.io/ibmmas/cli`

