# Install AI Broker Application

## Prerequisites

You will need a RedHat OpenShift v4.14 or above.

### Dependencies:

* IBM Suite License Service installed on OCP cluster or external instance or details from external instance
* IBM Data Reporter Operator installed on OCP cluster or external instance or details from external instance
* Object Storage
  + Minio (installed on the same cluster what aibroker) or external instance or details from external instance
  + AWS S3 (if customer use AWS S3 bucket bucket) buckets needs to have unique names 
* MariaDB database (installed in cluster where aibroker instance) or external instance or details from external instance

## Overview

This playbook will add **AI Broker v9.1.x** to OCP cluster.

This playbook can be ran against any OCP cluster regardless of its type; whether it's running in IBM Cloud, Azure, AWS, or your local datacenter.

* Install dependencies:
  + IBM Suite License Service (~10 Minutes) **optional**
  + IBM Data Reporter Operator (~10 Minutes) **optional**
  + Install MariaDB (~5 minutes) **optional**
  + Install Minio (~5 minutes) **optional**
* Install AI broker application (using playbook):
  + Install application (~20 Minutes)
  + Configure AI Broker (kmodels, tenant, etc) (~20 Minutes)

All timings are estimates, see the individual pages for each of these playbooks for more information. Use this sample playbook as a starting point for installing application, just customize the application install and configure stages at the end of the playbook.

## Storage providers

**Notice !!!**

AI Broker supports **AWS** and **Minio** storage providers.

## Required environment variables

* `MAS_INSTANCE_ID` Declare the instance ID for the AI Broker install
* `MAS_ENTITLEMENT_KEY` Your IBM Entitlement key to access the IBM Container Registry
* `MAS_ENTITLEMENT_USERNAME` Your IBM Entitlement user to access the IBM Container Registry
* `MAS_APP_CHANNEL` Aibroker application channel
* `MAS_AIBROKER_STORAGE_ACCESSKEY` Your strage provider access key
* `MAS_AIBROKER_STORAGE_SECRETKEY` Your storage provider secret key
* `MAS_AIBROKER_STORAGE_HOST` Your storage provider host
* `MAS_AIBROKER_STORAGE_REGION` Your storage provider region - only when use AWS S3 instance
* `MAS_AIBROKER_STORAGE_PROVIDER` Your storage provider name
* `MAS_AIBROKER_STORAGE_SSL` Your storage ssl (true/false)
* `MAS_AIBROKER_STORAGE_PIPELINES_BUCKET` Your piplines bucket
* `MAS_AIBROKER_STORAGE_TENANTS_BUCKET` Your tenants bucket
* `MAS_AIBROKER_STORAGE_TEMPLATES_BUCKET` Your templates bucket
* `MAS_AIBROKER_WATSONXAI_APIKEY` You WatsonX AI api key
* `MAS_AIBROKER_WATSONXAI_URL` You WatsonX AI url
* `MAS_AIBROKER_WATSONXAI_PROJECT_ID` You WatsonX projedt Id
* `WX_FULL` Indicates on-premises Watsonx installation (set true if you have on-prem installation)
* `MAS_AIBROKER_WATSONX_INSTANCE_ID` Your Watsonx Instance Id
* `MAS_AIBROKER_WATSONX_VERSION` Your Watsonx Version
* `MAS_AIBROKER_WATSONX_USERNAME` Your Watsonx Username
* `MAS_AIBROKER_DB_HOST` Your database instance host
* `MAS_AIBROKER_DB_PORT` Your database instance port
* `MAS_AIBROKER_DB_USER` Your database instance user
* `MAS_AIBROKER_DB_DATABASE` Your database instance datbase name
* `MAS_AIBROKER_DB_SECRET_NAME` Your database instance secret name
* `MAS_AIBROKER_DB_SECRET_VALUE` Your database instance password

## Required environment variables when AI Broker deployed on SAAS

* `MAS_AIBROKER_SAAS` specify if saas deployment (default value is: false) 
* `MAS_CONFIG_DIR` specify config location, mandatory when `MAS_AIBROKER_SAAS=true`
* `MAS_AIBROKER_DOMAIN` specify cluster domain, mandatory when `MAS_AIBROKER_SAAS=true`
* `MAS_AIBROKER_SLS_URL` specify SLS url, mandatory when `MAS_AIBROKER_SAAS=true`
* `MAS_AIBROKER_SLS_REGISTRATION_KEY` specify sls registration key, mandatory when `MAS_AIBROKER_SAAS=true`, to get value: look in `ibm-sls` namespace, pod `sls-api-licensing-xxx` and in `Environment` tab check `REGISTRATION_KEY` value
* `MAS_AIBROKER_DRO_URL` specify DRO url, mandatory when `MAS_AIBROKER_SAAS=true`
* `MAS_AIBROKER_DRO_TOKEN` specify DRO token, mandatory when `MAS_AIBROKER_SAAS=true` to get value: go to `mas-{{ instance_id }}-core` and look in secret `dro-apikey`
* `DB2_INSTANCE_NAME` specify DB2 instance name (default value is: aibroker), mandatory when `MAS_AIBROKER_SAAS=true`
* `IBM_ENTITLEMENT_KEY` specify IBM Entitlement key, mandatory when `MAS_AIBROKER_SAAS=true`

