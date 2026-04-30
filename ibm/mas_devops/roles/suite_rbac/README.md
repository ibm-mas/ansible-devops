# suite_rbac

This role applies CLI-managed RBAC resources for MAS 9.2+ based on the selected permission mode and the applications selected for installation.

## Role Variables

### mas_instance_id
Unique identifier for the MAS installation.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Identifies the MAS instance for which namespaces and RBAC resources will be prepared.

**When to use**:
- Always required when applying suite RBAC
- Must match the instance ID used during MAS installation
- Used when creating application namespaces such as `mas-{mas_instance_id}-manage`

**Valid values**: Lowercase alphanumeric string, 3-12 characters, starting with a letter (for example `prod`, `dev01`, `mastest`)

**Impact**:
- Used to create namespaces for selected applications except `core`
- Used by templated RBAC files that reference MAS instance specific names

### mas_permission_mode
Specifies the permission mode for CLI-managed RBAC application.

- **Required**
- Environment Variable: `MAS_PERMISSION_MODE`
- Default: cluster

**Purpose**: Controls which CLI-managed RBAC resources are applied for discovered operator entries.

**When to use**:
- Use `cluster` for standard installations where cluster-scoped RBAC should be applied
- Use `namespaced` when cluster roles are not allowed and namespace-scoped roles should be applied instead
- Use `minimal` when only operator-managed essential permissions should be used and the CLI should not apply cluster or non-essential roles

**Valid values**:
- `cluster`
- `namespaced`
- `minimal`

**Impact**:
- `cluster`: applies cluster roles where available
- `namespaced`: applies namespace-scoped non-essential roles where available
- `minimal`: skips cluster and non-essential role application
- In all modes, CLI-managed essential external roles can still be applied for external platform/operator namespaces when present

**Note**: The role validates that the supplied value is one of `cluster`, `namespaced`, or `minimal`.

### mas_channel
Specifies the MAS channel used to resolve the RBAC version directory.

- **Required**
- Environment Variable: `MAS_CHANNEL`
- Default: None

**Purpose**: Determines which versioned RBAC directory is used from the CLI image content.

**When to use**:
- Set this to the same MAS channel used during installation
- Typical values are `9.2.x`, `9.3.x`, and later supported channels

**Valid values**: MAS channel format such as `9.2.x`, `9.3.x`, `9.4.x`

**Impact**:
- The role extracts the major.minor version (for example `9.2`)
- RBAC files are discovered only from that version directory
- If the wrong channel is supplied, expected RBAC content may not be found

### mas_selected_apps
Comma-separated list of selected MAS application IDs.

- **Optional**
- Environment Variable: `MAS_SELECTED_APPS`
- Default: `core`

**Purpose**: Limits RBAC discovery and namespace creation to the applications selected by the CLI install flow.

**When to use**:
- Set automatically from the CLI install workflow
- Can be provided manually when invoking the role directly

**Valid values**: Comma-separated application IDs such as:
- `core`
- `core,manage`
- `core,manage,monitor`
- `core,aiservice`

**Impact**:
- The role discovers RBAC only for mapped MAS operators belonging to selected apps
- External platform/operator RBAC is still included when required
- Namespaces are created only for selected applications other than `core`

### rbac_files_dir
Root directory containing copied RBAC content inside the CLI image.

- **Optional**
- Default: `/opt/app-root/rbac`

**Purpose**: Defines where the role looks for versioned RBAC content copied from `pre-install`.

**Impact**:
- If this directory does not exist, the role fails before RBAC discovery
- The discovery logic expects catalog/platform grouped content under this root

## Role Behavior

### Version gating
The role only applies RBAC for MAS 9.2 and later.

- For channels below 9.2, the role logs a skip message and does nothing
- For 9.2+, the role validates inputs and continues

### RBAC discovery
The role scans the RBAC root recursively and discovers operator RBAC directories that match the resolved MAS version.

Expected structure is based on the CLI image layout, for example:

```text
/opt/app-root/rbac/
├── catalogs/
│   └── maximo-operator-catalog/
│       └── operators/
│           └── <operator>/
│               └── rbac/
│                   └── <mas_version>/
└── openshift-platform/
    └── operators/
        └── <operator>/
            └── rbac/
                └── <mas_version>/
```

For each discovered operator entry, the role records:
- operator source
- operator name
- RBAC path
- mapped MAS application ID, if applicable

### Application filtering
The role maps known MAS operators to application IDs using `operator_app_map` and filters discovered entries to:
- selected MAS applications
- external operators/platform entries required by MAS

This means:
- if `mas_selected_apps` is `core,manage`, MAS core and Manage RBAC are included
- unrelated MAS application RBAC is skipped

### Namespace creation
Before applying RBAC, the role creates namespaces for selected applications except `core`.

Example:
- `core,manage,monitor` creates:
  - `mas-<instance>-manage`
  - `mas-<instance>-monitor`

### RBAC application flow
For each discovered operator RBAC entry, the role applies RBAC in this order:

1. essential external roles
2. cluster roles in `cluster` mode
3. non-essential roles in `namespaced` mode

In `minimal` mode:
- cluster roles are not applied
- non-essential roles are not applied

### Essential external roles
The role applies CLI-managed essential roles only for external platform/operator sources when matching files exist.

File patterns:
- `role-essential-*.yaml`
- `role-essential-*.yml`

These are typically used for namespaces such as platform/operator namespaces outside MAS application namespaces.

### Cluster roles
In `cluster` mode, the role applies cluster-scoped RBAC from files discovered for the operator entry.

This preserves the full cluster-scoped behavior expected for standard installs.

### Non-essential roles
In `namespaced` mode, the role applies namespace-scoped non-essential roles from files matching:

- `role-non-essential-*.yaml`
- `role-non-essential-*.yml`

These support lifecycle and cross-namespace behaviors without using cluster roles.

### Minimal mode
In `minimal` mode, the role does not apply cluster roles or non-essential roles.

This leaves only operator-managed permissions and any CLI-managed essential external roles that may still be required.

## Operator Mapping

The role currently maps these RBAC operator names to MAS application IDs:

- `ibm-mas` -> `core`
- `ibm-aiservice` -> `aiservice`
- `ibm-mas-arcgis` -> `arcgis`
- `ibm-mas-facilities` -> `facilities`
- `ibm-mas-iot` -> `iot`
- `ibm-mas-manage` -> `manage`
- `ibm-mas-monitor` -> `monitor`
- `ibm-mas-optimizer` -> `optimizer`
- `ibm-mas-predict` -> `predict`
- `ibm-mas-visualinspection` -> `visualinspection`

Operators not found in this map are treated as external.

## Example Usage

### Standard installation
```yaml
- name: Apply MAS operator RBAC in cluster mode
  include_role:
    name: ibm.mas_devops.suite_rbac
  vars:
    mas_instance_id: "inst1"
    mas_channel: "9.2.x"
    mas_permission_mode: "cluster"
    mas_selected_apps: "core,manage"
```

### Namespaced installation
```yaml
- name: Apply namespace-scoped RBAC for selected MAS applications
  include_role:
    name: ibm.mas_devops.suite_rbac
  vars:
    mas_instance_id: "inst1"
    mas_channel: "9.2.x"
    mas_permission_mode: "namespaced"
    mas_selected_apps: "core,manage,monitor"
```

### Minimal installation
```yaml
- name: Apply only minimal CLI-managed RBAC behavior
  include_role:
    name: ibm.mas_devops.suite_rbac
  vars:
    mas_instance_id: "inst1"
    mas_channel: "9.2.x"
    mas_permission_mode: "minimal"
    mas_selected_apps: "core,manage"
```