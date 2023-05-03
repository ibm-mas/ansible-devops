# Install Manage Application

## Prerequisites
You will need a RedHat OpenShift v4.8 cluster with IBM Maximo Application Suite Core v8.7 already be installed, the [oneclick-core](oneclick-core.md) playbook can be used to set this up.

## Overview
This playbook will add **Maximo Manage v8.3** to an existing IBM Maximo Application Suite Core installation.  It will also creatie an in-cluster Db2 instance, which will be automatically set up as the system-level JDBC configuration in MAS.  Manage will be configured to accept automatic security updates and bug fixes, but not new feature releases.

This playbook can be ran against any OCP cluster regardless of its type; whether it's running in IBM Cloud, Azure, AWS, or your local datacenter.

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
- `IBM_ENTITLEMENT_KEY` Your IBM Entitlement key to access the IBM Container Registry
- `MAS_APP_ID` Declare app_id as either `manage` or `health`

!!! tip
    Manage requires the user to select one or more application components to enable in the workspace. By default the `base` component at the `latest` version will be installed if no `MAS_APPWS_COMPONENTS` is set. To customise the components that are enabled use the `MAS_APPWS_COMPONENTS` environment variable, for example to enable Manage(base) and Health set it to the following:

   `export MAS_APPWS_COMPONENTS="base=latest,health=latest"`

   To enable Asset Investment Optimizer, optional feature of health. Set `MANAGE_AIO_FLAG` to `true`. By default this flag is set to `false` . This featue is only avalaible on Manage with health as a addon or on Health as a Standalone install.

   `export MANAGE_AIO_FLAG=true`

   To install Health as a Standalone with a specified version, set `MAS_APP_ID` to health and set `MAS_APPWS_COMPONENTS` to `health=x.x.x`. By default health standalone will be installed using `health=latest`

   `export MAS_APP_ID=health`
   `export MAS_APPWS_COMPONENTS="health=latest"`

## Optional environment variables
To connect to an external database (Oracle, SQL Server or DB2) set the following variables:

- `CONFIGURE_EXTERNAL_DB` Set it to true. By default, the value is false
- `DB_INSTANCE_ID` Your database instance ID  
- `MAS_JDBC_USER` Your database user name
- `MAS_JDBC_PASSWORD` Your database password
- `MAS_JDBC_URL` Your JDBC URL
- `MAS_APP_SETTINGS_DB2_SCHEMA`  Your schema name. By default, the value is maximo
- `MAS_APP_SETTINGS_TABLESPACE` Your tablespace name. By default, the value is maxdata
- `MAS_APP_SETTINGS_INDEXSPACE` Your indexspace name. By default, the value is maxindex
- `MAS_JDBC_CERT_LOCAL_FILE` Path to your database certificate file if the database is SSL enabled

If the database is not SSL enabled, set the SSL_ENABLED variable to false. By default, SSL_ENABLED is true.

`export SSL_ENABLED=false`  

To install CP4D and Cognos Analytics (Support for this integration starts in MAS 8.10):
- `CPD_INSTALL_PLATFORM` True/False - If you HAVE CP4D already installed in your cluster, then set it to "false"
- `CPD_INSTALL_COGNOS` True/False - If you HAVE Cognos Analytics already installed in your cluster, then set it to "false"
- `CPD_PRODUCT_VERSION` Cloud Pak for Data version installed in the cluster in 4.X format.
   
## Usage

```bash
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig
export IBM_ENTITLEMENT_KEY=xxx
export MAS_APP_ID=manage

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_add_manage
```

If you want to connect to an external database:

``` bash 
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig
export IBM_ENTITLEMENT_KEY=xxx
export MAS_APP_ID=manage

export CONFIGURE_EXTERNAL_DB=true
export DB_INSTANCE_ID=maxdbxx 
export MAS_JDBC_USER=maximo
export MAS_JDBC_PASSWORD=xxx
export MAS_JDBC_URL=xxx 
export MAS_APP_SETTINGS_DB2_SCHEMA=maximo
export MAS_APP_SETTINGS_TABLESPACE=maxdata
export MAS_APP_SETTINGS_INDEXSPACE=maxindex
export MAS_CONFIG_SCOPE=wsapp
export MAS_APPWS_BINDINGS_JDBC=workspace-application


Database URL examples:

DB2:
export MAS_JDBC_URL=jdbc:db2://dbserverxx:50000/maxdbxx
export MAS_JDBC_URL=jdbc:db2://dbserverxx:50000/maxdbxx:sslConnection=true  if SSL enabled

Oracle:
export MAS_JDBC_URL=jdbc:oracle:thin:@dbserverxx:1521:maximo

SQL Server:
export MAS_JDBC_URL="jdbc:sqlserver://;serverName=dbserverxx;portNumber=1433;databaseName=msdbxx;integratedSecurity=false;sendStringParametersAsUnicode=false;selectMethod=cursor;encrypt=false;trustServerCertificate=false;"
export MAS_JDBC_URL="jdbc:sqlserver://;serverName=dbserverxx;portNumber=1433;databaseName=msdbxx;integratedSecurity=false;sendStringParametersAsUnicode=false;selectMethod=cursor;encrypt=true;trustServerCertificate=true;" if SSL enabled

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_add_manage
```

If you want to install Cognos Analytics:

```bash
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig
export IBM_ENTITLEMENT_KEY=xxx
export MAS_APP_ID=manage

If CP4D is not installed:

export CPD_INSTALL_PLATFORM="true"
export CPD_INSTALL_COGNOS="true"
export CPD_PRODUCT_VERSION="4.6.3"

If CP4D is already installed:

export CPD_INSTALL_PLATFORM="false"
export CPD_INSTALL_COGNOS="true"
export CPD_ADMIN_USERNAME="admin"
export CPD_ADMIN_PASSWORD="xxx"
export CPD_URL="https://mycp4durl"
export CPD_PRODUCT_VERSION="4.6.3"


oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_add_manage
```



!!! tip
    If you do not want to set up all the dependencies on your local system, you can run the install inside our docker image as well: `docker run -ti --pull always quay.io/ibmmas/cli`

