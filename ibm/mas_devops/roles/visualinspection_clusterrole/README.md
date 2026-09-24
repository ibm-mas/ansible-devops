# visualinspection_clusterrole
This role creates the cluster-scoped RBAC resources required by the Maximo Visual Inspection (MVI) operator before it is installed via OLM. Specifically, it applies a `ClusterRole` that grants the MVI operator ServiceAccount permission to use the custom `ibm-mas-visualinspection-scc` SecurityContextConstraints and to list nodes and pods cluster-wide. It then binds that ClusterRole to the operator ServiceAccount via a `ClusterRoleBinding`.

These resources are managed outside the OLM operator bundle (i.e. not in the CSV `clusterPermissions`) so that the operator subscription does not require elevated cluster-admin privileges at install time.

## Prerequisites
- OpenShift cluster with `oc` CLI access
- Cluster administrator access (ClusterRole and ClusterRoleBinding are cluster-scoped resources)
- The `ibm-mas-visualinspection-scc` SecurityContextConstraints must already exist on the cluster (applied by the MVI CASE bundle or a prior Ansible step)
- `MAS_INSTANCE_ID` environment variable must be set

## Role Variables

### mas_instance_id
The MAS instance identifier used to derive the MVI application namespace (`mas-<instance_id>-visualinspection`).

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

**Purpose**: Used to construct `mas_app_namespace`, which is the namespace where the MVI operator ServiceAccount lives and where the ClusterRoleBinding subject is scoped.

**Valid values**: Lowercase alphanumeric string matching the MAS instance ID (e.g. `dev910a`, `prod1`)

**Impact**: Determines which namespace's ServiceAccount is granted the ClusterRole. Each MAS instance gets its own ClusterRoleBinding pointing to its own namespace.

---

### mvi_setup_clusterrole
Controls whether the ClusterRole and ClusterRoleBinding are created (`true`) or deleted (`false`).

- **Optional**
- Environment Variable: `MVI_SETUP_CLUSTERROLE`
- Default: `true`

**Purpose**: Acts as an on/off flag so the role can serve both install-time (create) and teardown (delete) pipelines without needing a separate role.

**When to use**:
- Leave as `true` (default) during installation — the RBAC resources will be created or updated idempotently.
- Set to `false` in a post-uninstall pipeline to clean up the cluster-scoped resources that OLM does not manage.

**Valid values**: `true` / `false`

**Impact**:
- `true` → applies `clusterrole.yml.j2` and `clusterrole_binding.yml.j2` to the cluster
- `false` → deletes `ibm-mas-visualinspection-clusterrole` and `ibm-mas-visualinspection-clusterrolebinding` from the cluster

**Notes**:
- Because ClusterRole and ClusterRoleBinding are cluster-scoped, they are not automatically removed when a namespace or OLM subscription is deleted. This flag provides an explicit teardown path.
- The default value of `true` means this role is safe to include unconditionally in install playbooks.

---

## Resources managed

| Kind | Name |
|---|---|
| `ClusterRole` | `ibm-mas-visualinspection-clusterrole` |
| `ClusterRoleBinding` | `ibm-mas-visualinspection-clusterrolebinding` |

The ClusterRole grants:
- `use` on `securitycontextconstraints/ibm-mas-visualinspection-scc`
- `list` on `nodes` and `pods`

The ClusterRoleBinding binds the ClusterRole to `system:serviceaccount:mas-<instance_id>-visualinspection:ibm-mas-visualinspection-operator`.

---

## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  vars:
    mas_instance_id: dev910a
    mvi_setup_clusterrole: true
  roles:
    - ibm.mas_devops.visualinspection_clusterrole
```

## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export MAS_INSTANCE_ID=dev910a
export MVI_SETUP_CLUSTERROLE=true
ROLE_NAME=visualinspection_clusterrole ansible-playbook ibm.mas_devops.run_role
```

To tear down the RBAC resources after uninstalling MVI:

```bash
export MAS_INSTANCE_ID=dev910a
export MVI_SETUP_CLUSTERROLE=false
ROLE_NAME=visualinspection_clusterrole ansible-playbook ibm.mas_devops.run_role
```

## License
EPL-2.0
