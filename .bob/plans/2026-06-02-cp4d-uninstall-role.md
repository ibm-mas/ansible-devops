# CP4D Uninstall Role Implementation Plan

## Objective
Create a new Ansible role `cp4d_uninstall` that cleanly uninstalls Cloud Pak for Data (CP4D) and all its services from an OpenShift cluster, reversing the installation performed by the `cp4d` and `cp4d_service` roles.

## Critical Rules
- Follow the reverse order of installation: services first, then platform, then prerequisites
- Ensure idempotency - role must be safe to run multiple times
- Preserve data by default - require explicit flags for destructive operations (PVC deletion)
- Validate namespace existence before attempting deletions
- Handle missing resources gracefully (already uninstalled scenarios)
- **Follow the pattern from `suite_app_uninstall` role** - similar structure and approach
- Use proper Ansible error handling and retries for async operations
- Document all variables with clear descriptions in README.md
- Use `kubernetes.core.k8s` with `state: absent` and `wait: true` for deletions
- Include wait conditions with retries after deletions

## Execution Plan

### Phase 1: Analysis & Design
**Objective:** Understand CP4D installation components and design uninstall sequence

- [x] **1.1** Analyze CP4D installation roles
  - [x] Review [`cp4d/tasks/main.yml`](../../ibm/mas_devops/roles/cp4d/tasks/main.yml)
  - [x] Review [`cp4d_service/tasks/main.yml`](../../ibm/mas_devops/roles/cp4d_service/tasks/main.yml)
  - [x] Review [`cp4d/tasks/install-cp4d.yml`](../../ibm/mas_devops/roles/cp4d/tasks/install-cp4d.yml)
  - [x] Review [`cp4d_service/tasks/install.yml`](../../ibm/mas_devops/roles/cp4d_service/tasks/install.yml)
  - [x] Review [`suite_app_uninstall`](../../ibm/mas_devops/roles/suite_app_uninstall) for pattern reference

- [x] **1.2** Document CP4D component hierarchy
  - [x] **Services CRs**: `WS`, `WmlBase`, `AnalyticsEngine`, `CAService`, `CCS`, `DataRefinery`
  - [x] **Platform CRs**: `ZenService` (lite-cr), `Ibmcpd` (ibmcpd-cr)
  - [x] **Operators**: cpd-platform, service operators, ccs, datarefinery, ws-runtimes, elasticsearch/opensearch
  - [x] **Namespaces**: `ibm-cpd`, `ibm-cpd-operators`, `cs-control`, `ibm-common-services`, `ibm-licensing`
  - [x] **Catalog Sources**: `cpd-platform`, `opencloud-operators`
  - [x] **Prerequisites**: CPFS (CommonService), NamespaceScope, IBMLicensing

- [x] **1.3** Define uninstall sequence (following suite_app_uninstall pattern)
  - [x] Order: Services CRs → Platform CRs → Subscriptions → Namespaces
  - [x] Use `kubernetes.core.k8s` with `state: absent`, `wait: true`, `wait_timeout: 600`
  - [x] Add retry loops with `k8s_info` to verify deletion completion

### Phase 2: Role Structure Creation
**Objective:** Create basic role structure following Ansible best practices

- [x] **2.1** Create role directory structure
  ```
  ibm/mas_devops/roles/cp4d_uninstall/
  ├── README.md
  ├── defaults/
  │   └── main.yml
  ├── meta/
  │   └── main.yml
  └── tasks/
      ├── main.yml
      ├── uninstall-services.yml
      ├── uninstall-platform.yml
      ├── uninstall-prerequisites.yml
      ├── cleanup-catalog-sources.yml
      ├── cleanup-pvcs.yml
      └── cleanup-namespaces.yml
  ```

- [x] **2.2** Define role variables in `defaults/main.yml`
  - [x] `cpd_operators_namespace` (default: `ibm-cpd-operators`)
  - [x] `cpd_instance_namespace` (default: `ibm-cpd`)
  - [x] `cpd_cs_control_namespace` (default: `cs-control`)
  - [x] `cpd_cpfs_namespace` (default: `ibm-common-services`)
  - [x] `cpd_ibm_licensing_namespace` (default: `ibm-licensing`)
  - [x] `cpd_uninstall_delete_pvcs` (default: `false`) - destructive flag
  - [x] `cpd_uninstall_delete_namespaces` (default: `true`)
  - [x] `cpd_uninstall_delete_catalog_sources` (default: `true`)
  - [x] `cpd_uninstall_wait_timeout` (default: `600`) - seconds
  - [x] Service information dictionary with CR details

- [x] **2.3** Create `meta/main.yml` with dependencies
  - [x] Set minimum Ansible version ("2.10")
  - [x] Define role metadata (author, description, license)
  - [x] Add ansible_version_check dependency

### Phase 3: Implement Service Uninstall
**Objective:** Remove CP4D services (Watson Studio, WML, Spark, Cognos)

- [x] **3.1** Create `tasks/uninstall-services.yml`
  - [x] Detect installed services by checking CRs in `cpd_instance_namespace`
  - [x] Delete service CRs with wait conditions
  - [x] Delete CCS and DataRefinery CRs
  - [x] Wait for CR deletion to complete (finalizers)
  - [x] Delete service operators/subscriptions
  - [x] Delete dependency subscriptions (CCS, DataRefinery, WS Runtimes)
  - [x] Delete Elasticsearch/OpenSearch operators

