ibmcloud mongodb
=================

Role Variables
--------------

### mongodb_namespace
The namespace where the operator and MongoDb cluster will be deployed.

- Environment Variable: `MONGODB_NAMESPACE`
- Default Value: `mongoce`

### ibm_mongo_admin_credentials_secret_name
Secret for MongoDB Admin credentials.

- Secret Name: `<mongo-name>-admin-credentials`

### ibm_mongo_backup_id
CRN ID for backup resource

### is_restore
TODO

- Default Value: `false`

### ibmcloud_resourcegroup
Required.IBM Cloud Resource Group under which resource group will be created.

- Environment Variable: `IBMCLOUD_RESOURCEGROUP`
- Default Value: `false`

### ibmcloud_region
Required.IBM Cloud region where MongoDB resources will be created.

- Environment Variable: `IBMCLOUD_REGION`
- Default Value: `us-east`

### ibmcloud_region
Required.IBM Cloud API Key.

- Environment Variable: `IBMCLOUD_APIKEY`

### ibm_mongo_config
File containing Configurations related to MongoDB.
Following parameters can be set in this file

- mongo_plan
- mongo_location
- mongo_service
- mongo_service_endpoints
- mongo_version
- mongo_memory
- mongo_disk
- mongo_cpu
- mongo_name




