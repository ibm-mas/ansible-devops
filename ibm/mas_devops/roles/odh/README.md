# odh

=====

This role provides support to deploy odh components for AI Broker Application:

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

The tenant name for odh role.

* Environment Variable: `MAS_AIBROKER_TENANT_NAME`
* Default Value: `user`

### serverless_catalog_source

The serverless catalog source for odh role.

* Environment Variable: `SERVERLESS_CATALOG_SOURCE`
* Default Value: `redhat-operators`

### serverless_channel

The serverless_channel for odh role.

* Environment Variable: `SERVERLESS_CHANNEL`
* Default Value: `stable`

### service_mesh_channel

The service mesh channel for odh role.

* Environment Variable: `SERVICEMESH_CHANNEL`
* Default Value: `stable`

### service_mesh_catalog_source

The service mesh catalog source for odh role.

* Environment Variable: `SERVICEMESH_CATALOG_SOURCE`
* Default Value: `redhat-operators`

### authorino_catalog_source

The authorino catalog source for odh role.

* Environment Variable: `AUTHORINO_CATALOG_SOURCE`
* Default Value: `community-operators`

### odh_channel

The odh channel for odh role.

* Environment Variable: `ODH_CHANNEL`
* Default Value: `fast`

### odh_catalog_source

The odh catalog source for odh role.

* Environment Variable: `ODH_CATALOG_SOURCE`
* Default Value: `community-operators`

### odh_operator_version

The odh operator version for odh role.

* Environment Variable: `ODH_OPERATOR_VERSION`
* Default Value: `opendatahub-operator.v2.11.1`

## License

EPL-2.0
