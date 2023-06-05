# Install Predict Application

## Prerequisites
You will need a RedHat OpenShift v4.8 cluster with IBM Maximo Application Suite Core v8.7 already be installed, the [oneclick-core](oneclick-core.md) playbook can be used to set this up.

## Overview
This playbook will add **Predict v8.6** to an existing IBM Maximo Application Suite Core installation. It will also install CloudPak for Data + CP4D services.

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

All timings are estimates, see the individual pages for each of these playbooks for more information.  Use this sample playbook as a starting point for installing any MAS application, just customize the application install and configure stages at the end of the playbook. 

As of MAS 8.10, predict 8.8.0 will start to support SPSS Modeler, to install SPSS as part of CP4d please enable the below flag 
`export CPD_INSTALL_SPSS=true`
## Required environment variables
- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `MAS_CONFIG_DIR` Directory where generated config files will be saved (you may also provide pre-generated config files here)
- `IBM_ENTITLEMENT_KEY` Your IBM Entitlement key to access the IBM Container Registry
- `WML_INSTANCE_ID` Set Default value to "openshift"
- `WML_URL` Set Default value to "https://internal-nginx-svc.ibm-cpd.svc:12443" . ibm-cpd in the URL corresponds to the project name (namespace) of cp4d installation
- `CPD_PRODUCT_VERSION` (Required if `WML_VERSION` is not informed) Cloud Pak for Data version installed in the cluster in 4.X format, it will be used to obtain the correct WML version to be installed
- `WML_VERSION` (Required if `CPD_PRODUCT_VERSION` is not informed) The wml_version for cp4d 4.0.x will be 4.0, if cp4d is 4.5.x , wml_version should change to 4.5
- `PREDICT_DEPLOYMENT_SIZE` Controls the workload size of predict containers. Avaliable options are `developer`, `small`, `medium`. 'small' is the choosen one set by default.

    | Deployment_size        | Replica |
    | ---------------------- | :--: |
    | developer              |  1 |
    | small                  |  2 |
    | medium                 |  3 |

## These variables are required only if you set CP4D_INSTALL_WSL to false in optional varibles, otherwise don't set it.
- `CPD_ADMIN_USERNAME` CP4D Username
- `CPD_ADMIN_PASSWORD` CP4D Password
- `CPD_URL` CP4D Base URL

!!! warning
    Be sure that your current instance of CP4D has all the dependencies required by Predict:
    - Install CP4D
    - Install Watson Studio
    - Install Watson Machine Learning
    - Install Spark
    - Install Openscale

## Optional environment variables
- `CPD_INSTALL_PLATFORM` True/False - If you HAVE CP4D already installed in your cluster, then set it to "false"
- `CPD_INSTALL_WSL` True/False - If you HAVE Watson Studio already installed in your cluster, then set it to "false"
- `CPD_INSTALL_WML` True/False - If you HAVE Watson Machine Learning already installed in your cluster, then set it to "false"
- `CPD_INSTALL_SPARK` True/False - If you HAVE Spark already installed in your cluster, then set it to "false"
- `CPD_INSTALL_OPENSCALE` True/False - If you HAVE Openscale already installed in your cluster, then set it to "false"
- `CPD_INSTALL_SPSS` True/False - If you HAVE SPSS Modeler already installed in your cluster, then set it to "false"
- `CPD_WSL_PROJECT_ID` - Ensure a Project ID Text box has a valid Watson Studio project ID. To obtain the project ID, Navigate to Cp4d/Watson Studio and create/Reuse a project. Open the project and look into the Browser URL, obtain the project ID from the URL and update Project ID settings.


## Usage when you already HAVE CP4D installed

```bash
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig
export IBM_ENTITLEMENT_KEY=xxx

export CPD_ADMIN_USERNAME="admin"
export CPD_ADMIN_PASSWORD="xxx"
export CPD_URL="https://mycp4durl"
export WML_INSTANCE_ID="openshift"
export WML_URL="https://internal-nginx-svc.ibm-cpd.svc:12443"
export CPD_PRODUCT_VERSION="4.5.0"
export PREDICT_DEPLOYMENT_SIZE="small"


oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_add_predict
```

## Usage when you DON'T HAVE CP4D installed
```bash
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig
export IBM_ENTITLEMENT_KEY=xxx

export CPD_INSTALL_PLATFORM="true"
export CPD_INSTALL_WSL="true"
export CPD_INSTALL_WML="true"
export CPD_INSTALL_SPARK="true"
export CPD_INSTALL_OPENSCALE="true"
export CPD_INSTALL_SPSS="true"
export WML_INSTANCE_ID="openshift"
export WML_URL="https://internal-nginx-svc.ibm-cpd.svc:12443"
export CPD_PRODUCT_VERSION="4.5.0"
export PREDICT_DEPLOYMENT_SIZE="small"

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_add_predict
```

!!! tip
    If you do not want to set up all the dependencies on your local system, you can run the install inside our docker image as well: `docker run -ti --pull always quay.io/ibmmas/cli`
