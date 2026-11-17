# aiservice_rhoai

This role provides support to deploy rhoai components for AI Broker Application:

- Install Red Hat OpenShift Serverless Operator
- Install Red Hat OpenShift Service Mesh Operator
- Install Authorino Operator
- Install Red Hat OpenShift AI Operator
- Create DSCInitialization instance
- Create Data Science Cluster
- Create Data Science Pipelines Application

## Actions

This role supports multiple actions through the `rhoai_action` variable:

- **`install`** (default): Install RHOAI and all dependencies. Automatically detects and migrates existing ODH installations.
- **`uninstall`**: Remove RHOAI and optionally remove Serverless/ServiceMesh operators

### Action Variable

#### rhoai_action

Action to perform on the RHOAI installation — `install` (default) or `uninstall`.

- **Optional**
- Environment Variable: `RHOAI_ACTION`
- Default: `install`

```bash
# Install RHOAI (default) - will auto-migrate ODH if detected
export RHOAI_ACTION=install
ansible-playbook playbook.yml

# Uninstall RHOAI
export RHOAI_ACTION=uninstall
ansible-playbook playbook.yml
```

## ODH to RHOAI Migration

When installing RHOAI, this role automatically:

1. **Detects** existing Open Data Hub (ODH) installations
2. **Preserves** all data science workloads and deployed models
3. **Uninstalls** ODH operator and resources
4. **Installs** RHOAI operator and resources

**Migration is automatic** - no manual intervention required. The migration process:

- Maintains data science pipelines and notebooks
- Preserves model deployments and serving configurations
- Retains all user data and configurations
- Typically completes in 10-12 minutes

## RHOAI v2 to v3 Upgrade

RHOAI does not support an in-place upgrade from v2 to v3. When `rhoai_channel` is a v3 channel (for example `stable-3.x`) and an installed `rhods-operator` v2 CSV is detected, the install action:

1. **Detects** the installed RHOAI major version from the `rhods-operator` Subscription
2. **Uninstalls** RHOAI v2 (DataScienceCluster, DSCInitialization, operator, Authorino, and Serverless/ServiceMesh when in serverless mode)
3. **Installs** RHOAI v3 from the requested channel

Model serving is unavailable while the upgrade runs. InferenceServices must be checked after the upgrade, as the v3 operator recreates the serving components.

This runs automatically from `mas update` when RHOAI v2 is detected.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`rhoai_action`](#rhoai_action) | No | `install` |
| [`rhoai_channel`](#rhoai_channel) | No | `stable-3.x` |
| [`aiservice_rhoai_model_deployment_type`](#aiservice_rhoai_model_deployment_type) | No | `raw` |
| [`serverless_catalog_source`](#serverless_catalog_source) | No | `redhat-operators` |
| [`serverless_channel`](#serverless_channel) | No | `stable` |
| [`service_mesh_channel`](#service_mesh_channel) | No | `stable` |
| [`service_mesh_catalog_source`](#service_mesh_catalog_source) | No | `redhat-operators` |
| [`authorino_catalog_source`](#authorino_catalog_source) | No | `community-operators` |

### RHOAI Operator

#### rhoai_channel

Subscription channel for the Red Hat OpenShift AI operator — for example `stable-3.x` (default). RHOAI is the enterprise-supported version of Open Data Hub and requires a valid Red Hat subscription for enterprise support.

- **Optional**
- Environment Variable: `RHOAI_CHANNEL`
- Default: `stable-3.x`

Controls which version stream of Red Hat OpenShift AI is installed and receives updates. Setting a v3 channel when a v2 `rhods-operator` is installed triggers the automatic v2-to-v3 upgrade described above.

#### aiservice_rhoai_model_deployment_type

Model deployment type for RHOAI — `raw` (default) or `serverless`.

- **Optional**
- Environment Variable: `AISERVICE_RHOAI_MODEL_DEPLOYMENT_TYPE`
- Default: `raw`

When set to `serverless`, the role deploys model serving on OpenShift Serverless and installs the additional Serverless/ServiceMesh components and security context constraints required for it; the `raw` type uses standard deployments.

### Serverless Operator

#### serverless_catalog_source

Catalog source for the Red Hat OpenShift Serverless Operator — a valid CatalogSource name, for example `redhat-operators` or a custom catalog.

- **Optional**
- Environment Variable: `SERVERLESS_CATALOG_SOURCE`
- Default: `redhat-operators`

Determines the source of the Serverless operator; an incorrect catalog will prevent operator installation. Use the default for standard deployments and override for custom or mirrored catalogs in air-gapped environments. OpenShift Serverless is required for RHOAI data science pipelines — verify the catalog exists with `oc get catalogsource -n openshift-marketplace`.

#### serverless_channel

Subscription channel for the OpenShift Serverless Operator — a valid Serverless operator channel, for example `stable` or `stable-1.28`.

- **Optional**
- Environment Variable: `SERVERLESS_CHANNEL`
- Default: `stable`

Determines the Serverless version installed and which automatic updates are received. Use the default `stable` channel for production; it provides the latest stable release with automatic updates. Override only for specific version requirements.

### Service Mesh Operator

#### service_mesh_channel

Subscription channel for the Red Hat OpenShift Service Mesh Operator — a valid Service Mesh operator channel, for example `stable` or `stable-2.3`.

- **Optional**
- Environment Variable: `SERVICEMESH_CHANNEL`
- Default: `stable`

Determines the Service Mesh version installed and which automatic updates are received. Service Mesh is required for RHOAI model serving and networking. Use the default `stable` channel for production; override only for specific version requirements.

#### service_mesh_catalog_source

Catalog source for the Red Hat OpenShift Service Mesh Operator — a valid CatalogSource name, for example `redhat-operators` or a custom catalog.

- **Optional**
- Environment Variable: `SERVICEMESH_CATALOG_SOURCE`
- Default: `redhat-operators`

Determines the source of the Service Mesh operator; an incorrect catalog will prevent operator installation. Use the default for standard deployments and override for custom or mirrored catalogs in air-gapped environments. Verify the catalog exists with `oc get catalogsource -n openshift-marketplace`.

### Authorino Operator

#### authorino_catalog_source

Catalog source for the Authorino Operator — a valid CatalogSource name, for example `community-operators` or a custom catalog.

- **Optional**
- Environment Variable: `AUTHORINO_CATALOG_SOURCE`
- Default: `community-operators`

Determines the source of the Authorino operator, which provides authorization for RHOAI model serving; an incorrect catalog will prevent operator installation. Authorino is available in the `community-operators` catalog by default — override for custom or mirrored catalogs in air-gapped environments.

## Example Playbook

```yaml
- hosts: localhost
  vars:
    # Add required variables here
  roles:
    - ibm.mas_devops.aiservice_rhoai
```

## License

EPL-2.0