### Phase 4: Implement Platform Uninstall
**Objective:** Remove CP4D platform (Zen, IbmCpd CR)

- [x] **4.1** Create `tasks/uninstall-platform.yml`
  - [x] Delete `ZenService` CR with wait conditions
  - [x] Handle legacy `ibmcpd` CR name
  - [x] Delete `Ibmcpd` CR with wait conditions
  - [x] Delete platform operator subscription
  - [x] Delete Zen operator subscription

### Phase 5: Implement Prerequisites Uninstall
**Objective:** Remove CPFS, NamespaceScope, Licensing

- [x] **5.1** Create `tasks/uninstall-prerequisites.yml`
  - [x] Delete IBM Licensing CR with wait conditions
  - [x] Delete IBM Licensing subscription
  - [x] Delete CommonService CR with wait conditions
  - [x] Delete CPFS subscription
  - [x] Delete NamespaceScope CR with wait conditions
  - [x] Delete NamespaceScope subscription
  - [x] Delete ODLM subscription

### Phase 6: Implement Cleanup Tasks
**Objective:** Clean up namespaces, catalog sources, and optionally PVCs

- [x] **6.1** Create `tasks/cleanup-catalog-sources.yml`
  - [x] Delete CP4D Platform catalog source
  - [x] Delete OpenCloud Operators catalog source
  - [x] Delete Zen Operator catalog source
  - [x] Delete common-service-maps ConfigMaps
  - [x] Delete olm-utils-cm ConfigMap

- [x] **6.2** Create `tasks/cleanup-pvcs.yml`
  - [x] Warning messages for destructive operation
  - [x] List all PVCs in `cpd_instance_namespace`
  - [x] Delete PVCs with wait conditions
  - [x] List all PVCs in `cpd_cpfs_namespace`
  - [x] Delete CPFS PVCs with wait conditions

- [x] **6.3** Create `tasks/cleanup-namespaces.yml`
  - [x] Delete all CP4D namespaces with wait conditions
  - [x] Handle finalizers with extended retry periods
  - [x] Use ignore_errors for optional namespaces

### Phase 7: Main Task Orchestration
**Objective:** Create main task file that orchestrates the uninstall

- [x] **7.1** Create `tasks/main.yml`
  - [x] Debug output for configuration
  - [x] Warning messages for destructive operations
  - [x] Check if CP4D is installed
  - [x] Include all uninstall task files
  - [x] Conditional execution based on installation status
  - [x] Final summary message

### Phase 8: Documentation
**Objective:** Create comprehensive README.md

- [x] **8.1** Write README.md following existing role patterns
  - [x] Role description and purpose
  - [x] Uninstall process overview
  - [x] Role variables section (all variables documented)
  - [x] Example playbooks section (4 scenarios)
  - [x] Run role playbook section
  - [x] Important notes and warnings
  - [x] Troubleshooting section
  - [x] License section

### Phase 9: Testing & Validation
**Objective:** Ensure role works correctly

- [ ] **9.1** Create test playbook
  - [ ] Create `test-cp4d-uninstall.yml` playbook
  - [ ] Test with default variables
  - [ ] Test with custom namespaces
  - [ ] Test idempotency (run twice)

- [ ] **9.2** Manual testing scenarios
  - [ ] Test uninstall with all services installed
  - [ ] Test uninstall with partial installation
  - [ ] Test uninstall when already uninstalled
  - [ ] Test with PVC deletion enabled
  - [ ] Test with namespace deletion disabled

- [ ] **9.3** Validation checks
  - [ ] Verify no orphaned resources
  - [ ] Verify no stuck finalizers
  - [ ] Verify clean cluster state after uninstall

## Validation

### Success Criteria
After running the `cp4d_uninstall` role:
1. All CP4D service CRs are deleted
2. All CP4D platform CRs (ZenService, Ibmcpd) are deleted
3. All CP4D operators are uninstalled
4. All prerequisite operators (CPFS, NamespaceScope, Licensing) are uninstalled
5. Namespaces are deleted (if requested)
6. PVCs are deleted (if explicitly requested)
7. No CP4D-related pods remain running
8. Role can be run multiple times without errors (idempotent)

### Validation Commands
```bash
# Verify no CP4D CRs remain
oc get ibmcpd,zenservice,ws,wmlbase,analyticsengine,ccs,caservice -A

# Verify no CP4D operators remain
oc get subscriptions -n ibm-cpd-operators
oc get csv -n ibm-cpd-operators | grep -E 'cpd|zen|wsl|wml|spark|ca|ccs'

# Verify no CP4D pods remain
oc get pods -n ibm-cpd
oc get pods -n ibm-cpd-operators

# Verify namespaces deleted (if requested)
oc get namespace ibm-cpd ibm-cpd-operators cs-control ibm-common-services ibm-licensing
```

## Notes
- The uninstall process follows the reverse order of installation
- Service uninstall must complete before platform uninstall
- Platform uninstall must complete before prerequisites uninstall
- PVC deletion is opt-in to prevent accidental data loss
- Namespace deletion includes a grace period for finalizers
- Role handles missing resources gracefully (already uninstalled)
- All async operations include appropriate wait conditions and timeouts