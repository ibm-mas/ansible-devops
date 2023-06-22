# Install Monitor Application

## Prerequisites
You will need a RedHat OpenShift v4.8 cluster with IBM Maximo Application Suite Core v8.7 and Maximo IoT v8.4 already be installed, the [oneclick-core](oneclick-core.md) and [oneclick-iot](oneclick-iot.md)playbooks can be used to set this up.

## Overview
This playbook will add **Maximo Monitor v8.7** to an existing IBM Maximo Application Suite Core installation.  Monitor will be configured to accept automatic security updates and bug fixes, but not new feature releases.

This playbook can be ran against any OpenShift cluster regardless of its type; whether it's running in IBM Cloud, Azure, AWS, or your local datacenter.

- Install Maximo Monitor application:
    - Install application (60 minutes)
    - Configure workspace (5 minutes)

All timings are estimates, see the individual pages for each of these playbooks for more information.  Use this sample playbook as a starting point for installing any MAS application, just customize the application install and configure stages at the end of the playbook.


## Required environment variables
- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `MAS_CONFIG_DIR` Directory where generated config files will be saved (you may also provide pre-generated config files here)
- `IBM_ENTITLEMENT_KEY` Your IBM Entitlement key to access the IBM Container Registry

## Optional environment variables
- `MAS_APP_SETTINGS_MONITOR_DEPLOYMENT_SIZE` Define the Monitor deployment size, one of `dev`,
 `small` or `large`. Defaults to `dev`.

## Usage
```bash
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=/home/david/masconfig
export IBM_ENTITLEMENT_KEY=xxx

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_add_monitor
```

!!! tip
    If you do not want to set up all the dependencies on your local system, you can run the install inside our docker image as well: `docker run -ti --pull always quay.io/ibmmas/cli`