## Optional environment variables

* `MAS_ICR_CP` Provide custom registry for AI Broker applications
* `MAS_ICR_CPOPEN` Provide custom registry for AI Broker operator
* `MAS_CATALOG_VERSION` Your custom AI broker catalog version
* `ARTIFACTORY_USERNAME` Your artifactory user name to access - this is needed if user deploy from custom registry for example `docker-na-public.artifactory.swg-devops.com`
* `ARTIFACTORY_TOKEN` Your artifactory token for user to access - this is needed if user deploy from custom registry for example `docker-na-public.artifactory.swg-devops.com`
* `MAS_AIBROKER_TENANT_ACTION` Whether to install or remove tenant (default value is: install)
* `MAS_AIBROKER_APIKEY_ACTION` Whether to install or remove or update apikey (default value is: install)
* `MAS_AIBROKER_WATSONX_ACTION` Whether to install or remove watsonx secret (default value is: install)
* `MAS_AIBROKER_S3_ACTION` Whether to install or remove s3 (default value is: install)
* `INSTALL_DB2` Whether to install DB2 (default value is: false)
* `INSTALL_MINIO` Whether to install minio (default value is: false)
* `INSTALL_MARIADB` Whether to install mariadb (default value is: false)
* `INSTALL_SLS` Whether to install IBM Suite License Service (default value is: false)
* `INSTALL_DRO` Whether to install IBM Data Reporter Operator (default value is: false)
* `MAS_AIBROKER_DB2_USERNAME` The username to use for authentication with the database
* `MAS_AIBROKER_DB2_PASSWORD` The password to use for authentication with the database
* `MAS_AIBROKER_DB2_JDBC_URL` The JDBC URL specifying the host and port of the database, typically in the format jdbc:db2://host:port/
* `MAS_AIBROKER_DB2_SSL_ENABLED` A flag indicating whether to enable SSL encryption for the database connection (default value is: true)
* `USE_AWS_DB2` A flag indicating whether to use an AWS-hosted DB2 instance (default value is: false)
* `DS_PIPELINES_ENABLED` from Opendata hub version 2.30.0 user can skip and not install data science pipelines (default value is: false)
* `MAS_AIBROKER_CLUSTER_DOMAIN` Provide custom domain (default value is: empty)
* `MAS_AIBROKER_IS_EXTERNAL_ROUTE` A flag indicating to enable external route (default value is: false)
 

## Usage

### AI broker deployment steps

#### Notice: For S3 manage please make sure you have deployed dependencies

##### install boto3 python module (use python environment)

```
python3 -m venv /tmp/venv
source /tmp/venv/bin/activate
python3 -m pip install boto3
```

#### Run playbooks for deploy AI Broker

