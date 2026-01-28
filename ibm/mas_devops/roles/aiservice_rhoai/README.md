AI Service RHOAI
===============================================================================
This role provides support to deploy rhoai components for AI Broker Application:

* Install Red Hat OpenShift Serverless Operator
* Install Red Hat OpenShift Service Mesh Operator
* Install Authorino Operator
* Install Open Data Hub Operator
* Create DSCInitialization instance
* Create Data Science Cluster
* Create Create Data Science Pipelines Application

Role Variables
--------------

### tenantName

The tenant name for rhoai role.

* Environment Variable: `AISERVICE_TENANT_NAME`
* Default Value: `user`

### serverless_catalog_source

The serverless catalog source for rhoai role.

* Environment Variable: `SERVERLESS_CATALOG_SOURCE`
* Default Value: `redhat-operators`

### serverless_channel

The serverless_channel for rhoai role.

* Environment Variable: `SERVERLESS_CHANNEL`
* Default Value: `stable`

### service_mesh_channel

The service mesh channel for rhoai role.

* Environment Variable: `SERVICEMESH_CHANNEL`
* Default Value: `stable`

### service_mesh_catalog_source

The service mesh catalog source for rhoai role.

* Environment Variable: `SERVICEMESH_CATALOG_SOURCE`
* Default Value: `redhat-operators`

### authorino_catalog_source

The authorino catalog source for rhoai role.

* Environment Variable: `AUTHORINO_CATALOG_SOURCE`
* Default Value: `community-operators`

### rhoai_channel

The rhoai channel for rhoai role.

* Environment Variable: `RHOAI_CHANNEL`
* Default Value: `fast`

### rhoai_catalog_source

The rhoai catalog source for rhoai role.

* Environment Variable: `RHOAI_CATALOG_SOURCE`
* Default Value: `community-operators`

## License

EPL-2.0
