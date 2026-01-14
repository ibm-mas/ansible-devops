# ibm_catalogs
This role installs the **IBM Maximo Operator Catalog**, which is a curated Operator Catalog derived from the **IBM Operator Catalog**, with all content certified compatible with IBM Maximo Application Suite:

Additional, for IBM employees only, the pre-release development operator catalog can be installed, this is achieved by setting both the `artifactory_username` and `artifactory_token` variables.


## Role Variables

### General Variables

#### mas_catalog_version
Version of the IBM Maximo Operator Catalog to install.

- **Optional**
- Environment Variable: `MAS_CATALOG_VERSION`
- Default Value: `@@MAS_LATEST_CATALOG@@` (latest stable version)

**Purpose**: Specifies which version of the IBM Maximo Operator Catalog to install. The catalog provides certified operators compatible with MAS, including MAS Core, applications, and dependencies.

**When to use**:
- Leave as default to install the latest stable catalog version (recommended)
- Set explicitly when you need a specific catalog version
- Set to match your MAS version requirements
- Use specific version for reproducible deployments

**Valid values**: Valid catalog version string (e.g., `v8-240625-amd64`, `v9-250115-amd64`)

**Impact**: Determines which operator versions are available for installation. The catalog version must be compatible with your target MAS version. Using an incompatible catalog version may prevent MAS installation or upgrades.

**Related variables**: The catalog version affects which MAS and application versions can be installed.

**Note**: The default value is automatically updated to the latest stable catalog version. For production deployments, consider pinning to a specific version for consistency and reproducibility.

### Development Variables

#### artifactory_username
Artifactory username for accessing pre-release development catalogs (IBM employees only).

- **Optional**
- Environment Variable: `ARTIFACTORY_USERNAME`
- Default Value: None

**Purpose**: Provides authentication to IBM Artifactory for installing development catalog sources containing pre-release MAS operators. This enables testing of upcoming MAS versions before general availability.

**When to use**:
- Only for IBM employees with Artifactory access
- Only for development/testing of pre-release MAS versions
- Must be set together with `artifactory_token`
- Never use in production environments

**Valid values**: Valid IBM Artifactory username

**Impact**: When set with `artifactory_token`, enables installation of development catalog sources. Without both credentials, only production catalogs are available.

**Related variables**:
- `artifactory_token`: Required together with this username
- Both must be set to enable development catalog access

**Note**: **IBM EMPLOYEES ONLY** - This is for pre-release testing only. Never use development catalogs in production. Keep credentials secure and do not commit to source control.

#### artifactory_token
Artifactory API token for accessing pre-release development catalogs (IBM employees only).

- **Optional**
- Environment Variable: `ARTIFACTORY_TOKEN`
- Default Value: None

**Purpose**: Provides API token authentication to IBM Artifactory for installing development catalog sources containing pre-release MAS operators. This enables testing of upcoming MAS versions before general availability.

**When to use**:
- Only for IBM employees with Artifactory access
- Only for development/testing of pre-release MAS versions
- Must be set together with `artifactory_username`
- Never use in production environments

**Valid values**: Valid IBM Artifactory API token string

**Impact**: When set with `artifactory_username`, enables installation of development catalog sources. Without both credentials, only production catalogs are available.

**Related variables**:
- `artifactory_username`: Required together with this token
- Both must be set to enable development catalog access

**Note**: **IBM EMPLOYEES ONLY** - This is for pre-release testing only. Never use development catalogs in production. Keep this token secure and do not commit to source control. Generate tokens from IBM Artifactory.

## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  roles:
    - ibm.mas_devops.ibm_catalogs
```


## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
ROLE_NAME=ibm_catalogs ansible-playbook ibm.mas_devops.run_role
```


## License
EPL-2.0