```bash
export ARTIFACTORY_USERNAME=""
export ARTIFACTORY_TOKEN=""
export MAS_ICR_CP=""
export MAS_ICR_CPOPEN=""
export MAS_ENTITLEMENT_USERNAME=""
export MAS_ENTITLEMENT_KEY=""
export MAS_INSTANCE_ID=""
export MAS_APP_CHANNEL=""
export MAS_CATALOG_VERSION=""
export IBM_ENTITLEMENT_KEY=${MAS_ENTITLEMENT_KEY}
export MAS_CONFIG_DIR=""
export DRO_CONTACT_EMAIL=""
export DRO_CONTACT_FIRSTNAME=""
export DRO_CONTACT_LASTNAME=""
export SLS_MONGODB_CFG_FILE=${MAS_CONFIG_DIR}/mongo-mongoce.yml
export SLS_LICENSE_ID=""
export SLS_LICENSE_FILE=""
export INSTALL_DB2=""
export INSTALL_MINIO=""
export INSTALL_MARIADB=""
export INSTALL_MONGO=""
export INSTALL_SLS=""
export INSTALL_DRO=""
export MAS_AIBROKER_S3_BUCKET_PREFIX=""
export MAS_AIBROKER_S3_REGION=""
export MAS_AIBROKER_S3_ENDPOINT_URL=""
export MAS_AIBROKER_TENANT_S3_REGION=""
export MAS_AIBROKER_TENANT_S3_ENDPOINT_URL=""
export MAS_AIBROKER_TENANT_S3_BUCKET_PREFIX=""
export MAS_AIBROKER_TENANT_S3_ACCESS_KEY=""
export MAS_AIBROKER_TENANT_S3_SECRET_KEY=""
export RSL_URL=""
export RSL_ORG_ID=""
export RSL_TOKEN=""
export MINIO_ROOT_PASSWORD=""
export MAS_AIBROKER_STORAGE_ACCESSKEY=""
export MAS_AIBROKER_STORAGE_SECRETKEY=${MINIO_ROOT_PASSWORD}
export MAS_AIBROKER_STORAGE_HOST=""
export MAS_AIBROKER_STORAGE_SSL=""
export MAS_AIBROKER_STORAGE_PROVIDER=""
export MAS_AIBROKER_STORAGE_PORT=""
export MAS_AIBROKER_STORAGE_REGION=""
export MAS_AIBROKER_STORAGE_PIPELINES_BUCKET=""
export MAS_AIBROKER_STORAGE_TENANTS_BUCKET=""
export MAS_AIBROKER_STORAGE_TEMPLATES_BUCKET=""
export MARIADB_PASSWORD=""
export MAS_AIBROKER_DB_HOST=""
export MAS_AIBROKER_DB_PORT=""
export MAS_AIBROKER_DB_USER=""
export MAS_AIBROKER_DB_DATABASE=""
export MAS_AIBROKER_DB_SECRET_NAME=""
export MAS_AIBROKER_DB_SECRET_VALUE=${MARIADB_PASSWORD}
export MAS_AIBROKER_WATSONXAI_APIKEY=""
export MAS_AIBROKER_WATSONXAI_URL=""
export MAS_AIBROKER_WATSONXAI_PROJECT_ID=""
export MAS_AIBROKER_SUBSCRIPTION_ID=""
export MAS_AIBROKER_DRO_TENANT_ID=""
export MAS_AIBROKER_TENANT_ENTITLEMENT_START_DATE="YYYY-MM-DD"
export MAS_AIBROKER_TENANT_ENTITLEMENT_END_DATE="YYYY-MM-DD"
oc login --token=xxxx --server=https://myocpserver
ansible-playbook playbooks/oneclick_add_aibroker.yml
```

* `MAS_AIBROKER_SLS_REGISTRATION_KEY` - value can be found in `ibm-sls` namespace, in pod  `sls-api-licensing-85699fb57-9lmrq` please look in environments tab, then value `REGISTRATION_KEY`
* `MAS_AIBROKER_DRO_TOKEN` - go to `mas-instance_id-core` namespace and in secrets find `dro-apikey`
* in `AWS` for `MAS_AIBROKER_STORAGE_PIPELINES_BUCKET`,    `MAS_AIBROKER_STORAGE_TENANTS_BUCKET`,  `MAS_AIBROKER_STORAGE_TEMPLATES_BUCKET` user need to create S3 buckets with unique name

## NOTICE: playbook oneclick_add_aibroker.yml will run roles: 

### Roles: * optional

    - ibm.mas_devops.ibm_catalogs
    - ibm.mas_devops.cert_manager
    - ibm.mas_devops.mongodb
    - ibm.mas_devops.sls
    - ibm.mas_devops.dro
    - ibm.mas_devops.db2
    - ibm.mas_devops.minio
    - ibm.mas_devops.mariadb

### Role: odh

* Install Red Hat OpenShift Serverless Operator
* Install Red Hat OpenShift Service Mesh Operator
* Install Authorino Operator
* Install Open Data Hub Operator
* Create DSCInitialization instance
* Create Data Science Cluster
* Create Create Data Science Pipelines Application

### Role: kmodels

* Install Kmodel controller
* Install istio
* Install Kmodel store
* Install Kmodel watcher

### Role: aibroker

* Install AI Broker api application

### Role: aibroker

* Create AI Broker tenant
* Create, delete AI Broker API Key
* Create, delete AWS S3 API Key
* Create, delete WatsonX AI API Key

## How to create S3

### Prerequisites

* IBM AI Broker Application

#### Run playbooks

```bash
export MAS_INSTANCE_ID="<instanceId>"
export MAS_AIBROKER_STORAGE_ACCESSKEY="<storage provider access key>"
export MAS_AIBROKER_STORAGE_SECRETKEY="<storage provider secret key>"
export MAS_AIBROKER_STORAGE_HOST="<storage provider host>"
export MAS_AIBROKER_STORAGE_REGION="<storage provider region>"
export MAS_AIBROKER_S3_ACTION="install"
export ROLE_NAME="aibroker"
oc login --token=xxxx --server=https://myocpserver
ansible-playbook playbooks/run_role.yml
```

