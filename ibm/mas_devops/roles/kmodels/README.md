# Kmodels

=====

This role provides support to deploy Kmodels components for AI Broker Application:

* Install Kmodel controller
* Install istio
* Install Kmodel store
* Install Kmodel watcher

Role Variables
--------------

### tenantName

The tenant name for Kmodels role.

* Environment Variable: `MAS_AIBROKER_TENANT_NAME`
* Default Value: `user`

### storage_piplines_bucket

The storage piplines bucket for Kmodels role.

* Environment Variable: `MAS_AIBROKER_STORAGE_PIPELINES_BUCKET`
* Default Value: ``

### storage_tenants_bucket

The storage tenants bucket for Kmodels role.

* Environment Variable: `MAS_AIBROKER_STORAGE_TENANTS_BUCKET`
* Default Value: ``

## License

EPL-2.0
