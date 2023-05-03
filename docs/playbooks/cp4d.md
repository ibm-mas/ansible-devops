# Install Cloud Pak for Data

## Prerequisites
You will need a RedHat OpenShift v4.10 cluster with IBM Maximo Application Suite Core v8.10 already installed, the [oneclick-core](oneclick-core.md) playbook can be used to set this up.

## Overview
This playbook will add **Cloud Pak for Data 4.x** to an existing cluster installation. It could also install additional CP4D services.

This playbook can be run against any OCP cluster regardless of its type; whether it's running in IBM Cloud, Azure, AWS, or your local datacenter.

- Install CP4D ControlPlane (~1 hour)
- Install CP4D Services (~30 Minutes - 1 hour for each service)

All timings are estimates, see the individual pages for each of these playbooks for more information.  Use this sample playbook as a starting point for installing any MAS application, just customize the application install and configure stages at the end of the playbook. 

## Required environment variables
- `MAS_CONFIG_DIR` Directory where generated config files will be saved (you may also provide pre-generated config files here)
- `CPD_ENTITLEMENT_KEY` Your IBM Entitlement key to access the IBM Container Registry
- `CPD_ENTITLEMENT_USERNAME` Your user name to access the IBM Container Registr

- `CPD_INSTALL_PLATFORM` True/False - If you HAVE CP4D already installed in your cluster, then set it to "false"
- `CPD_PRODUCT_VERSION` (Required) Cloud Pak for Data version installed in the cluster in 4.X format.

## These variables are required only if you set CP4D_INSTALL_WSL to false in optional varibles, otherwise don't set it.
- `CPD_ADMIN_USERNAME` CP4D Username
- `CPD_ADMIN_PASSWORD` CP4D Password
- `CPD_URL` CP4D Base URL

## Optional environment variables
- `CPD_INSTALL_COGNOS` True/False - Set to true to install Cognos Analytics
- `CPD_INSTALL_WSL` True/False - Set to true to install Watson Studio
- `CPD_INSTALL_WML` True/False - Set to true to install Watson Machine Learning
- `CPD_INSTALL_SPARK` True/False - Set to true to install Analytics Engine "Spark"
- `CPD_INSTALL_OPENSCALE` True/False - Set to true to install AI Openscale
- `CPD_INSTALL_DISCOVERY` True/False - Set to true to install Watson Discovery
- `CPD_INSTALL_SPSS` True/False - Set to true to install SPSS Modeler

## Usage when you already HAVE CP4D installed

```bash
export MAS_CONFIG_DIR=~/masconfig
export CPD_INSTALL_COGNOS="true"

export CPD_ENTITLEMENT_KEY=xxx
export CPD_ENTITLEMENT_USERNAME=xxx

export CPD_ADMIN_USERNAME="admin"
export CPD_ADMIN_PASSWORD="xxx"
export CPD_URL="https://mycp4durl"
export CPD_PRODUCT_VERSION="4.6.3"


oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.cp4d
```

## Usage when you DON'T HAVE CP4D installed
```bash
export MAS_CONFIG_DIR=~/masconfig

export CPD_ENTITLEMENT_KEY=xxx
export CPD_ENTITLEMENT_USERNAME=xxx

export CPD_INSTALL_PLATFORM="true"
export CPD_PRODUCT_VERSION="4.6.3"

## To install additional CP4D services, add one or many of these environment variables:
export CPD_INSTALL_COGNOS="true"
export CPD_INSTALL_WSL="true"
export CPD_INSTALL_WML="true"
export CPD_INSTALL_SPARK="true"
export CPD_INSTALL_OPENSCALE="true"
export CPD_INSTALL_DISCOVERY="true"
export CPD_INSTALL_SPSS="true"

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.cp4d
```

!!! tip
    If you do not want to set up all the dependencies on your local system, you can run the install inside our docker image as well: `docker run -ti --pull always quay.io/ibmmas/cli`
