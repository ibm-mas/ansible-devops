# suite_rbac

This role applies Role-Based Access Control (RBAC) resources for MAS operators based on the selected permission mode.

## Role Variables

### mas_instance_id
Unique identifier for the MAS installation.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies the specific MAS instance for which RBAC resources will be created. This ID is used to generate unique RBAC resource names and bind them to the correct operator ServiceAccounts.

**When to use**:
- Always required when applying RBAC for MAS operators
- Must match the instance ID used during MAS installation
- Used to target the correct operator namespaces (e.g., `mas-{mas_instance_id}-core`)

**Valid values**: Lowercase alphanumeric string, 3-12 characters, starting with a letter (e.g., `prod`, `dev01`, `mastest`)

**Impact**: This ID is embedded in all RBAC resource names (Roles, RoleBindings, ClusterRoles, ClusterRoleBindings) to ensure uniqueness and proper binding to operator ServiceAccounts.

**Related variables**: Works with `mas_permission_mode` to determine which RBAC resources are applied.

### mas_permission_mode
Specifies the permission mode for MAS operator RBAC configuration.

- **Optional**
- Environment Variable: `MAS_PERMISSION_MODE`
- Default: `cluster`

**Purpose**: Controls the scope and type of permissions granted to MAS operators.

**When to use**:
- Use `cluster` (default) for standard installations where operators need cluster-wide visibility
- Use `nonEssential` for restricted environments where cluster-admin privileges are not available
- Use `essential` when operators should manage their own essential permissions only

**Valid values**:
- `cluster` - Apply ClusterRoles for cluster-wide permissions (default, recommended for most installations)
- `nonEssential` - Apply namespace-scoped Roles only, no ClusterRoles (for restricted environments)
- `essential` - Skip RBAC application; operators will apply their own essential Roles (minimal permissions)

**Impact**: 
- `cluster` mode: Operators can discover and manage resources across the cluster (e.g., CRDs, other namespaces)
- `nonEssential` mode: Operators are restricted to their own namespaces and explicitly granted external namespaces (e.g., cert-manager)
- `essential` mode: Operators receive only the minimum permissions needed for basic functionality;

**Related variables**: 
- Requires `mas_instance_id` to generate proper RBAC resource names
- Works with `mas_channel` to determine the correct RBAC version to apply

**Note**: Changing permission mode after installation may require operator restarts to pick up new permissions. The `nonEssential` mode may limit certain operator features that require cluster-wide visibility.

### mas_channel
Specifies the MAS channel version to determine which RBAC files to apply.

- **Optional**
- Environment Variable: `MAS_CHANNEL`
- Default: None (will use latest available RBAC version)

**Purpose**: Determines which version of RBAC files to apply based on the MAS release channel. Different MAS versions may have different RBAC requirements, so this ensures the correct permissions are granted.

**When to use**:
- Set to match your MAS installation channel (e.g., `9.2.x`, `9.3.x`)
- Leave unset to automatically use the latest available RBAC version
- Must match the channel used in `suite_install` role

**Valid values**: MAS channel format (e.g., `9.2.x`, `9.3.x`, `9.4.x`)

**Impact**: The role extracts the major.minor version (e.g., `9.2` from `9.2.x`) and applies RBAC files from the corresponding version directory. Using mismatched versions may result in missing or incorrect permissions.

**Related variables**: Should match the `mas_channel` used in `suite_install` role.

## Role Behavior

### Operator Discovery
The role automatically discovers which MAS operators are installed by scanning the RBAC files directory structure:
- Looks for operators in `/opt/app-root/rbac/operators/{version}/`
- Identifies operators with RBAC subdirectories (clusterroles, roles/essential, roles/non-essential)
- Applies RBAC only for discovered operators


### RBAC File Structure
The role expects RBAC files in the following structure:
```
/opt/app-root/rbac/operators/
├── 9.2/
│   ├── ibm-mas/
│   │   └── rbac/
│   │       ├── clusterroles/
│   │       │   ├── clusterrole-coreapi.yaml
│   │       │   └── clusterrole-entitymgr-suite.yaml
│   │       └── roles/
│   │           ├── essential/
│   │           │   └── role-cert-manager.yaml
│   │           └── non-essential/
│   │               ├── role-cert-manager-coreapi.yaml
│   │               └── role-openshift-marketplace.yaml
│   ├── ibm-mas-manage/
│   │   └── rbac/
│   │       └── ...
│   └── ...
└── 9.3/
    └── ...
```

## Example Usage

### Standard Installation (cluster mode)
```yaml
- name: Apply MAS operator RBAC
  include_role:
    name: ibm.mas_devops.suite_rbac
  vars:
    mas_instance_id: "inst1"
    mas_channel: "9.2.x"
    mas_permission_mode: "cluster"
```

### Restricted Environment (nonEssential mode)
```yaml
- name: Apply MAS operator RBAC with namespace-scoped permissions
  include_role:
    name: ibm.mas_devops.suite_rbac
  vars:
    mas_instance_id: "inst1"
    mas_channel: "9.2.x"
    mas_permission_mode: "nonEssential"
```

### Minimal Permissions (essential mode)
```yaml
- name: Skip RBAC application, let operators manage their own
  include_role:
    name: ibm.mas_devops.suite_rbac
  vars:
    mas_instance_id: "inst1"
    mas_channel: "9.2.x"
    mas_permission_mode: "essential"
```