# Install AI Broker Application

## Prerequisites

You will need a RedHat OpenShift v4.12 cluster with IBM Maximo Application Suite Core v8.11 already be installed, the [oneclick-core](oneclick-core.md) playbook can be used to set this up. AI Broker can be also installed on cluster without IBM Maximo Application Suite Core. However with stanadlone AI Broker there are few dependences. This playbook will check if needed components exists on cluster. If playbooks finds that some components are missing - playbook will install all missing dependencies

### Dependencies:

- ibm-operator-catalog
- ibm-common-services
- cert-manager

## Overview

This playbook will add **AI Broker v1.0.x** to an existing IBM Maximo Application Suite Core installation or as standalone instance.

This playbook can be ran against any OCP cluster regardless of its type; whether it's running in IBM Cloud, Azure, AWS, or your local datacenter.

- Install dependencies:
  - Install ibm operator catalog (~10 minutes)
  - Install ibm common services (~10 minutes)
  - Install cert-manager (~10 minutes)
- Install AI broker application:
  - Install application (~10 Minutes)
  - Configure AI Broker (kmodels, tenant, etc) (~10 Minutes)

All timings are estimates, see the individual pages for each of these playbooks for more information. Use this sample playbook as a starting point for installing application, just customize the application install and configure stages at the end of the playbook.

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

## Optional environment variables

- `MAS_APP_CHANNEL` Your custom AI broker application channel
- `MAS_CATALOG_VERSION` Your custom AI broker catalog version
- `STORAGE_PROVIDER` Your custom storage provider (aws, minio)

## Usage

!!! tip
If you do not want to set up all the dependencies on your local system, you can run the playbook from inside the CLI container image: `docker run -ti --pull always quay.io/ibmmas/cli`

### AI broker deployment steps

```bash
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

oc login --token=xxxx --server=https://myocpserver
ansible-playbook ibm.mas_devops.oneclick_add_aibroker
```
