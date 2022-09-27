# Install Predict Application

## Prerequisites
You will need a RedHat OpenShift v4.8 cluster with IBM Maximo Application Suite Core v8.7 already be installed, the [oneclick-core](oneclick-core.md) playbook can be used to set this up.

## Overview
This playbook will add **Predict v8.6** to an existing IBM Maximo Application Suite Core installation. It will also install CloudPak for Data + CP4D services.

This playbook can be ran against any OCP cluster regardless of it's type; whether it's running in IBM Cloud, Azure, AWS, or your local datacenter.

- Install dependencies:
    - Install CP4D (~1 1/2 hours)
    - Install Watson Studio (~3 hours)
    - Install Watson Machine Learning (~2 1/2 hours)
    - Install Spark (~30 minutes)
    - Install Openscale (~1 hour)
- Install Predict application:
    - Install application (~15 Minutes) 
    - Configure workspace (~30 Minutes) 

All timings are estimates, see the individual pages for each of these playbooks for more information.  Use this sample playbook as a starting point for installing any MAS application, just customize the application install and configure stages at the end of the playbook.

## Required environment variables
- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `MAS_CONFIG_DIR` Directory where generated config files will be saved (you may also provide pre-generated config files here)
- `MAS_ENTITLEMENT_KEY` Your IBM Entitlement key to access the IBM Container Registry

## These variables are requered only if you set CP4D_INSTALL_WSL to false in optional varibles, otherwise don't set it.
- `CPD_ADMIN_USERNAME` CP4D Username
- `CPD_ADMIN_PASSWORD` CP4D Password
- `CPD_URL` CP4D Base URL

## Optional environment variables
- `CP4D_INSTALL_PLATFORM` True/False - If you HAVE CP4D already installed in your cluster, then set it to "false"
- `CP4D_INSTALL_WSL` True/False - If you HAVE Watson Studio already installed in your cluster, then set it to "false"
- `CP4D_INSTALL_WML` True/False - If you HAVE Watson Machine Learning already installed in your cluster, then set it to "false"
- `CP4D_INSTALL_SPARK` True/False - If you HAVE Spark already installed in your cluster, then set it to "false"
- `CP4D_INSTALL_OPENSCALE` True/False - If you HAVE Openscale already installed in your cluster, then set it to "false"
- `CP4D_INSTALL_DISCOVERY` True/False - If you HAVE Watson Discovery already installed in your cluster, then set it to "false"



## Usage when you already HAVE CP4D installed

```bash
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig
export MAS_ENTITLEMENT_KEY=xxx

export CPD_ADMIN_USERNAME="admin"
export CPD_ADMIN_PASSWORD="xxx"
export CPD_URL="https://mycp4durl"

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_add_predict
```

## Usage when you DON'T HAVE CP4D installed
```bash
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig
export MAS_ENTITLEMENT_KEY=xxx
export CP4D_INSTALL_PLATFORM="true"
export CP4D_INSTALL_WSL="true"
export CP4D_INSTALL_WML="true"
export CP4D_INSTALL_SPARK="true"
export CP4D_INSTALL_OPENSCALE="true"
export CP4D_INSTALL_DISCOVERY="true"
oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_add_predict
```

!!! tip
    If you do not want to set up all the dependencies on your local system, you can run the install inside our docker image as well: `docker run -ti quay.io/ibmmas/ansible-devops:latest bash`
