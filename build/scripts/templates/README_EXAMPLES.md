# README Template Examples

This document provides concrete examples of how to use the README template for different types of roles in the `ibm.mas_devops` collection.

## Example 1: Simple Installation Role

```markdown
# ibm_catalogs
This role installs the IBM Maximo Operator Catalog, which is a curated Operator Catalog derived from the IBM Operator Catalog, with all content certified compatible with IBM Maximo Application Suite.

Additionally, for IBM employees only, the pre-release development operator catalog can be installed by setting both the `artifactory_username` and `artifactory_token` variables.

## Role Variables

### General Variables

#### mas_catalog_version
Version of the IBM Maximo Operator Catalog to install.

- **Optional**
- Environment Variable: `MAS_CATALOG_VERSION`
- Default Value: `v9-240625-amd64`

#### artifactory_username
Username for Artifactory access to enable installation of development catalog sources for pre-release installation.

- **Optional**
- Environment Variable: `ARTIFACTORY_USERNAME`
- Default Value: None

#### artifactory_token
API token for Artifactory access to enable installation of development catalog sources for pre-release installation.

- **Optional**
- Environment Variable: `ARTIFACTORY_TOKEN`
- Default Value: None

## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    mas_catalog_version: v9-240625-amd64
  roles:
    - ibm.mas_devops.ibm_catalogs
```

## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export MAS_CATALOG_VERSION=v9-240625-amd64
ROLE_NAME=ibm_catalogs ansible-playbook ibm.mas_devops.run_role
```

## License
EPL-2.0
```

## Example 2: Role with Prerequisites

```markdown
# aws_route53
This role creates an AWS Route53 public hosted zone in the targeted AWS Account.

For further details on how to create and configure an AWS Route53 instance, refer to [AWS Route53 documentation](https://docs.aws.amazon.com/cli/latest/reference/route53/index.html).

## Prerequisites
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) must be installed
- AWS credentials configured via `aws configure` command or by exporting `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables

## Role Variables

### General Variables

#### route53_hosted_zone_name
AWS Route53 Hosted Zone name.

- **Required**
- Environment Variable: `ROUTE53_HOSTED_ZONE_NAME`
- Default Value: None

#### route53_hosted_zone_region
AWS Route53 Hosted Zone region.

- **Optional**
- Environment Variable: `ROUTE53_HOSTED_ZONE_REGION`
- Default Value: Same value as defined in `AWS_REGION`, or if none defined, then `us-east-2`

## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    route53_hosted_zone_name: mycompany.com
    route53_hosted_zone_region: us-east-2
  roles:
    - ibm.mas_devops.aws_route53
```

## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export ROUTE53_HOSTED_ZONE_NAME=mycompany.com
export ROUTE53_HOSTED_ZONE_REGION=us-east-2
ROLE_NAME=aws_route53 ansible-playbook ibm.mas_devops.run_role
```

## License
EPL-2.0
```

## Example 3: Complex Role with Multiple Variable Categories

```markdown
# suite_install
This role installs Maximo Application Suite. It internally resolves the namespace based on the `mas_instance_id` as `mas-{mas_instance_id}-core`.

## Role Variables

### Basic Installation Variables

#### mas_catalog_source
Defines the catalog to be used to install MAS. You can set it to `ibm-operator-catalog` for both release and development installations.

- **Required**
- Environment Variable: `MAS_CATALOG_SOURCE`
- Default Value: None

#### mas_channel
Defines which channel of MAS to subscribe to.

- **Required**
- Environment Variable: `MAS_CHANNEL`
- Default Value: None

### Basic Configuration Variables

#### mas_domain
Optional domain configuration. If not provided, the role will use the default cluster subdomain.

- **Optional**
- Environment Variable: `MAS_DOMAIN`
- Default Value: None

#### mas_instance_id
Defines the instance ID to be used for MAS installation.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

#### mas_entitlement_key
API Key for entitled registry. This password will be used to create the image pull secret. Set to your IBM entitlement key when installing release or use your artifactory `apikey` for development.

- **Required**
- Environment Variable: `MAS_ENTITLEMENT_KEY`
- Default Value: None

#### mas_config_dir
Directory containing configuration files (`*.yaml` and `*.yml`) to be applied to the MAS installation. Intended for creating the various MAS custom resources to configure the suite post-install, but can be used to apply any kubernetes resource you need to customize any aspect of your cluster.

- **Optional**
- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

### Advanced Configuration Variables

#### mas_annotations
Provide a list of comma-separated key=value pairs which will be applied as annotations on all resources created. For example, to deploy your suite in non-production mode, set this to `mas.ibm.com/operationalMode=nonproduction`.

- **Optional**
- Environment Variable: `MAS_ANNOTATIONS`
- Default Value: None

#### mas_img_pull_policy
Sets `spec.settings.imagePullPolicy`, controlling the pod image pull policies in the suite (`Always`, `IfNotPresent`, `Never`). When not set, the built-in operator default image pull policy will be used.

- **Optional**
- Environment Variable: `MAS_IMG_PULL_POLICY`
- Default Value: None

#### custom_labels
Provide a list of comma-separated key=value pairs which will be applied as labels on all resources created.