## How to delete S3

### Prerequisites

* S3 created in a cluster

#### Run playbooks

```bash
export MAS_INSTANCE_ID="<instanceId>"
export MAS_AIBROKER_STORAGE_ACCESSKEY="<storage provider access key>"
export MAS_AIBROKER_STORAGE_SECRETKEY="<storage provider secret key>"
export MAS_AIBROKER_STORAGE_HOST="<storage provider host>"
export MAS_AIBROKER_STORAGE_REGION="<storage provider region>"
export MAS_AIBROKER_S3_ACTION="remove"
export ROLE_NAME="aibroker"
oc login --token=xxxx --server=https://myocpserver
ansible-playbook playbooks/run_role.yml
```

## How to create API Key

### Prerequisites

* IBM AI Broker Application

#### Run playbooks

```bash
export MAS_INSTANCE_ID="<instanceId>"
export MAS_AIBROKER_APIKEY_ACTION="install"
export ROLE_NAME="aibroker"
oc login --token=xxxx --server=https://myocpserver
ansible-playbook playbooks/run_role.yml
```

## How to delete API Key

### Prerequisites

* API Key created in a cluster

#### Run playbooks

```bash
export MAS_INSTANCE_ID="<instanceId>"
export MAS_AIBROKER_APIKEY_ACTION="remove"
export ROLE_NAME="aibroker"
oc login --token=xxxx --server=https://myocpserver
ansible-playbook playbooks/run_role.yml
```

## How to create WatsonX API Key

### Prerequisites

* IBM AI Broker Application

#### Run playbooks

```bash
export MAS_INSTANCE_ID="<instanceId>"
export MAS_AIBROKER_WATSONX_ACTION="install"
export ROLE_NAME="aibroker"
oc login --token=xxxx --server=https://myocpserver
ansible-playbook playbooks/run_role.yml
```

## How to WatsonX API Key

### Prerequisites

* WatsonX API Key created in a cluster

#### Run playbooks

```bash
export MAS_INSTANCE_ID="<instanceId>"
export MAS_AIBROKER_WATSONX_ACTION="remove"
export ROLE_NAME="aibroker"
oc login --token=xxxx --server=https://myocpserver
ansible-playbook playbooks/run_role.yml
```

# create tanant

```bash
export MAS_AIBROKER_TENANT_NAME="user7"
export MAS_AIBROKER_SLS_SUBSCRIPTION_ID="007"
export TENANT_ACTION="install"
export ROLE_NAME="aibroker_tenant"
export MAS_AIBROKER_SAAS="true"
export MAS_AIBROKER_DOMAIN=""
export MAS_AIBROKER_SLS_URL="https://sls.ibm-sls.ibm-sls."${MAS_AIBROKER_DOMAIN}
export MAS_AIBROKER_SLS_REGISTRATION_KEY=""
export MAS_AIBROKER_DRO_URL="https://ibm-data-reporter-redhat-marketplace."${MAS_AIBROKER_DOMAIN}
export MAS_AIBROKER_DRO_TOKEN=""
export MAS_AIBROKER_SLS_CACERT=""
export MAS_AIBROKER_DRO_CACERT=""
export MAS_AIBROKER_WATSONXAI_APIKEY=""
export MAS_AIBROKER_WATSONXAI_URL=""
export MAS_AIBROKER_WATSONXAI_PROJECT_ID=""
export MAS_AIBROKER_STORAGE_ACCESSKEY=""
export MAS_AIBROKER_STORAGE_SECRETKEY=""
export MAS_AIBROKER_STORAGE_HOST=""
export MAS_AIBROKER_STORAGE_SSL=""
export MAS_AIBROKER_STORAGE_PROVIDER=""
export MAS_AIBROKER_STORAGE_PORT=""
export MAS_AIBROKER_STORAGE_REGION=""
export MAS_AIBROKER_STORAGE_PIPELINES_BUCKET=""
export MAS_AIBROKER_STORAGE_TENANTS_BUCKET=""
export MAS_AIBROKER_STORAGE_TEMPLATES_BUCKET=""
oc login --token=xxxx --server=https://myocpserver
ansible-playbook playbooks/run_role.yml
```

* `MAS_AIBROKER_SLS_REGISTRATION_KEY` - value can be found in `ibm-sls` namespace, in pod  `sls-api-licensing-85699fb57-9lmrq` please look in environments tab, then value `REGISTRATION_KEY`
* `MAS_AIBROKER_DRO_TOKEN` - go to `mas-instance_id-core` namespace and in secrets find `dro-apikey`

**NOTE:** for create addidional tenants we don't need to specify buckets
