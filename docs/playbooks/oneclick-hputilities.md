# Install Health & Predict Utilities Application

## Prerequisites
You will need a RedHat OpenShift cluster with IBM Maximo Application Suite Core. already be installed, the [oneclick-core](oneclick-core.md) playbook can be used to set this up.

## Overview
This playbook will add **Health & Predict Utilities** to an existing IBM Maximo Application Suite Core installation. Optionally, it can also install HPU dependencies (CloudPak for Data + Watson Studio + AppConnect).

This playbook can be ran against any OCP cluster regardless of it's type whether it's running in IBM Cloud, Azure, AWS, or your local datacenter.

- Install dependencies:
    - Install CP4D (~1 1/2 hours)
    - Install Watson Studio (~3 hours)
    - Install AppConnect (30 minutes)
- Install Health & Predict Utilities application:
    - Install application (~15 Minutes)
    - Configure workspace (~30 Minutes)

All timings are estimates, see the individual pages for each of these playbooks for more information.  Use this sample playbook as a starting point for installing any MAS application, just customize the application install and configure stages at the end of the playbook. 

## Required environment variables
- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `MAS_WORKSPACE_ID` Declare the workspace ID for the MAS install
- `MAS_CONFIG_DIR` Directory where generated config files will be saved (you may also provide pre-generated config files here)
- `IBM_ENTITLEMENT_KEY` Your IBM Entitlement key to access the IBM Container Registry
- `CPD_PRODUCT_VERSION` Cloud Pak for Data version installed in the cluster in 4.X format, it will be used to obtain the correct Watson Studio version to be installed

## These variables are required only if you set CP4D_INSTALL_WSL to false in optional variables, otherwise don't set it (if you have an existing CPD installation to use).
- `CPD_ADMIN_USERNAME` CP4D Username
- `CPD_ADMIN_PASSWORD` CP4D Password
- `CPD_URL` CP4D Base URL

!!! warning
    Be sure that your current instance of CP4D has all the dependencies required by Health & Predict Utilities:
    - Install CP4D
    - Install Watson Studio

## Optional environment variables
- `CPD_INSTALL_PLATFORM` True/False - If you HAVE CP4D already installed in your cluster, then set it to "false"
- `CPD_INSTALL_WSL` True/False - If you HAVE Watson Studio already installed in your cluster, then set it to "false"
- `CPD_WSL_PROJECT_NAME` - Watson Studio project name, if not provided, a new project will be created while configuring Watson Studio for HPU.
- `INSTALL_APPCONNECT` - Optionally install AppConnect. Default to `False`.

## Usage when you already HAVE CP4D installed

```bash
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig
export IBM_ENTITLEMENT_KEY=xxx

export CPD_ADMIN_USERNAME="admin"
export CPD_ADMIN_PASSWORD="xxx"
export CPD_URL="https://mycp4durl"
export CPD_PRODUCT_VERSION="4.6.3"
export CPD_WSL_PROJECT_NAME="my-wsl-project"

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_add_hputilities
```

## Usage when you DON'T HAVE CP4D installed
```bash
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig
export IBM_ENTITLEMENT_KEY=xxx

export CPD_INSTALL_PLATFORM="true"
export CPD_INSTALL_WSL="true"
export CPD_PRODUCT_VERSION="4.6.3"

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_add_hputilities
```

!!! tip
    If you do not want to set up all the dependencies on your local system, you can run the install inside our docker image as well: `docker run -ti --pull always quay.io/ibmmas/cli`
