# MAS Core with Manage on IBM Cloud

This playbook will add Maximo Managed to an existing IBM Maximo Application Suite Core installation, along with all necessary dependencies.  This can be ran against any OCP cluster regardless of it's type, whether it's running in IBM Cloud, Azure, AWS, or your local datacenter.

- Install dependencies:
    - Install IBM Db2 Universal Operator (2 minutes)
    - Create Db2 Warehouse Instance (45 minutes)
    - Additional Db2 configuration for Manage (5 minutes)
- Install Maximo Manage application:
    - Install application (10 minutes)
    - Configure workspace (2 hours)

All timings are estimates, see the individual pages for each of these playbooks for more information.  Use this sample playbook as a starting point for installing any MAS application, just customize the application install and configure stages at the end of the playbook.

## Required environment variables
- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `MAS_CONFIG_DIR` Directory where generated config files will be saved (you may also provide pre-generated config files here)


!!! tip
    Manage requires the user to select one or more application components to enable in the workspace. By default the `base` component at the `latest` version will be installed if no `MAS_APPWS_COMPONENTS` is set. To customise the components that are enabled use the `MAS_APPWS_COMPONENTS` environment variable, for example to enable Manage(base) and Health set it to the following:

   `export MAS_APPWS_COMPONENTS="base=latest,health=latest"`

   To install Health as a Standalone with a specified version, set `MAS_APP_ID` to health and set `MAS_APPWS_COMPONENTS` to `health=x.x.x`. By default health standalone will be installed using `health=latest`


## Usage

```bash
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_manage
```
