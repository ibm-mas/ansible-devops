# Add Helm Support for CPD Platform Components

## Objective
Add Helm installation support for cpd-platform, cpfs, and zen operators in the cp4d role, following the same pattern used in cp4d_service role. This will support CPD 5.3.1+ while maintaining backward compatibility with CPD 5.2.0 OLM installations.

## Critical Rules
- Maintain backward compatibility with existing OLM installations (CPD 5.2.0)
- Follow the same Helm implementation pattern as cp4d_service role
- Add installation method selection (auto/olm/helm) similar to cp4d_service
- Create separate helm/ folder for Helm-specific tasks
- Do not modify existing OLM installation logic

## Execution Plan

### Phase 1: Add Configuration and Support Matrix
- [x] **1.1** Update [`cp4d/defaults/main.yml`](../../ibm/mas_devops/roles/cp4d/defaults/main.yml) to add:
  - Installation method selection variable (`cpd_install_method`)
  - Helm repository configuration
  - Component metadata for cpfs, zen, cpd-platform with Helm chart names
- [x] **1.2** Create [`cp4d/vars/component-support.yml`](../../ibm/mas_devops/roles/cp4d/vars/component-support.yml) defining support matrix for cpfs, zen, cpd-platform
- [x] **1.3** Validate configuration matches cp4d_service pattern

### Phase 2: Create Helm Installation Tasks
- [x] **2.1** Create [`cp4d/tasks/helm/`](../../ibm/mas_devops/roles/cp4d/tasks/helm/) directory
- [x] **2.2** Create [`cp4d/tasks/helm/setup-helm-repo.yml`](../../ibm/mas_devops/roles/cp4d/tasks/helm/setup-helm-repo.yml) (reuse from cp4d_service)
- [x] **2.3** Create [`cp4d/tasks/helm/install-helm.yml`](../../ibm/mas_devops/roles/cp4d/tasks/helm/install-helm.yml) orchestrator for all three components
- [x] **2.4** Create [`cp4d/tasks/helm/install-component.yml`](../../ibm/mas_devops/roles/cp4d/tasks/helm/install-component.yml) generic component installer

### Phase 3: Update Main Installation Flow
- [x] **3.1** Update [`cp4d/tasks/main.yml`](../../ibm/mas_devops/roles/cp4d/tasks/main.yml) to:
  - Load component support matrix
  - Determine installation method (auto/olm/helm)
  - Route to appropriate installation path
- [x] **3.2** Refactor existing OLM tasks into [`cp4d/tasks/olm/`](../../ibm/mas_devops/roles/cp4d/tasks/olm/) directory:
  - Move `install-cpfs.yml` to `olm/install-cpfs.yml`
  - Move `create-subscriptions.yml` to `olm/create-subscriptions.yml`
  - Move `install-cp4d.yml` to `olm/install-cp4d.yml`
- [x] **3.3** Update task includes in main.yml to reference new paths

### Phase 4: Testing and Validation
- [ ] **4.1** Test OLM installation path (CPD 5.2.0 compatibility)
- [ ] **4.2** Test Helm installation path (CPD 5.3.1)
- [ ] **4.3** Test auto-detection logic
- [ ] **4.4** Verify all three components install correctly via Helm

## Validation
- Run ansible-playbook with CPD 5.2.0 using OLM (existing behavior)
- Run ansible-playbook with CPD 5.3.1 using Helm (new behavior)
- Verify cpfs, zen, and cpd-platform operators are installed and functional
- Confirm ZenService and Ibmcpd CRs are created successfully