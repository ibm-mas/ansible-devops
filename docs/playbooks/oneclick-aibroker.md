# Install AI Broker Application

## Prerequisites

You will need a RedHat OpenShift v4.14 or above with IBM Maximo Application Suite Core v9.x already be installed, the [oneclick-core](oneclick-core.md) playbook can be used to set this up.

### Dependencies:

* Object Storage
  + Minio ( if customer does not use AWS S3 )
  + AWS S3 ( if customer owns AWS S3 bucket )
* MariaDB database (installed in cluster where aibroker instance)
* IBM Maximo Application Suite Core v9.x

## Overview

This playbook will add **AI Broker v1.0.x** to an existing IBM Maximo Application Suite Core installation.

This playbook can be ran against any OCP cluster regardless of its type; whether it's running in IBM Cloud, Azure, AWS, or your local datacenter.

* Install dependencies:
  + Install IBM Maximo Application Suite Core v9.x (~30 Minutes)
  + Install MariaDB (~5 minutes)
  + Install Minio (~5 minutes)
* Install AI broker application:
  + Install application (~10 Minutes)
  + Configure AI Broker (kmodels, tenant, etc) (~5 Minutes)

All timings are estimates, see the individual pages for each of these playbooks for more information. Use this sample playbook as a starting point for installing application, just customize the application install and configure stages at the end of the playbook.

## Storage providers

**Notice !!!**

AI Broker supports **AWS** and **Minio** storage providers.

## Required environment variables

* `MAS_INSTANCE_ID` Declare the instance ID for the AI Broker install
* `MAS_ENTITLEMENT_KEY` Your IBM Entitlement key to access the IBM Container Registry
* `MAS_ENTITLEMENT_USERNAME` Your IBM Entitlement user to access the IBM Container Registry
* `STORAGE_ACCESSKEY` Your strage provider access key
* `STORAGE_SECRETKEY` Your storage provider secret key
* `STORAGE_HOST` Your storage provider host
* `STORAGE_REGION` Your storage provider region - only when use AWS S3 instance
* `STORAGE_PROVIDER` Your storage provider name
* `STORAGE_SSL` Your storage ssl (true/false)
* `STORAGE_PIPELINES_BUCKET` Your piplines bucket
* `STORAGE_TENANTS_BUCKET` Your tenants bucket
* `STORAGE_TEMPLATES_BUCKET` Your templates bucket
* `WATSONXAI_APIKEY` You WatsonX AI api key
* `WATSONXAI_URL` You WatsonX AI url
* `WATSONXAI_PROJECT_ID` You WatsonX projedt Id
* `DB_HOST` Your database instance host
* `DB_PORT` Your database instance port
* `DB_USER` Your database instance user
* `DB_DATABASE` Your database instance datbase name
* `DB_SECRET_NAME` Your database instance secret name
* `DB_SECRET_VALUE` Your database instance password

## Optional environment variables

* `MAS_AIBROKER_CHANNEL` Your custom AI broker application channel
* `MAS_ICR_CP` Provide custom registry for AI Broker applications
* `MAS_ICR_CPOPEN` Provide custom registry for AI Broker operator
* `MAS_CATALOG_VERSION` Your custom AI broker catalog version
* `ARTIFACTORY_USERNAME` Your artifactory user name to access - this is needed if user deploy from custom registry for example `docker-na-public.artifactory.swg-devops.com`
* `ARTIFACTORY_TOKEN` Your artifactory token for user to access - this is needed if user deploy from custom registry for example `docker-na-public.artifactory.swg-devops.com`
* `TENANT_ACTION` Whether to install or remove tenant (default value is: install)
* `APIKEY_ACTION` Whether to install or remove or update apikey (default value is: install)
* `WATSONX_ACTION` Whether to install or remove watsonx secret (default value is: install)
* `S3_ACTION` Whether to install or remove s3 (default value is: install)

## Usage

### AI broker deployment steps

#### Notice: For S3 manage please make sure you have deployed dependencies

##### install boto3 python module (use python environment)

```
python3 -m venv /tmp/venv
source /tmp/venv/bin/activate
python3 -m pip install boto3
```

#### Run playbooks for deploy AI Broker from internal registry ex. `docker-na-public.artifactory.swg-devops.com`

