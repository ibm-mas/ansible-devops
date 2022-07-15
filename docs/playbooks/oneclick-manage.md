# Install Manage Application

## Prerequisites
You will need a RedHat OpenShift v4.8 cluster with IBM Maximo Application Suite Core v8.7 already be installed, the [oneclick-core](oneclick-core.md) playbook can be used to set this up.

## Overview
This playbook will add **Maximo Manage v8.3** to an existing IBM Maximo Application Suite Core installation.  It will also creatie an in-cluster Db2 instance, which will be automatically set up as the system-level JDBC configuration in MAS.  Manage will be configured to accept automatic security updates and bug fixes, but not new feature releases.

This playbook can be ran against any OCP cluster regardless of it's type; whether it's running in IBM Cloud, Azure, AWS, or your local datacenter.

- Install dependencies:
    - Install IBM Db2 Universal Operator (2 minutes)
    - Create Db2 Warehouse Instance (45 minutes)
    - Additional Db2 configuration for Manage (5 minutes)
- Configure Maximo Application Suite:
    - Set up Db2 instance as the system-level JDBC datasource
- Install Maximo Manage application:
    - Install application (10 minutes)
    - Configure workspace (2 hours)

All timings are estimates, see the individual pages for each of these playbooks for more information.  Use this sample playbook as a starting point for installing any MAS application, just customize the application install and configure stages at the end of the playbook.

## Required environment variables
- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `MAS_CONFIG_DIR` Directory where generated config files will be saved (you may also provide pre-generated config files here)
- `MAS_ENTITLEMENT_KEY` Your IBM Entitlement key to access the IBM Container Registry
- `MAS_APP_ID` Declare app_id as either `manage` or `health`


!!! tip
    Manage requires the user to select one or more application components to enable in the workspace. By default the `base` component at the `latest` version will be installed if no `MAS_APPWS_COMPONENTS` is set. To customise the components that are enabled use the `MAS_APPWS_COMPONENTS` environment variable, for example to enable Manage(base) and Health set it to the following:

   `export MAS_APPWS_COMPONENTS="base=latest,health=latest"`

   To enable Asset Investment Optimizer, optional feature of health. Set `MANAGE_AIO_FLAG` to `true`. By default this flag is set to `false` . This featue is only avalaible on Manage with health as a addon or on Health as a Standalone install.

   `export MANAGE_AIO_FLAG=true`

   To install Health as a Standalone with a specified version, set `MAS_APP_ID` to health and set `MAS_APPWS_COMPONENTS` to `health=x.x.x`. By default health standalone will be installed using `health=latest`

   `export MAS_APP_ID=health`
   `export MAS_APPWS_COMPONENTS="health=latest"`

## Usage

```bash
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig
export MAS_ENTITLEMENT_KEY=xxx
export MAS_APP_ID=manage

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_add_manage
```

!!! tip
    If you do not want to set up all the dependencies on your local system, you can run the install inside our docker image as well: `docker run -ti quay.io/ibmmas/ansible-devops:latest bash`

