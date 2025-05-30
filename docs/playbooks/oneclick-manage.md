Install Manage Application
===============================================================================

This playbook will add Maximo Manage to an existing IBM Maximo Application Suite Instance.  Refer to the [oneclick-core](oneclick-core.md) playbook to set up the MAS Core Platform before running this playbook.  The playbook will also create an in-cluster Db2 instance using the IBM Db2 Universal Operator, which will be automatically set up as the system-level JDBC configuration in MAS.

Playbook Content
-------------------------------------------------------------------------------

1. [Install Cloud Pak for Data](../roles/cp4d.md) (optional, set `CPD_INSTALL_PLATFORM`)
2. [Add Cognos to CP4D](../roles/cp4d_service.md) (optional, set `CPD_INSTALL_COGNOS`)
3. [Add Watson Studio Local to CP4D](../roles/cp4d_service.md) (optional, set `CPD_INSTALL_WSL`)
4. [Create Db2 Instance using IBM Db2 Universal Operator](../roles/db2.md)
5. [Initialize Db2 Instance for Maximo Manage](../roles/suite_db2_setup_for_manage.md)
6. [Configure MAS to use the new Db2 Instance](../roles/suite_config.md)
7. [Configure MAS to use BYO database](../roles/gencfg_jdbc.md) (optional, set `CONFIGURE_EXTERNAL_DB`)
8. [Install Maximo Manage Application](../roles/suite_app_install.md)
9. [Configure Maximo Manage Workspace](../roles/suite_app_config.md)
10. [Configure Manage Attachments](../roles/suite_manage_attachments_config.md) (optional, set `CONFIGURE_MANAGE_ATTACHMENTS`)
11. [Configure Manage Building Information Models](../roles/suite_manage_bim_config.md) (optional, set `CONFIGURE_MANAGE_BIM`)

See the individual pages for each of these roles for more information and full details of all configuration options available in this playbook.


Required environment variables
-------------------------------------------------------------------------------
- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `MAS_CONFIG_DIR` Directory where generated config files will be saved (you may also provide pre-generated config files here)
- `IBM_ENTITLEMENT_KEY` Your IBM Entitlement key to access the IBM Container Registry

!!! tip
    Manage requires the user to select one or more application components to enable in the workspace. By default the `base` component at the `latest` version will be installed if no `MAS_APPWS_COMPONENTS` is set. To customise the components that are enabled use the `MAS_APPWS_COMPONENTS` environment variable, for example to enable Manage(base) and Health set it to the following:

   `export MAS_APPWS_COMPONENTS="base=latest,health=latest"`

   To disable Asset Investment Optimizer, optional feature of health, set `MAS_APP_SETTINGS_AIO_FLAG` to `false`. By default this flag is set to `true` . This feature is only avalaible on Manage with health as a addon or on Health as a Standalone install. This feature is disabled on MAS Core 9.1 and later.

   `export MAS_APP_SETTINGS_AIO_FLAG=false`


   **Note**:

   To install Manage Foundation only that is available on MAS Core 9.1 or later, export the following environment variable:

   `export IS_FULL_MANAGE=false`

   Also, the `MAS_APPWS_COMPONENTS` environment variable must be empty:

   `export MAS_APPWS_COMPONENTS=""`

Optional Cloud Pak for Data Installation
-------------------------------------------------------------------------------
Optional integration with Cloud Pak for Data is supported in Maximo Manage.  This can be enabled in the playbook as below:

```bash
export CPD_INSTALL_PLATFORM=true
export CPD_INSTALL_COGNOS=true
export CPD_INSTALL_WSL=true
export CPD_PRODUCT_VERSION=x.y.z
```




Usage
-------------------------------------------------------------------------------

!!! tip
    If you do not want to set up all the dependencies on your local system, you can run the install inside our docker image as well: `docker run -ti --pull always quay.io/ibmmas/cli`

### In-Cluster Db2
```bash
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig
export IBM_ENTITLEMENT_KEY=xxx

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_add_manage
```


### Bring Your Own Database
If you do not want to use the Db2 Universal Operator to provide the datbase for Maximo Manage then you can configure the playbook as below:

``` bash
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig
export IBM_ENTITLEMENT_KEY=xxx

export CONFIGURE_EXTERNAL_DB=true
export DB_INSTANCE_ID=maxdbxx
export MAS_JDBC_USER=maximo
export MAS_JDBC_PASSWORD=xxx
export MAS_JDBC_URL=xxx

export MAS_APP_SETTINGS_DB_SCHEMA=maximo
export MAS_APP_SETTINGS_TABLESPACE=maxdata
export MAS_APP_SETTINGS_INDEXSPACE=maxindex

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_add_manage
```

For full details of configuration options available refer to the [gencfg_jdbc](../roles/gencfg_jdbc.md) role documentation.


### Cloud Pak For Data Integration
To install CP4D with Cognos and/or Watson Studio Local optional dependencies:

```bash
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig
export IBM_ENTITLEMENT_KEY=xxx

export CPD_INSTALL_PLATFORM="true"
export CPD_INSTALL_COGNOS="true"
export CPD_INSTALL_WSL="true"
export CPD_PRODUCT_VERSION="4.6.6"

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_add_manage
```

For full details of configuration options available refer to the [cp4d](../roles/cp4d.md) & [cp4d_service](../roles/cp4d_service.md) role documentation.


### Health Standalone Install
To install Health as a Standalone application, set `MAS_APP_ID` and `MAS_APPWS_COMPONENTS` as below:

```bash
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig
export IBM_ENTITLEMENT_KEY=xxx

export MAS_APP_ID=health
export MAS_APPWS_COMPONENTS="health=latest"

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_add_manage
```

!!! warning
    Note that installing Health standalone will prevent the use of all other Manage components.  It is recommended to install Manage normally and just enable the Health component in the Manage application.
