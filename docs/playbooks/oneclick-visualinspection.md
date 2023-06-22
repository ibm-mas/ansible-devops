# Install Visual Inspection Application

## Prerequisites
You will need a RedHat OpenShift v4.8 cluster with IBM Maximo Application Suite Core v8.9. The [oneclick-core] (oneclick-core.md) playbook can be used to set this up.

## Overview
This playbook will add **Maximo Visual Inspection v8.7** to an existing IBM Maximo Application Suite Core installation.  MVI will be configured to accept automatic security updates and bug fixes, but not new feature releases.

This playbook can be ran against any OpenShift cluster regardless of its type; whether it's running in IBM Cloud, Azure, AWS, or your local datacenter.

- Install dependencies:
    - Install NVIDIA Graphical Processing Unit (GPU) (10 minutes)
- Install Maximo Visual Inspection application:
    - Install application (15 minutes)
    - Configure workspace (10 minutes)

All timings are estimates, see the individual pages for each of these playbooks for more information.  Use this sample playbook as a starting point for installing any MAS application, just customize the application install and configure stages at the end of the playbook.

## Required environment variables
- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `MAS_CONFIG_DIR` Directory where generated config files will be saved (you may also provide pre-generated config files here)
- `IBM_ENTITLEMENT_KEY` Your IBM Entitlement key to access the IBM Container Registry

## Usage
```bash
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=/home/david/masconfig
export IBM_ENTITLEMENT_KEY=xxx

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_add_visualinspection
```

!!! tip
    If you do not want to set up all the dependencies on your local system, you can run the install inside our docker image as well: `docker run -ti --pull always quay.io/ibmmas/cli`
