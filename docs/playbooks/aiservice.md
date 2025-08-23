Install AI Service
===============================================================================

!!! important
    These playbooks are samples to demonstrate how to use the roles in this collection.

    They are **note intended for production use** as-is, they are a starting point for power users to aid in the development of their own Ansible playbooks using the roles in this collection.

    The recommended way to install MAS is to use the [MAS CLI](https://ibm-mas.github.io/cli/), which uses this Ansible Collection to deliver a complete managed lifecycle for your MAS instance.


Dependencies
-------------------------------------------------------------------------------

* IBM Suite License Service installed on OCP cluster or external instance or details from external instance
* IBM Data Reporter Operator installed on OCP cluster or external instance or details from external instance
* Object Storage
  + Minio (installed on the same cluster what aiservice) or external instance or details from external instance
  + AWS S3 (if customer use AWS S3 bucket bucket) buckets needs to have unique names

Overview
-------------------------------------------------------------------------------
This playbook will add **AI Service v9.1.x** to OCP cluster.

This playbook can be ran against any OCP cluster regardless of its type; whether it's running in IBM Cloud, Azure, AWS, or your local datacenter.

- Install dependencies:
    - IBM Maximo Operator Catalog **optional**
    - RedHat Certificate Manager **optional**
    - MongoDb **optional**
    - IBM Suite License Service (~10 Minutes) **optional**
    - IBM Data Reporter Operator (~10 Minutes) **optional**
    - IBM Db2 **optional**
    - Minio (~5 minutes) **optional**
- Install ODH:
    - Install Red Hat OpenShift Serverless Operator
    - Install Red Hat OpenShift Service Mesh Operator
    - Install Authorino Operator
    - Install Open Data Hub Operator
    - Create DSCInitialization instance
    - Create Data Science Cluster
    - Create Create Data Science Pipelines Application
- Install AI Service (using playbook):
    - Install application (~20 Minutes)
    - Configure AI Service (kmodels, tenant, etc) (~20 Minutes)

All timings are estimates, see the individual pages for each of these playbooks for more information. Use this sample playbook as a starting point for installing application, just customize the application install and configure stages at the end of the playbook.


Required environment variables
-------------------------------------------------------------------------------

* `MAS_INSTANCE_ID` Declare the instance ID for the AI service install
* `MAS_ENTITLEMENT_KEY` Your IBM Entitlement key to access the IBM Container Registry
* `MAS_ENTITLEMENT_USERNAME` Your IBM Entitlement user to access the IBM Container Registry
* `MAS_APP_CHANNEL` Aiservice application channel
* `AISERVICE_STORAGE_ACCESSKEY` Your strage provider access key
* `AISERVICE_STORAGE_SECRETKEY` Your storage provider secret key
* `AISERVICE_STORAGE_HOST` Your storage provider host
* `AISERVICE_STORAGE_REGION` Your storage provider region - only when use AWS S3 instance
* `AISERVICE_STORAGE_PROVIDER` Your storage provider name
* `AISERVICE_STORAGE_SSL` Your storage ssl (true/false)
* `AISERVICE_STORAGE_PIPELINES_BUCKET` Your piplines bucket
* `AISERVICE_STORAGE_TENANTS_BUCKET` Your tenants bucket
* `AISERVICE_STORAGE_TEMPLATES_BUCKET` Your templates bucket
* `AISERVICE_WATSONXAI_APIKEY` You WatsonX AI api key
* `AISERVICE_WATSONXAI_URL` You WatsonX AI url
* `AISERVICE_WATSONXAI_PROJECT_ID` You WatsonX projedt Id

!!! tip
    AI service supports **AWS** and **Minio** storage providers.


Required environment variables (SaaS)
-------------------------------------------------------------------------------

* `AISERVICE_SAAS` specify if saas deployment (default value is: false)
* `MAS_CONFIG_DIR` specify config location, mandatory when `AISERVICE_SAAS=true`
* `AISERVICE_DOMAIN` specify cluster domain, mandatory when `AISERVICE_SAAS=true`
* `AISERVICE_SLS_URL` specify SLS url, mandatory when `AISERVICE_SAAS=true`
* `AISERVICE_SLS_REGISTRATION_KEY` specify sls registration key, mandatory when `AISERVICE_SAAS=true`, to get value: look in `ibm-sls` namespace, pod `sls-api-licensing-xxx` and in `Environment` tab check `REGISTRATION_KEY` value
* `AISERVICE_DRO_URL` specify DRO url, mandatory when `AISERVICE_SAAS=true`
* `AISERVICE_DRO_TOKEN` specify DRO token, mandatory when `AISERVICE_SAAS=true` to get value: go to `mas-{{ instance_id }}-core` and look in secret `dro-apikey`
* `DB2_INSTANCE_NAME` specify DB2 instance name (default value is: aiservice), mandatory when `AISERVICE_SAAS=true`
* `IBM_ENTITLEMENT_KEY` specify IBM Entitlement key, mandatory when `AISERVICE_SAAS=true`


Optional environment variables
-------------------------------------------------------------------------------

* `MAS_ICR_CP` Provide custom registry for AI service applications
* `MAS_ICR_CPOPEN` Provide custom registry for AI service operator
* `MAS_CATALOG_VERSION` Your custom AI service catalog version
* `ARTIFACTORY_USERNAME` Your artifactory user name to access - this is needed if user deploy from custom registry for example `docker-na-public.artifactory.swg-devops.com`
* `ARTIFACTORY_TOKEN` Your artifactory token for user to access - this is needed if user deploy from custom registry for example `docker-na-public.artifactory.swg-devops.com`
* `AISERVICE_TENANT_ACTION` Whether to install or remove tenant (default value is: install)
* `AISERVICE_APIKEY_ACTION` Whether to install or remove or update apikey (default value is: install)
* `AISERVICE_WATSONX_ACTION` Whether to install or remove watsonx secret (default value is: install)
* `AISERVICE_S3_ACTION` Whether to install or remove s3 (default value is: install)
* `INSTALL_DB2` Whether to install DB2 (default value is: false)
* `INSTALL_MINIO` Whether to install minio (default value is: false)
* `INSTALL_SLS` Whether to install IBM Suite License Service (default value is: false)
* `INSTALL_DRO` Whether to install IBM Data Reporter Operator (default value is: false)
* `AISERVICE_DB2_USERNAME` The username to use for authentication with the database
* `AISERVICE_DB2_PASSWORD` The password to use for authentication with the database
* `AISERVICE_DB2_JDBC_URL` The JDBC URL specifying the host and port of the database, typically in the format jdbc:db2://host:port/
* `AISERVICE_DB2_SSL_ENABLED` A flag indicating whether to enable SSL encryption for the database connection (default value is: true)
* `USE_AWS_DB2` A flag indicating whether to use an AWS-hosted DB2 instance (default value is: false)
* `AISERVICE_CLUSTER_DOMAIN` Provide custom domain (default value is: empty)
* `AISERVICE_IS_EXTERNAL_ROUTE` A flag indicating to enable external route (default value is: false)

Usage
-------------------------------------------------------------------------------
### AI service deployment steps

!!! tip
    For S3 manage please make sure you have deployed dependencies

Install boto3 python module (use python environment):

```bash
python3 -m venv /tmp/venv
source /tmp/venv/bin/activate
python3 -m pip install boto3
```

Run playbooks for deploy AI service:

- `AISERVICE_SLS_REGISTRATION_KEY` - value can be found in `ibm-sls` namespace, in pod  `sls-api-licensing-85699fb57-9lmrq` please look in environments tab, then value `REGISTRATION_KEY`
- `AISERVICE_DRO_TOKEN` - go to `mas-instance_id-core` namespace and in secrets find `dro-apikey`
- In `AWS` for `AISERVICE_STORAGE_PIPELINES_BUCKET`, `AISERVICE_STORAGE_TENANTS_BUCKET`, `AISERVICE_STORAGE_TEMPLATES_BUCKET` user need to create S3 buckets with unique name


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
export INSTALL_MONGO=""
export INSTALL_SLS=""
export INSTALL_DRO=""
export AISERVICE_S3_BUCKET_PREFIX=""
export AISERVICE_S3_REGION=""
export AISERVICE_S3_ENDPOINT_URL=""
export AISERVICE_TENANT_S3_REGION=""
export AISERVICE_TENANT_S3_ENDPOINT_URL=""
export AISERVICE_TENANT_S3_BUCKET_PREFIX=""
export AISERVICE_TENANT_S3_ACCESS_KEY=""
export AISERVICE_TENANT_S3_SECRET_KEY=""
export RSL_URL=""
export RSL_ORG_ID=""
export RSL_TOKEN=""
export MINIO_ROOT_PASSWORD=""
export AISERVICE_STORAGE_ACCESSKEY=""
export AISERVICE_STORAGE_SECRETKEY=${MINIO_ROOT_PASSWORD}
export AISERVICE_STORAGE_HOST=""
export AISERVICE_STORAGE_SSL=""
export AISERVICE_STORAGE_PROVIDER=""
export AISERVICE_STORAGE_PORT=""
export AISERVICE_STORAGE_REGION=""
export AISERVICE_STORAGE_PIPELINES_BUCKET=""
export AISERVICE_STORAGE_TENANTS_BUCKET=""
export AISERVICE_STORAGE_TEMPLATES_BUCKET=""
export AISERVICE_WATSONXAI_APIKEY=""
export AISERVICE_WATSONXAI_URL=""
export AISERVICE_WATSONXAI_PROJECT_ID=""
export AISERVICE_SUBSCRIPTION_ID=""
export AISERVICE_DRO_TENANT_ID=""
export AISERVICE_TENANT_ENTITLEMENT_START_DATE="YYYY-MM-DD"
export AISERVICE_TENANT_ENTITLEMENT_END_DATE="YYYY-MM-DD"
oc login --token=xxxx --server=https://myocpserver
ansible-playbook playbooks/aiservice.yml
```


Create S3
-------------------------------------------------------------------------------

```bash
export MAS_INSTANCE_ID="<instanceId>"
export AISERVICE_STORAGE_ACCESSKEY="<storage provider access key>"
export AISERVICE_STORAGE_SECRETKEY="<storage provider secret key>"
export AISERVICE_STORAGE_HOST="<storage provider host>"
export AISERVICE_STORAGE_REGION="<storage provider region>"
export AISERVICE_S3_ACTION="install"
export ROLE_NAME="aiservice"
oc login --token=xxxx --server=https://myocpserver
ansible-playbook playbooks/run_role.yml
```


Delete S3
-------------------------------------------------------------------------------

```bash
export MAS_INSTANCE_ID="<instanceId>"
export AISERVICE_STORAGE_ACCESSKEY="<storage provider access key>"
export AISERVICE_STORAGE_SECRETKEY="<storage provider secret key>"
export AISERVICE_STORAGE_HOST="<storage provider host>"
export AISERVICE_STORAGE_REGION="<storage provider region>"
export AISERVICE_S3_ACTION="remove"
export ROLE_NAME="aiservice"
oc login --token=xxxx --server=https://myocpserver
ansible-playbook playbooks/run_role.yml
```


Create API Key
-------------------------------------------------------------------------------

```bash
export MAS_INSTANCE_ID="<instanceId>"
export AISERVICE_APIKEY_ACTION="install"
export ROLE_NAME="aiservice"
oc login --token=xxxx --server=https://myocpserver
ansible-playbook playbooks/run_role.yml
```

Delete API Key
-------------------------------------------------------------------------------

```bash
export MAS_INSTANCE_ID="<instanceId>"
export AISERVICE_APIKEY_ACTION="remove"
export ROLE_NAME="aiservice"
oc login --token=xxxx --server=https://myocpserver
ansible-playbook playbooks/run_role.yml
```

Create WatsonX API Key
-------------------------------------------------------------------------------

```bash
export MAS_INSTANCE_ID="<instanceId>"
export AISERVICE_WATSONX_ACTION="install"
export ROLE_NAME="aiservice"
oc login --token=xxxx --server=https://myocpserver
ansible-playbook playbooks/run_role.yml
```

Delete WatsonX API Key
-------------------------------------------------------------------------------

```bash
export MAS_INSTANCE_ID="<instanceId>"
export AISERVICE_WATSONX_ACTION="remove"
export ROLE_NAME="aiservice"
oc login --token=xxxx --server=https://myocpserver
ansible-playbook playbooks/run_role.yml
```

Create Tenant
-------------------------------------------------------------------------------
The `AISERVICE_SLS_REGISTRATION_KEY` value can be found in `ibm-sls` namespace, in pod  `sls-api-licensing-85699fb57-9lmrq` please look in environments tab, then value `REGISTRATION_KEY`.  To obtain the `AISERVICE_DRO_TOKEN` go to `mas-instance_id-core` namespace and in secrets find `dro-apikey`

```bash
export AISERVICE_TENANT_NAME="user7"
export AISERVICE_SLS_SUBSCRIPTION_ID="007"
export TENANT_ACTION="install"
export ROLE_NAME="aiservice_tenant"
export AISERVICE_SAAS="true"
export AISERVICE_DOMAIN=""
export AISERVICE_SLS_URL="https://sls.ibm-sls.ibm-sls."${AISERVICE_DOMAIN}
export AISERVICE_SLS_REGISTRATION_KEY=""
export AISERVICE_DRO_URL="https://ibm-data-reporter-redhat-marketplace."${AISERVICE_DOMAIN}
export AISERVICE_DRO_TOKEN=""
export AISERVICE_SLS_CACERT=""
export AISERVICE_DRO_CACERT=""
export AISERVICE_WATSONXAI_APIKEY=""
export AISERVICE_WATSONXAI_URL=""
export AISERVICE_WATSONXAI_PROJECT_ID=""
export AISERVICE_STORAGE_ACCESSKEY=""
export AISERVICE_STORAGE_SECRETKEY=""
export AISERVICE_STORAGE_HOST=""
export AISERVICE_STORAGE_SSL=""
export AISERVICE_STORAGE_PROVIDER=""
export AISERVICE_STORAGE_PORT=""
export AISERVICE_STORAGE_REGION=""
export AISERVICE_STORAGE_PIPELINES_BUCKET=""
export AISERVICE_STORAGE_TENANTS_BUCKET=""
export AISERVICE_STORAGE_TEMPLATES_BUCKET=""
oc login --token=xxxx --server=https://myocpserver
ansible-playbook playbooks/run_role.yml
```

!!! tip
    To create addidional tenants we don't need to specify buckets
