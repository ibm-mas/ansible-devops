# cis

This role provides support for Configuring IBM Cloud Internet Services. During CIS provisioning it performs four tasks in the given order:

1. Provision CIS Instance in customer account
2. Add customer domain to customer's CIS Instance
3. Configure Domain settings in customer CIS Instance
4. Add DNS Records of type `NS` for customer's Domain nameservers to Master CIS Account

During CIS Instance deprovisioning the role will perform the following tasks:

1. Delete DNS Record from Master Account
2. Delete Domain from Customer Account
3. Delete Customer CIS Instance

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`cis_action`](#cis_action) | No | `provision` |
| [`cis_plan`](#cis_plan) | No | `standard` |
| [`ibmcloud_region`](#ibmcloud_region) | No | `us-east` |
| [`ibmcloud_apikey`](#ibmcloud_apikey) | Yes | None |
| [`ibmcloud_resourcegroup`](#ibmcloud_resourcegroup) | No | `Default` |
| [`master_ibmcloud_api_key`](#master_ibmcloud_api_key) | Yes | None |
| [`master_cis_resource_group`](#master_cis_resource_group) | No | `manager` |
| [`master_cis_resource_name`](#master_cis_resource_name) | No | `<mas_instance_id>-cis` |
| [`master_cis_base_domain`](#master_cis_base_domain) | Yes | None |
| [`mas_instance_id`](#mas_instance_id) | Yes | None |
| [`cluster_name`](#cluster_name) | Yes | None |
| [`mas_config_dir`](#mas_config_dir) | Yes | None |

### CIS Instance

#### cis_action

Action to perform on the Cloud Internet Services instance — `provision` creates the CIS instance, adds the domain, configures domain settings, and adds NS records to the master account; `deprovision` deletes the DNS records from the master account, removes the domain, and deletes the CIS instance.

- **Optional**
- Environment Variable: `CIS_ACTION`
- Default: `provision`

Use `provision` (default) when setting up DNS and CDN services for a new MAS deployment, and `deprovision` when cleaning up CIS resources after MAS uninstallation. Provisioning creates a multi-account DNS delegation architecture and requires coordination between the customer and master IBM Cloud accounts; failed provisioning may require manual cleanup in the IBM Cloud console.

!!! warning
    Deprovisioning permanently removes all CIS resources and DNS records that may still be in use (irreversible) — verify before proceeding, and always deprovision before removing the OpenShift cluster.

#### cis_plan

IBM Cloud Internet Services plan tier, which determines available features (WAF rules, rate limiting, page rules, load balancing), performance limits, SLA guarantees, and pricing — `standard` (basic CDN, DDoS protection, and DNS, sufficient for most development and test environments) or `enterprise` (advanced security, performance, and support features, recommended for production deployments with high traffic). Plan availability and features may vary by region.

- **Optional**
- Environment Variable: `CIS_PLAN`
- Default: `standard`

Only applies when `cis_action` is `provision`. The plan cannot be changed after provisioning (it requires recreation), so review IBM Cloud CIS pricing before selecting a plan.

#### ibmcloud_region

IBM Cloud region targeted by the CIS operations.

- **Optional**
- Environment Variable: `IBMCLOUD_REGION`
- Default: `us-east`

### Customer Account

#### ibmcloud_apikey

The IBM Cloud API key (44-character alphanumeric string) for the customer account where CIS will be provisioned. Must have Editor or Administrator role on the CIS service and access to the specified resource group.

- **Required**
- Environment Variable: `IBMCLOUD_APIKEY`
- Default: None

Always required for both provisioning and deprovisioning. Authenticates all operations in the customer's account, which owns the CIS instance and incurs charges. Store API keys securely using environment variables or secrets management, never commit them to version control, and consider using service IDs with restricted permissions.

#### ibmcloud_resourcegroup

The IBM Cloud resource group (case-sensitive, must exist before provisioning) in the customer account that will own the CIS instance — for example `Default`, `Production`, `Development`, or `MAS-Resources`.

- **Optional**
- Environment Variable: `IBMCLOUD_RESOURCEGROUP`
- Default: `Default`

The resource group determines billing and cost allocation and controls IAM access policies; it cannot be changed after CIS instance creation. Ensure `ibmcloud_apikey` has access to the specified resource group, and use consistent resource groups across all MAS-related services.

### Master Account

#### master_ibmcloud_api_key

The IBM Cloud API key for the master account that hosts the base domain. This is a separate key from `ibmcloud_apikey`, typically provided by the organization managing the master domain, and needs only DNS record management permissions in the master CIS instance (not full CIS access).

- **Required**
- Environment Variable: `MASTER_IBMCLOUD_APIKEY`
- Default: None

Used to create the NS (nameserver) records in the master CIS instance that delegate the subdomain to the customer's CIS nameservers — without it the customer's domain will not be resolvable. Store it securely, since it has access to the master DNS infrastructure.

#### master_cis_resource_group

The resource group (case-sensitive) in the master account where the master CIS instance is located — must match the actual resource group in which `master_cis_resource_name` exists.

- **Optional**
- Environment Variable: `MASTER_CIS_RESOURCE_GROUP`
- Default: `manager`

Used to locate the master CIS instance for NS record creation; an incorrect value causes DNS delegation to fail. The default `manager` is commonly used in IBM MAS deployments — verify the correct resource group with the master account administrator, and ensure `master_ibmcloud_api_key` has access to it.

#### master_cis_resource_name

The name of the master CIS instance in the master account that hosts the base domain and receives the NS records for subdomain delegation — must match an existing CIS instance (case-sensitive) in `master_cis_resource_group`.

- **Optional**
- Environment Variable: `MASTER_CIS_RESOURCE_NAME`
- Default: `<mas_instance_id>-cis`

The instance must already exist in the master account; this role only uses it for NS record management, it does not create it. If the master CIS instance uses a different naming convention than the default, verify the correct instance name with the master account administrator.

#### master_cis_base_domain

The base domain hosted in the master CIS instance under which the customer's subdomain will be delegated — for example `mas.ibm.com`, `maximo.example.com`, or `apps.company.com`, without protocol (http/https) or trailing slashes.

- **Required**
- Environment Variable: `MASTER_CIS_BASE_DOMAIN`
- Default: None

The domain must already exist and be active in the master CIS instance; verify DNS propagation of the base domain before provisioning. The full customer domain will be `<cluster_name>.<mas_instance_id>.<master_cis_base_domain>` — for example `cluster1.prod.mas.ibm.com` when the base domain is `mas.ibm.com`.

### Domain Naming and MAS Configuration

#### mas_instance_id

The MAS instance identifier used to generate the CIS service name and as part of the domain name structure — an alphanumeric string, typically 3-12 characters, lowercase recommended for DNS compatibility (for example `prod`, `dev`, `test`, or `masinst1`).

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

Generates the default CIS instance name (`<mas_instance_id>-cis`) and forms the second part of the domain: `<cluster_name>.<mas_instance_id>.<base_domain>`. Use the same `mas_instance_id` across all MAS DevOps roles for consistency; it cannot be changed after provisioning without recreating resources.

#### cluster_name

The OpenShift cluster name used as the first component of the domain name — alphanumeric with hyphens, lowercase recommended for DNS compatibility (for example `ocp-prod`, `rosa-cluster`, `roks-dev`, or `cluster1`), and unique within the MAS instance.

- **Required**
- Environment Variable: `CLUSTER_NAME`
- Default: None

Multiple clusters can share the same `mas_instance_id` with different `cluster_name` values — for example `cluster_name=rosa-prod`, `mas_instance_id=mas01`, base domain `ibm.com` yields `rosa-prod.mas01.ibm.com`.

#### mas_config_dir

Local directory where the role saves the CIS instance details as Kubernetes ConfigMap YAML files for use by other MAS components — for example `~/masconfig` or `/opt/mas/config`. The directory is created if it doesn't exist and must be writable by the user running the playbook; an absolute path is recommended.

- **Required**
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

This directory is the central location for all MAS configuration artifacts and should be the same across all MAS DevOps roles. The ConfigMaps generated here are applied to the OpenShift cluster during MAS installation, so back the directory up.

## Example Playbook

Create CIS Instance along with save Instance details in MAS_CONFIG_DIR path as ConfigMap

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cis_action: provision
    mas_instance_id: masinst1
    mas_config_dir: ~/masconfig
    ibmcloud_apikey: "****"
    master_ibmcloud_api_key: "******"
    cluster_name: "test"
  roles:
    - ibm.mas_devops.cis
```

## License

EPL-2.0
