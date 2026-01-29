**Role Name**
=========

**cp4d_uninstall**

This role provides a **controlled, safe, and repeatable uninstallation of IBM Cloud Pak for Data (CP4D)**
from an OpenShift cluster.

It is designed to handle:
- normal CP4D uninstalls
- partially completed or failed uninstalls
- clusters where CP4D namespaces are stuck in `Terminating`
- custom resources blocked by finalizers after operator removal

The role follows a **safe-first, force-last** execution model and includes
an explicit confirmation step to prevent accidental uninstall.

**Scope and Intent**
----------------

This role is **only** intended for uninstalling CP4D.

It is **not** intended to:
- uninstall other Cloud Paks
- clean shared cluster services
- remove non-CP4D workloads running in unrelated namespaces

All actions are scoped strictly to CP4D namespaces and CP4D-related resources.

**Safety Model**
------------

The role enforces safety at multiple levels:
1. **CP4D presence detection**
   - The role first checks whether CP4D namespaces exist.
   - If CP4D is not detected, the role exits without making changes.

2. **Interactive confirmation**
   - If CP4D is detected, the user is prompted to confirm uninstall.
   - Default behaviour is **safe exit** (no uninstall).

3. **Safe-to-force execution order**
   - Operator and workload cleanup first
   - Finalizer removal only when required
   - Namespace deletion as the final step

4. **Automation-friendly override**
   - Interactive confirmation can be skipped explicitly for CI/CD.

**Uninstall Strategy**
------------------

The uninstall process is intentionally staged:

1. Stop operator reconciliation (OLM objects, CatalogSources)
2. Remove CP4D workloads (Deployments, StatefulSets, Jobs)
3. Clean known operator-scoped custom resources
4. Perform a last-resort finalizer cleanup for any remaining resources
5. Delete CP4D-related CRDs actually used by CP4D
6. Delete CP4D namespaces

This ordering ensures:
- no resources are recreated during uninstall
- finalizers do not block namespace deletion
- partial failures can be re-run safely

**Finalizer Handling**
------------------

Finalizers are handled carefully and intentionally:

- Known CP4D operator CRs are cleaned explicitly first
- A generic finalizer cleanup step acts as a **last-resort safety net**
- Finalizers are only removed for resources still present in CP4D namespaces
- This logic exists to handle broken or abandoned controllers

This approach matches real-world CP4D support scenarios.

**Role Variables**
--------------

### Variables in `defaults/main.yml`

```yaml
cp4d_namespaces:
  - ibm-cpd
  - ibm-cpd-operators
