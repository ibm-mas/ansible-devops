# Install Predict Application

## Prerequisites

You will need a RedHat OpenShift cluster with IBM Maximo Application Suite Core v8.11 already be installed, the [mas_install_core](mas-core.md) playbook can be used to set this up.

## Overview

This playbook will add **Predict v8.9** to an existing IBM Maximo Application Suite Core installation. It will also install CloudPak for Data + CP4D services.

This playbook can be ran against any OCP cluster regardless of its type; whether it's running in IBM Cloud, Azure, AWS, or your local datacenter.

- Install dependencies:
  - Install CP4D (~1 1/2 hours)
  - Install Watson Studio (~3 hours)
  - Install Watson Machine Learning (~2 1/2 hours)
  - Install Spark (~30 minutes)
  - Install Openscale (~1 hour)
  - Install SPSS
- Install Predict application:
  - Install application (~15 Minutes)
  - Configure workspace (~30 Minutes)

All timings are estimates, see the individual pages for each of these playbooks for more information. Use this sample playbook as a starting point for installing any MAS application, just customize the application install and configure stages at the end of the playbook.

As of MAS 8.10, predict 8.8.0 will start to support SPSS Modeler, to install SPSS as part of CP4D set `CPD_INSTALL_SPSS=true` in your environment variables before running the playbook.


## Required environment variables

- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `MAS_CONFIG_DIR` Directory where generated config files will be saved (you may also provide pre-generated config files here)
- `IBM_ENTITLEMENT_KEY` Your IBM Entitlement key to access the IBM Container Registry
- `CPD_WSL_PROJECT_ID` - Ensure a Project ID Text box has a valid Watson Studio project ID. To obtain the project ID, Navigate to Cp4d/Watson Studio and create/Reuse a project. Open the project and look into the Browser URL, obtain the project ID from the URL and update Project ID settings.
- `CPD_WML_INSTANCE_ID` Set Default value to "openshift"
- `CPD_WML_URL` Set Default value to "https://internal-nginx-svc.ibm-cpd.svc:12443" . ibm-cpd in the URL corresponds to the project name (namespace) of cp4d installation
- `CPD_PRODUCT_VERSION` (Required if `WML_VERSION` is not informed) Cloud Pak for Data version installed in the cluster in 4.X format, it will be used to obtain the correct WML version to be installed
- `WML_VERSION` (Required if `CPD_PRODUCT_VERSION` is not informed) The wml_version for cp4d 4.0.x will be 4.0, if cp4d is 4.5.x , wml_version should change to 4.5, if cp4d is 4.6.x , wml_version should change to 4.6


**These variables are required only if you set CP4D_INSTALL_WSL to false in optional varibles:**

- `CPD_ADMIN_USERNAME` CP4D Username
- `CPD_ADMIN_PASSWORD` CP4D Password
- `CPD_ADMIN_URL` CP4D Base URL

!!! warning
    When not using this playbook to install Cloud Pak for Data it is important to ensure that your existing instance already has all the required services enabled.


## Optional environment variables

- `CPD_INSTALL_PLATFORM` True/False - If you HAVE CP4D already installed in your cluster you can skip this variable as `False` is set default
- `CPD_INSTALL_WSL` True/False - If you HAVE Watson Studio already installed in your cluster you can skip this variable as `False` is set default
- `CPD_INSTALL_WML` True/False - If you HAVE Watson Machine Learning already installed in your cluster you can skip this variable as `False` is set default
- `CPD_INSTALL_SPARK` True/False - If you HAVE Spark already installed in your cluster you can skip this variable as `False` is set default
- `CPD_INSTALL_OPENSCALE` True/False - If you HAVE Openscale already installed in your cluster you can skip this variable as `False` is set default
- `CPD_INSTALL_SPSS` True/False - If you HAVE SPSS Modeler already installed in your cluster you can skip this variable as `False` is set default


## Usage

!!! tip
    If you do not want to set up all the dependencies on your local system, you can run the playbook from inside the CLI container image: `docker run -ti --pull always quay.io/ibmmas/cli`

### Cloud Pak for Data is already installed

```bash
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig
export IBM_ENTITLEMENT_KEY=xxx

export MAS_APP_CHANNEL="8.9.x"

export CPD_PRODUCT_VERSION="4.6.4"
export CPD_WSL_PROJECT_ID="xxxx"
export CPD_WML_INSTANCE_ID="openshift"
export CPD_WML_URL="https://internal-nginx-svc.ibm-cpd.svc:12443"
export WML_VERSION="4.6"
export CPD_ADMIN_USERNAME="admin"
export CPD_ADMIN_PASSWORD="xxx"
export CPD_ADMIN_URL="https://mycp4durl"

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.mas_add_predict
```

### Cloud Pak for Data is not installed

```bash
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig
export IBM_ENTITLEMENT_KEY=xxx

export MAS_APP_CHANNEL="8.9.x"

export CPD_PRODUCT_VERSION="4.6.4"
export CPD_INSTALL_PLATFORM="true"
export CPD_INSTALL_WSL="true"
export CPD_INSTALL_WML="true"
export CPD_INSTALL_SPARK="true"
export CPD_INSTALL_OPENSCALE="true"
export CPD_INSTALL_DISCOVERY="true"
export CPD_INSTALL_SPSS="true"
export CPD_WSL_PROJECT_ID="xxxx"
export CPD_WML_INSTANCE_ID="openshift"
export CPD_WML_URL="https://internal-nginx-svc.ibm-cpd.svc:12443"
export WML_VERSION="4.6"
export CPD_ADMIN_USERNAME="admin"
export CPD_ADMIN_PASSWORD="xxx"
export CPD_ADMIN_URL="https://mycp4durl"

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.mas_add_predict
```
