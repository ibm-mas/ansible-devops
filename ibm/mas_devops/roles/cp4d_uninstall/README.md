**Role Name**
===========

**cp4d_uninstall**

This role provides a **force cleanup uninstall** of IBM Cloud Pak for Data (CP4D) from a cluster.

It is designed to handle:
   - complete removal of a CP4D installation
   - partially completed or failed uninstalls
   - clusters where CP4D namespaces are stuck in Terminating
   - custom resources blocked by finalizers after operator removal
   - recovery scenarios where operator controllers are no longer reconciling

This role performs a full teardown of the CP4D namespaces and all CP4D-related services.

It is **not intended for selective or service-level uninstall** (for example removing WSL, WML, or Spark while keeping the rest of CP4D operational).

The role follows a controlled execution model and requires explicit confirmation before performing destructive operations.

**Scope and Intent**
----------------

This role is intended to remove the entire CP4D installation, including all services deployed within:
   - ibm-cpd
   - ibm-cpd-operators

It is not designed to:
   - selectively uninstall individual CP4D services
   - uninstall other Cloud Paks
   - clean shared cluster services
   - remove non-CP4D workloads running in unrelated namespaces

All actions are scoped strictly to CP4D namespaces and CP4D-related resources.

**Safety Model**
------------

The role enforces safety at multiple levels:
1. CP4D presence detection
   - The role first checks whether CP4D namespaces exist.
   - If CP4D is not detected, the role exits without making changes.

2. Explicit confirmation required
   - Uninstall proceeds only when explicitly confirmed.
   - If confirmation is not provided, the role exits safely without performing any destructive actions.

3. Controlled execution order
   - Operator reconciliation sources are removed first
   - Workloads are cleaned before namespace deletion
   - Finalizer removal is used only when required
   - Namespace deletion is performed as the final step

4. Automation-friendly execution
   - Confirmation can be provided via environment variable for CI/CD usage.

**Uninstall Strategy**
------------------

The uninstall process is intentionally staged:
1. Stop operator reconciliation (OLM objects, CatalogSources)
2. Remove CP4D workloads (Deployments, StatefulSets, Jobs)
3. Clean operator-scoped custom resources
4. Perform finalizer cleanup for remaining blocking resources
5. Delete CP4D-related CRDs actively used by CP4D
6. Delete CP4D namespaces

This ordering ensures:
- resources are not recreated during uninstall
- finalizers do not permanently block namespace deletion
- broken installations can be cleaned successfully
- the role can be safely re-run in recovery scenarios

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