- **Optional**
- Environment Variable: `CUSTOM_LABELS`
- Default Value: None

## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    mas_instance_id: inst1
    mas_catalog_source: ibm-operator-catalog
    mas_channel: 9.0.x
    mas_entitlement_key: "{{ lookup('env', 'IBM_ENTITLEMENT_KEY') }}"
  roles:
    - ibm.mas_devops.suite_install
```

## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export MAS_INSTANCE_ID=inst1
export MAS_CATALOG_SOURCE=ibm-operator-catalog
export MAS_CHANNEL=9.0.x
export MAS_ENTITLEMENT_KEY=your_key_here
ROLE_NAME=suite_install ansible-playbook ibm.mas_devops.run_role
```

## License
EPL-2.0
```

## Example 4: Role with Action-Based Behavior

```markdown
# mongodb
This role supports provisioning of MongoDB in three different providers: community, AWS DocumentDB, and IBM Cloud Database for MongoDB.

If the selected provider is `community`, then the MongoDB Community Kubernetes Operator will be configured and deployed into the specified namespace. By default, a three-member MongoDB replica set will be created. The cluster will bind six PVCs, providing persistence for the data and system logs across the three nodes.

The role will generate a YAML file containing the definition of a Secret and MongoCfg resource that can be used to configure the deployed instance as the MAS system MongoDB. This file can be directly applied using `oc apply -f $MAS_CONFIG_DIR/mongocfg-mongoce-system.yaml` or used in conjunction with the [`suite_config`](suite_config.md) role.

## Prerequisites
- To run this role with `ibm` or `aws` providers, you must have already installed the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- AWS credentials must be configured via `aws configure` command or by exporting `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables
- To run the `docdb_secret_rotate` action when the provider is `aws`, you must have already installed the [Mongo Shell](https://www.mongodb.com/docs/mongodb-shell/install/)

## Role Variables

### Common Variables

#### mas_instance_id
The instance ID of Maximo Application Suite that the MongoCfg configuration will target. If this or `mas_config_dir` are not set, then the role will not generate a MongoCfg template.

- **Optional**
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

#### mas_config_dir
Local directory to save the generated MongoCfg resource definition. This can be used to manually configure a MAS instance to connect to the MongoDB cluster, or used as an input to the [`suite_config`](suite_config.md) role. If this or `mas_instance_id` are not set, then the role will not generate a MongoCfg template.

- **Optional**
- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

#### mongodb_provider
MongoDB provider. Choose whether to use the MongoDB Community Edition Operator (`community`), IBM Cloud Database for MongoDB (`ibm`), or AWS DocumentDB (`aws`).

- **Optional**
- Environment Variable: `MONGODB_PROVIDER`
- Default Value: `community`

#### mongodb_action
Determines which action to perform with respect to MongoDB for a specified provider.

- **Optional**
- Environment Variable: `MONGODB_ACTION`
- Default Value: `install`

Each provider supports a different set of actions:
- **community**: `install`, `uninstall`, `backup`, `restore`
- **aws**: `install`, `uninstall`, `docdb_secret_rotate`, `destroy-data`
- **ibm**: `install`, `uninstall`, `backup`, `restore`, `create-mongo-service-credentials`

### Community Edition Variables

#### mongodb_namespace
The namespace where the operator and MongoDB cluster will be deployed.

- **Optional**
- Environment Variable: `MONGODB_NAMESPACE`
- Default Value: `mongoce`

#### mongodb_storage_class
The name of the storage class to configure the MongoDB operator to use for persistent storage in the MongoDB cluster. Storage class must support ReadWriteOnce (RWO) access mode.

- **Required** when `mongodb_provider=community`
- Environment Variable: `MONGODB_STORAGE_CLASS`
- Default Value: None

## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    mongodb_provider: community
    mongodb_action: install
    mongodb_namespace: mongoce
    mongodb_storage_class: ibmc-block-gold
    mas_instance_id: inst1
    mas_config_dir: /tmp/mas-config
  roles:
    - ibm.mas_devops.mongodb
```

## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export MONGODB_PROVIDER=community
export MONGODB_ACTION=install
export MONGODB_NAMESPACE=mongoce
export MONGODB_STORAGE_CLASS=ibmc-block-gold
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=/tmp/mas-config
ROLE_NAME=mongodb ansible-playbook ibm.mas_devops.run_role
```

## License
EPL-2.0
```

## Key Patterns to Follow

### 1. Title and Description
- Use role directory name as title (lowercase with underscores)
- Start with brief one-line description
- Follow with detailed explanation
- No decorative separators

### 2. Prerequisites
- Only include if there are actual prerequisites
- Use bulleted list format
- Include links to installation guides
- Be specific about configuration requirements

### 3. Variable Documentation
- Group related variables under category headings
- Use level 4 headings for each variable
- Always include Required/Optional status
- Always include Environment Variable name
- Always include Default Value (or None)
- Provide clear, actionable descriptions

### 4. Examples
- Use realistic variable values
- Show common use cases
- Keep examples concise but complete
- Use consistent formatting

### 5. Consistency
- Use standard section introductions
- Maintain heading level hierarchy
- Follow code block formatting conventions
- End with License section