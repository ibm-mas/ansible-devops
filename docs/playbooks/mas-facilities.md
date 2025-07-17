Install Real Estate and Facilities Application
===============================================================================

!!! important
    These playbooks are samples to demonstrate how to use the roles in this collection.

    They are **note intended for production use** as-is, they are a starting point for power users to aid in the development of their own Ansible playbooks using the roles in this collection.

    The recommended way to install MAS is to use the [MAS CLI](https://ibm-mas.github.io/cli/), which uses this Ansible Collection to deliver a complete managed lifecycle for your MAS instance.


Overview
-------------------------------------------------------------------------------
This playbook will add Maximo Real Estate and Facilities to an existing IBM Maximo Application Suite Instance.  Refer to the [mas_install_core](mas-core.md) playbook to set up the MAS Core Platform before running this playbook.
This playbook will create an in-cluster Db2 instance using the IBM Db2 Universal Operator, which will be automatically set up as the workspace-application level JDBC configuration in MAS.


Playbook Content
-------------------------------------------------------------------------------

1. [Create and initialize Db2 Instance for Maximo Real Estate and Facilities](../roles/suite_db2_setup_for_facilities.md)
2. [Configure MAS to use BYO database](../roles/gencfg_jdbc.md) (optional, set `CONFIGURE_EXTERNAL_DB`)
3. [Configure MAS to use the new Db2 Instance](../roles/suite_config.md)
4. [Install Maximo Real Estate and Facilities Application](../roles/suite_app_install.md)
5. [Configure Maximo Real Estate and Facilities Workspace](../roles/suite_app_config.md)

See the individual pages for each of these roles for more information and full details of all configuration options available in this playbook.


Required environment variables
-------------------------------------------------------------------------------
- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `MAS_CONFIG_DIR` Directory where generated config files will be saved (you may also provide pre-generated config files here)
- `IBM_ENTITLEMENT_KEY` Your IBM Entitlement key to access the IBM Container Registry


### In-Cluster Db2
```bash
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig
export IBM_ENTITLEMENT_KEY=xxx

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.mas_add_facilities
```


### Bring Your Own Database
If you do not want to use the Db2 Universal Operator to provide the database for MREF then you can configure the playbook as below:

``` bash
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig
export IBM_ENTITLEMENT_KEY=xxx

export CONFIGURE_EXTERNAL_DB=true
export DB_INSTANCE_ID=maxdbxx
export MAS_JDBC_USER=user1
export MAS_JDBC_PASSWORD=xxx
export MAS_JDBC_URL=xxx

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.mas_add_facilities
```

For full details of configuration options available refer to the [gencfg_jdbc](../roles/gencfg_jdbc.md) role documentation.