```bash
export ARTIFACTORY_USERNAME="<artifactory user>"
export ARTIFACTORY_TOKEN="<artifactory token>"
export MAS_ICR_CP="<internal redistry for aibroker applications>"
export MAS_ICR_CPOPEN="<internal redistry for aibroker operator>"
export MAS_INSTANCE_ID="<instanceId>"
export STORAGE_ACCESSKEY="<storage provider access key>"
export STORAGE_SECRETKEY="<storage provider secret key>"
export STORAGE_HOST="<storage provider host>"
export STORAGE_SSL="true or false"
export STORAGE_REGION="<storage provider region - only for aws>"
export STORAGE_PROVIDER="<storage provider name>"
export STORAGE_PORT="<storage provider port - only for minio>"
export STORAGE_PIPELINES_BUCKET="<pipelines bucket name>"
export STORAGE_TENANTS_BUCKET="<tenants bucket name>"
export STORAGE_TEMPLATES_BUCKET="<templates bucket name>"
export APP_DOMAIN="<app domain>"
export WATSONXAI_APIKEY="<watsonx AI api key>"
export WATSONXAI_URL="<watsonx AI url>"
export WATSONXAI_PROJECT_ID="<watsonx AI project ID>"
export DB_HOST="<database instance host>"
export DB_PORT="<database instance port>"
export DB_USER="<database instance user>"
export DB_DATABASE="<database instance datbase name>"
export DB_SECRET_NAME="<database instance secret name>"
export DB_SECRET_VALUE="<database instance password>"

oc login --token=xxxx --server=https://myocpserver
ansible-playbook playbooks/oneclick_add_aibroker.yml
```

#### Run playbooks for deploy AI Broker from public registry ex. `icr.io`

```bash
export MAS_ENTITLEMENT_USERNAME="<user>"
export MAS_ENTITLEMENT_KEY="<token>"
export MAS_INSTANCE_ID="<instanceId>"
export STORAGE_ACCESSKEY="<storage provider access key>"
export STORAGE_SECRETKEY="<storage provider secret key>"
export STORAGE_HOST="<storage provider host>"
export STORAGE_SSL="true or false"
export STORAGE_REGION="<storage provider region - only for aws>"
export STORAGE_PROVIDER="<storage provider name>"
export STORAGE_PORT="<storage provider port - only for minio>"
export STORAGE_PIPELINES_BUCKET="<pipelines bucket name>"
export STORAGE_TENANTS_BUCKET="<tenants bucket name>"
export STORAGE_TEMPLATES_BUCKET="<templates bucket name>"
export APP_DOMAIN="<app domain>"
export WATSONXAI_APIKEY="<watsonx AI api key>"
export WATSONXAI_URL="<watsonx AI url>"
export WATSONXAI_PROJECT_ID="<watsonx AI project ID>"
export DB_HOST="<database instance host>"
export DB_PORT="<database instance port>"
export DB_USER="<database instance user>"
export DB_DATABASE="<database instance datbase name>"
export DB_SECRET_NAME="<database instance secret name>"
export DB_SECRET_VALUE="<database instance password>"

oc login --token=xxxx --server=https://myocpserver
ansible-playbook playbooks/oneclick_add_aibroker.yml
```

### 

## NOTICE: playbook oneclick_add_aibroker.yml will run three roles: 

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
export STORAGE_ACCESSKEY="<storage provider access key>"
export STORAGE_SECRETKEY="<storage provider secret key>"
export STORAGE_HOST="<storage provider host>"
export STORAGE_REGION="<storage provider region>"
export S3_ACTION="install"
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
export STORAGE_ACCESSKEY="<storage provider access key>"
export STORAGE_SECRETKEY="<storage provider secret key>"
export STORAGE_HOST="<storage provider host>"
export STORAGE_REGION="<storage provider region>"
export S3_ACTION="remove"
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
export APIKEY_ACTION="install"
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
export APIKEY_ACTION="remove"
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
export WATSONX_ACTION="install"
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
export WATSONX_ACTION="remove"
export ROLE_NAME="aibroker"
oc login --token=xxxx --server=https://myocpserver
ansible-playbook playbooks/run_role.yml
