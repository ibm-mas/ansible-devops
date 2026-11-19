# aiservice_tenant

This role provides support to install and configure AI Broker:

* Install AI Broker api application
* Create, delete AI Broker tenant
* Create, delete AI Broker API Key
* Create, delete AWS S3 API Key
* Create, delete WatsonX AI API Key

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`tenant_action`](#tenant_action) | No | `install` |
| [`aiservice_tenant_id`](#aiservice_tenant_id) | No | `user` |
| [`aiservice_watsonx_action`](#aiservice_watsonx_action) | No | `install` |
| [`aiservice_watsonxai_apikey`](#aiservice_watsonxai_apikey) | Conditional | None |
| [`aiservice_watsonxai_url`](#aiservice_watsonxai_url) | Conditional | None |
| [`aiservice_watsonxai_project_id`](#aiservice_watsonxai_project_id) | Conditional | None |
| [`tenant_entitlement_type`](#tenant_entitlement_type) | No | `standard` |
| [`tenant_entitlement_start_date`](#tenant_entitlement_start_date) | No | None |
| [`tenant_entitlement_end_date`](#tenant_entitlement_end_date) | No | None |
| [`aiservice_tenant_scheduling_config_file`](#aiservice_tenant_scheduling_config_file) | No | None |
| [`aiservice_tenant_operator_config_file`](#aiservice_tenant_operator_config_file) | No | None |

The WatsonX AI variables are only required when `aiservice_watsonx_action` is `install`.

### Tenant Management

#### tenant_action

Action to perform on the AI Broker tenant — `install` (create or configure the tenant) or `remove` (delete the tenant).

- **Optional**
- Environment Variable: `TENANT_ACTION`
- Default: `install`

!!! warning
    The `remove` action permanently deletes the tenant and all associated data.

#### aiservice_tenant_id

Unique identifier for the AI Broker tenant — an alphanumeric string such as `user`, `team1`, or `prod-tenant`.

- **Optional**
- Environment Variable: `AISERVICE_TENANT_ID`
- Default: `user`

Identifies the tenant for resource isolation and management in multi-tenant deployments, and is combined with `aiservice_instance_id` to form the tenant name. The default `user` is suitable for single-tenant deployments; use descriptive names for multi-tenant environments.

### WatsonX AI Integration

#### aiservice_watsonx_action

Action to perform on the WatsonX AI integration — `install` (configure WatsonX AI credentials for the tenant) or `remove` (delete the WatsonX AI integration).

- **Optional**
- Environment Variable: `AISERVICE_WATSONX_ACTION`
- Default: `install`

WatsonX AI integration enables AI model access through the IBM watsonx.ai platform.

#### aiservice_watsonxai_apikey

WatsonX AI API key for authentication, obtained from the IBM Cloud console under the watsonx.ai service credentials.

- **Required** when `aiservice_watsonx_action` is `install`
- Environment Variable: `AISERVICE_WATSONXAI_APIKEY`
- Default: None

Enables AI Broker to authenticate with WatsonX AI services; an invalid key will prevent AI model access. The API key is stored as a Kubernetes secret — store it securely and never commit it to version control.

#### aiservice_watsonxai_url

WatsonX AI service endpoint URL for model inference and management — a valid HTTPS URL such as `https://us-south.ml.cloud.ibm.com` or `https://eu-de.ml.cloud.ibm.com`.

- **Required** when `aiservice_watsonx_action` is `install`
- Environment Variable: `AISERVICE_WATSONXAI_URL`
- Default: None

Determines which WatsonX AI region/endpoint the AI Broker connects to; the URL varies by IBM Cloud region — verify it in the IBM Cloud watsonx.ai service details.

#### aiservice_watsonxai_project_id

WatsonX AI project identifier (UUID format, e.g. `12345678-1234-1234-1234-123456789012`) containing the AI models and resources to be accessed.

- **Required** when `aiservice_watsonx_action` is `install`
- Environment Variable: `AISERVICE_WATSONXAI_PROJECT_ID`
- Default: None

Find the project ID in the IBM Cloud watsonx.ai project settings; the project must exist before configuring AI Broker.

### Entitlement Configuration

Configure the tenant's entitlement to the AI Service for licensing and access control.

#### tenant_entitlement_type

Type of entitlement for the tenant — the valid values depend on the AI Service deployment configuration.

- **Optional**
- Environment Variable: `AISERVICE_TENANT_ENTITLEMENT_TYPE`
- Default: `standard`

Determines which AI Service features and capacity the tenant can access; entitlement types are defined by the AI Service deployment configuration.

#### tenant_entitlement_start_date

Start date for the tenant entitlement period, as a date string in `YYYY-MM-DD` format (e.g. `2024-01-01`).

- **Optional**
- Environment Variable: `AISERVICE_TENANT_ENTITLEMENT_START_DATE`
- Default: None

Defines when the tenant's entitlement becomes active — the tenant cannot access the AI Service before this date. Ensure the date is valid and in the past or present for immediate access.

#### tenant_entitlement_end_date

End date for the tenant entitlement period, as a date string in `YYYY-MM-DD` format (e.g. `2024-12-31`).

- **Optional**
- Environment Variable: `AISERVICE_TENANT_ENTITLEMENT_END_DATE`
- Default: None

Defines when the tenant's entitlement expires — the tenant cannot access the AI Service after this date. It should be after `tenant_entitlement_start_date`; plan for entitlement renewal before expiration.

### Scheduling and Operator Configuration

#### aiservice_tenant_scheduling_config_file

Path to a YAML file containing scheduling configuration (tolerations and nodeSelector) for the tenant's pipeline and predictor workloads.

- **Optional**
- Environment Variable: `AISERVICE_TENANT_SCHEDULING_CONFIG_FILE`
- Default: None

Use it to schedule AI workloads on dedicated nodes with specific taints, direct pipeline and predictor pods to nodes with specific labels (e.g. GPU-enabled nodes for inference workloads), or isolate AI workloads from other cluster workloads. The configuration is applied to the AIServiceTenant CR under `spec.settings.scheduling`; empty objects (`pipeline: {}` or `predictor: {}`) are allowed and will be ignored. Improper configuration may prevent pods from scheduling.

The YAML file must be valid YAML and contain `pipeline` and/or `predictor` objects. Each object can have `tolerations` (a non-empty list of Kubernetes tolerations with required fields `key`, `operator`, and `effect`, plus optional `value` and `tolerationSeconds`) and `nodeSelector` (a non-empty dictionary of node label key-value pairs) — at least one of the two must be defined for each non-empty object:

```yaml
---
# Pipeline scheduling configuration
pipeline:
  tolerations:
    - key: "aiservice-pipeline"
      operator: "Equal"
      value: "true"
      effect: "NoSchedule"
  nodeSelector:
    workload-type: "aiservice-pipeline"
    node-role: "compute"

# Predictor scheduling configuration
predictor:
  tolerations:
    - key: "aiservice-predictor"
      operator: "Equal"
      value: "true"
      effect: "NoSchedule"
    - key: "gpu"
      operator: "Equal"
      value: "true"
      effect: "NoSchedule"
  nodeSelector:
    workload-type: "aiservice-predictor"
    accelerator: "gpu"
```

Common use cases include GPU node scheduling (e.g. `nodeSelector: {accelerator: nvidia-gpu}` with a toleration for the `nvidia.com/gpu` taint), dedicated node pools (e.g. `node-pool: ai-workloads` with a `dedicated=ai:NoSchedule` toleration), and zone-based scheduling (e.g. `topology.kubernetes.io/zone: us-east-1a`).

#### aiservice_tenant_operator_config_file

Path to a YAML file containing the tenant operator customization settings — its content is added to the "config" field in the operator Subscription.

- **Optional**
- Environment Variable: `AISERVICE_TENANT_OPERATOR_CONFIG_FILE`
- Default: None

Set when customizing the tenant operator, such as adjusting CPU/memory requests/limits. Invalid configuration will prevent the tenant operator from installing.

## Example Playbook

```yaml
- hosts: localhost
  vars:
    # Add required variables here
  roles:
    - ibm.mas_devops.aiservice_tenant
```

## License

EPL-2.0
