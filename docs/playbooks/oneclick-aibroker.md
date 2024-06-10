# Install AI Broker Application

## Prerequisites

You will need a RedHat OpenShift v4.12 cluster with IBM Maximo Application Suite Core v9.x already be installed, the [oneclick-core](oneclick-core.md) playbook can be used to set this up.

### Dependencies:

- IBM Maximo Application Suite Core v9.x

## Overview

This playbook will add **AI Broker v1.0.x** to an existing IBM Maximo Application Suite Core installation or as standalone instance.

This playbook can be ran against any OCP cluster regardless of its type; whether it's running in IBM Cloud, Azure, AWS, or your local datacenter.

- Install dependencies:
  - Install IBM Maximo Application Suite Core v9.x
- Install AI broker application:
  - Install application (~10 Minutes)
  - Configure AI Broker (kmodels, tenant, etc) (~10 Minutes)

All timings are estimates, see the individual pages for each of these playbooks for more information. Use this sample playbook as a starting point for installing application, just customize the application install and configure stages at the end of the playbook.

## Storage providers

**Notice !!!**

AI Broker supports **AWS** and **Minio** storage providers.

## Required environment variables

- `MAS_INSTANCE_ID` Declare the instance ID for the AI Broker install
- `IBM_ENTITLEMENT_KEY` Your IBM Entitlement key to access the IBM Container Registry
- `IBM_ENTITLEMENT_USERNAME` Your IBM Entitlement user to access the IBM Container Registry
- `STORAGE_ACCESSKEY` Your strage provider access key
- `STORAGE_SECRETKEY` Your storage provider secret key
- `STORAGE_HOST` Your storage provider host
- `STORAGE_REGION` Your storage provider region
- `STORAGE_PROVIDER` Your storage provider name
- `ICR_PASSWORD` Your ICR registry password
- `ICR_USERNAME` Your ICR registry user name
- `TENANT_NAME` Your Aibroker tenant name
- `APP_DOMAIN` Your app domain for example: `apps.dev.cp.fyre.ibm.com`
- `STORAGE_PIPELINES_BUCKET` Your piplines bucket
- `STORAGE_TENANTS_BUCKET` Your tenants bucket
- `WATSONXAI_APIKEY` You WatsonX AI api key
- `WATSONXAI_URL` You WatsonX AI url
- `WATSONXAI_PROJECT_ID` You WatsonX projedt Id

## Optional environment variables

- `MAS_AIBROKER_CHANNEL` Your custom AI broker application channel
- `MAS_CATALOG_VERSION` Your custom AI broker catalog version
- `STORAGE_PROVIDER` Your custom storage provider (aws, minio)
- `TENANT_ACTION` Whether to install or remove tenant (default value is: install)
- `APIKEY_ACTION` Whether to install or remove or update apikey (default value is: install)
- `WATSONX_ACTION` Whether to install or remove watsonx secret (default value is: install)
- `S3_ACTION` Whether to install or remove s3 (default value is: install)

## Usage

### AI broker deployment steps

#### Notice: For S3 manage please make sure you have deployed dependencies

##### install boto3 python module (use python environment)

```
python3 -m venv /tmp/venv
source /tmp/venv/bin/activate
python3 -m pip install boto3
```

#### Notice: For WatsonX AI manage please make sure you have deployed dependencies

##### install ibm-watson-machine-learning python module (use python environment)

```
python3 -m venv /tmp/venv
source /tmp/venv/bin/activate
python3 -m pip install ibm-watson-machine-learning
```

#### Run playbooks

```bash
export ARTIFACTORY_USERNAME="<artifactory user>"
export ARTIFACTORY_TOKEN="<artifactory token>"
export IBM_ENTITLEMENT_USERNAME="<user>"
export IBM_ENTITLEMENT_KEY="<token>"
export MAS_INSTANCE_ID="aibroker"
export STORAGE_ACCESSKEY="<storage provider access key>"
export STORAGE_SECRETKEY="<storage provider secret key>"
export STORAGE_HOST="<storage provider host>"
export STORAGE_REGION="<storage provider region>"
export STORAGE_PROVIDER="<storage provider name>"
export ICR_USERNAME="<irc username>"
export ICR_PASSWORD="<icr password>"
export TENANT_NAME="user"
export STORAGE_PIPELINES_BUCKET="<pipelines bucket name>"
export STORAGE_TENANTS_BUCKET="<tenants bucket name>"
export APP_DOMAIN="<app domain>"
export WATSONXAI_APIKEY="<watsonx AI api key>"
export WATSONXAI_URL="<watsonx AI url>"
export WATSONXAI_PROJECT_ID="<watsonx AI project ID>"

oc login --token=xxxx --server=https://myocpserver
ansible-playbook playbooks/oneclick_add_aibroker.yml
```
## How to create tenant

### Prerequisites

- IBM AI Broker Application

#### Run playbooks

```bash
export MAS_INSTANCE_ID="aibroker"
export TENANT_NAME="<Tenant Name>"
export TENANT_ACTION="install"
oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.aibroker
```

## How to delete tenant

### Prerequisites

- Tenant installed in a cluster

#### Run playbooks

```bash
export TENANT_NAME="<Tenant Name>"
export TENANT_ACTION="remove"
oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.aibroker
```

## How to create S3

### Prerequisites

- IBM AI Broker Application

#### Run playbooks

```bash
export MAS_INSTANCE_ID="aibroker"
export TENANT_NAME="<Tenant Name>"
export STORAGE_ACCESSKEY="<storage provider access key>"
export STORAGE_SECRETKEY="<storage provider secret key>"
export STORAGE_HOST="<storage provider host>"
export STORAGE_REGION="<storage provider region>"
export S3_ACTION="install"
oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.aibroker
```

## How to delete S3

### Prerequisites

- S3 created in a cluster

#### Run playbooks

```bash
export MAS_INSTANCE_ID="aibroker"
export TENANT_NAME="<Tenant Name>"
export STORAGE_ACCESSKEY="<storage provider access key>"
export STORAGE_SECRETKEY="<storage provider secret key>"
export STORAGE_HOST="<storage provider host>"
export STORAGE_REGION="<storage provider region>"
export S3_ACTION="remove"
oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.aibroker
```

## How to create API Key

### Prerequisites

- IBM AI Broker Application

#### Run playbooks

```bash
export MAS_INSTANCE_ID="aibroker"
export TENANT_NAME="<Tenant Name>"
export APIKEY_ACTION="install"
oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.aibroker
```

## How to delete API Key

### Prerequisites

- API Key created in a cluster

#### Run playbooks

```bash
export MAS_INSTANCE_ID="aibroker"
export TENANT_NAME="<Tenant Name>"
export APIKEY_ACTION="remove"
oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.aibroker
```
