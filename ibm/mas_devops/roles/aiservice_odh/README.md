# AI Service ODH
This role provides support to deploy odh components for AI Broker Application:

* Install Red Hat OpenShift Serverless Operator
* Install Red Hat OpenShift Service Mesh Operator
* Install Authorino Operator
* Install Open Data Hub Operator
* Create DSCInitialization instance
* Create Data Science Cluster
* Create Create Data Science Pipelines Application

## Role Variables

### tenantName
Tenant identifier for the Open Data Hub deployment.

- Optional
- Environment Variable: `AISERVICE_TENANT_NAME`
- Default: `user`

**Purpose**: Identifies the tenant for multi-tenant ODH deployments, used for resource isolation and organization.

**When to use**: Override the default when deploying multiple ODH instances or when organizational naming conventions require specific tenant identifiers.

**Valid values**: Alphanumeric string (e.g., `user`, `team1`, `prod-tenant`)

**Impact**: Determines the tenant context for ODH resources and configurations.

**Related variables**: None

**Notes**: The default `user` is suitable for single-tenant deployments.

### serverless_catalog_source
Catalog source for Red Hat OpenShift Serverless Operator.

- Optional
- Environment Variable: `SERVERLESS_CATALOG_SOURCE`
- Default: `redhat-operators`

**Purpose**: Specifies which operator catalog provides the OpenShift Serverless Operator required for ODH.

**When to use**: Use default for standard deployments. Override for custom or mirrored catalogs in air-gapped environments.

**Valid values**: Valid CatalogSource name (e.g., `redhat-operators`, `custom-catalog`)

**Impact**: Determines the source of the Serverless operator. Incorrect catalog will prevent operator installation.

**Related variables**: [`serverless_channel`](#serverless_channel)

**Notes**:
- OpenShift Serverless is required for ODH data science pipelines
- Verify catalog exists: `oc get catalogsource -n openshift-marketplace`

### serverless_channel
Subscription channel for OpenShift Serverless Operator.

- Optional
- Environment Variable: `SERVERLESS_CHANNEL`
- Default: `stable`

**Purpose**: Controls which version stream of OpenShift Serverless will be installed and receive updates.

**When to use**: Use default `stable` for production. Override only for specific version requirements.

**Valid values**: Valid Serverless operator channel (e.g., `stable`, `stable-1.28`)

**Impact**: Determines the Serverless version installed and which automatic updates are received.

**Related variables**: [`serverless_catalog_source`](#serverless_catalog_source)

**Notes**: The `stable` channel provides the latest stable release with automatic updates.

### service_mesh_channel
Subscription channel for Red Hat OpenShift Service Mesh Operator.

- Optional
- Environment Variable: `SERVICEMESH_CHANNEL`
- Default: `stable`

**Purpose**: Controls which version stream of OpenShift Service Mesh will be installed for ODH networking.

**When to use**: Use default `stable` for production. Override for specific version requirements.

**Valid values**: Valid Service Mesh operator channel (e.g., `stable`, `stable-2.3`)

**Impact**: Determines the Service Mesh version installed and which automatic updates are received.

**Related variables**: [`service_mesh_catalog_source`](#service_mesh_catalog_source)

**Notes**:
- Service Mesh is required for ODH model serving and networking
- The `stable` channel provides the latest stable release

### service_mesh_catalog_source
Catalog source for Red Hat OpenShift Service Mesh Operator.

- Optional
- Environment Variable: `SERVICEMESH_CATALOG_SOURCE`
- Default: `redhat-operators`

**Purpose**: Specifies which operator catalog provides the OpenShift Service Mesh Operator required for ODH.

**When to use**: Use default for standard deployments. Override for custom or mirrored catalogs in air-gapped environments.

**Valid values**: Valid CatalogSource name (e.g., `redhat-operators`, `custom-catalog`)

**Impact**: Determines the source of the Service Mesh operator. Incorrect catalog will prevent operator installation.

**Related variables**: [`service_mesh_channel`](#service_mesh_channel)

**Notes**: Verify catalog exists: `oc get catalogsource -n openshift-marketplace`

### authorino_catalog_source
Catalog source for Authorino Operator.

- Optional
- Environment Variable: `AUTHORINO_CATALOG_SOURCE`
- Default: `community-operators`

**Purpose**: Specifies which operator catalog provides the Authorino Operator for ODH authorization.

**When to use**: Use default for standard deployments. Override for custom or mirrored catalogs in air-gapped environments.

**Valid values**: Valid CatalogSource name (e.g., `community-operators`, `custom-catalog`)

**Impact**: Determines the source of the Authorino operator. Incorrect catalog will prevent operator installation.

**Related variables**: None

**Notes**:
- Authorino provides authorization for ODH model serving
- Available in community-operators catalog by default

### odh_channel
Subscription channel for Open Data Hub Operator.

- Optional
- Environment Variable: `ODH_CHANNEL`
- Default: `fast`

**Purpose**: Controls which version stream of Open Data Hub will be installed and receive updates.

**When to use**: Use `fast` for latest features. Use `stable` for production environments requiring more testing.

**Valid values**: Valid ODH operator channel (e.g., `fast`, `stable`)

**Impact**: Determines the ODH version installed and update frequency. `fast` channel receives updates more quickly than `stable`.

**Related variables**: [`odh_catalog_source`](#odh_catalog_source)

**Notes**:
- `fast` channel provides latest features but may be less stable
- `stable` channel recommended for production deployments

### odh_catalog_source
Catalog source for Open Data Hub Operator.

- Optional
- Environment Variable: `ODH_CATALOG_SOURCE`
- Default: `community-operators`

**Purpose**: Specifies which operator catalog provides the Open Data Hub Operator.

**When to use**: Use default for standard deployments. Override for custom or mirrored catalogs in air-gapped environments.

**Valid values**: Valid CatalogSource name (e.g., `community-operators`, `custom-catalog`)

**Impact**: Determines the source of the ODH operator. Incorrect catalog will prevent operator installation.

**Related variables**: [`odh_channel`](#odh_channel)

**Notes**:
- ODH is available in community-operators catalog
- For air-gapped environments, mirror the catalog and update this variable


## Example Playbook

```yaml
- hosts: localhost
  vars:
    # Add required variables here
  roles:
    - ibm.mas_devops.aiservice_odh
```

## License

EPL-2.0
