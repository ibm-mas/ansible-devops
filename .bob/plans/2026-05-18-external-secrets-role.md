# External Secrets Operator Ansible Role Implementation Plan

## Objective
Create an Ansible role named `external-secrets` that manages the External Secrets Operator deployment in Kubernetes clusters using Helm, following established patterns from the `longhorn` and `cert_manager` roles.

## Critical Rules
- Follow the exact structure and patterns used in `longhorn` role for Helm-based deployments
- Use action-based routing pattern from `cert_manager` role (install/uninstall)
- All Ansible modules must use fully qualified collection names (e.g., `kubernetes.core.helm`)
- Role must be idempotent - repeated executions produce same result without errors
- Include comprehensive wait conditions and health checks for operator readiness
- Support check mode for dry-run operations
- Document all variables with descriptions, defaults, and usage examples
- Follow External Secrets official getting started guide: https://external-secrets.io/latest/introduction/getting-started/

## Execution Plan

### Phase 1: Role Structure Setup ✅
- [x] **1.1** Create role directory structure
  - [x] Create `ibm/mas_devops/roles/external-secrets/` directory
  - [x] Create subdirectories: `tasks/`, `defaults/`, `templates/`, `meta/`
- [x] **1.2** Create `meta/main.yml` with role metadata
  - [x] Define role dependencies (if any)
  - [x] Set galaxy_info with author, description, license (EPL-2.0)
  - [x] Define supported platforms
- [x] **1.3** Validation: Verify directory structure matches `longhorn` role pattern

### Phase 2: Default Variables Configuration ✅
- [x] **2.1** Create `defaults/main.yml` with all configurable variables
  - [x] `external_secrets_action`: Action to perform (install/uninstall), default "install"
  - [x] `external_secrets_namespace`: Target namespace, default "external-secrets-system"
  - [x] `external_secrets_chart_version`: Helm chart version, default to latest stable
  - [x] `external_secrets_release_name`: Helm release name, default "external-secrets"
  - [x] `external_secrets_repo_url`: Helm repository URL, default "https://charts.external-secrets.io"
  - [x] `external_secrets_cleanup_crds`: Flag for CRD cleanup on uninstall, default false
  - [x] `external_secrets_cleanup_namespace`: Flag for namespace cleanup, default false
  - [x] `external_secrets_values`: Custom Helm values override, default empty dict
- [x] **2.2** Validation: Review defaults against External Secrets documentation

### Phase 3: Main Task Router ✅
- [x] **3.1** Create `tasks/main.yml` as action router
  - [x] Add debug task to display all configuration parameters
  - [x] Add conditional include for `tasks/install.yml` when action is "install"
  - [x] Add conditional include for `tasks/uninstall.yml` when action is "uninstall"
  - [x] Add assertion to validate action parameter
- [x] **3.2** Validation: Test routing logic with check mode

### Phase 4: Installation Tasks ✅
- [x] **4.1** Create `tasks/install.yml` for operator installation
  - [x] Add Helm repository using `kubernetes.core.helm_repository`
  - [x] Create namespace using `kubernetes.core.k8s` with template
  - [x] Install Helm chart using `kubernetes.core.helm` with values template
  - [x] Add tags: `install`, `external-secrets`
- [x] **4.2** Add wait conditions for operator readiness
  - [x] Wait for external-secrets deployment to be ready
  - [x] Wait for external-secrets-webhook deployment to be ready
  - [x] Wait for external-secrets-cert-controller deployment to be ready
  - [x] Use retries: 30, delay: 60 (similar to cert_manager pattern)
- [x] **4.3** Add verification tasks
  - [x] Verify CRDs are created (SecretStore, ClusterSecretStore, ExternalSecret)
  - [x] Verify webhook is responding
- [ ] **4.4** Validation: Test installation on clean cluster

### Phase 5: Uninstallation Tasks ✅
- [x] **5.1** Create `tasks/uninstall.yml` for operator removal
  - [x] Add safety check to confirm uninstallation intent
  - [x] Uninstall Helm release using `kubernetes.core.helm` with state: absent
  - [x] Conditionally delete namespace based on `external_secrets_cleanup_namespace`
  - [x] Conditionally delete CRDs based on `external_secrets_cleanup_crds`
  - [x] Add tags: `uninstall`, `external-secrets`
- [x] **5.2** Add CRD cleanup logic
  - [x] List all External Secrets CRDs to delete
  - [x] Use loop to delete each CRD: externalsecrets, secretstores, clustersecretstores, etc.
  - [x] Add wait conditions for resource deletion
- [ ] **5.3** Validation: Test uninstallation and verify cleanup

### Phase 6: Templates ✅
- [x] **6.1** Create `templates/namespace.yml.j2`
  - [x] Define Namespace resource with `external_secrets_namespace` variable
  - [x] Add appropriate labels and annotations
- [x] **6.2** Create `templates/values.yml.j2` for Helm values
  - [x] Include default values for External Secrets Operator
  - [x] Support custom values override via `external_secrets_values`
  - [x] Configure resource limits and requests
  - [x] Configure webhook settings
  - [x] Add conditional blocks for optional features
- [x] **6.3** Validation: Render templates and verify YAML syntax

### Phase 7: Documentation ✅
- [x] **7.1** Create comprehensive `README.md`
  - [x] Overview section describing External Secrets Operator
  - [x] Features list
  - [x] Deployed components section
  - [x] Role variables section with detailed descriptions
    - [x] For each variable: purpose, when to use, valid values, impact, related variables, notes
  - [x] Example playbooks section
    - [x] Basic installation example
    - [x] Installation with custom values
    - [x] Uninstallation example
  - [x] Prerequisites section (Helm, cluster access)
  - [x] Additional resources and links
  - [x] License (EPL-2.0)
- [x] **7.2** Add inline documentation
  - [x] Comment all task files with clear descriptions
  - [x] Document complex logic and conditionals
  - [x] Add examples in comments where helpful
- [x] **7.3** Validation: Review documentation for completeness and accuracy

### Phase 8: Testing and Validation
- [ ] **8.1** Create test playbook
  - [ ] Test installation with default values
  - [ ] Test installation with custom values
  - [ ] Test idempotency (run twice, verify no changes on second run)
  - [ ] Test check mode
  - [ ] Test uninstallation with and without cleanup flags
- [ ] **8.2** Verify error handling
  - [ ] Test with missing prerequisites (no Helm)
  - [ ] Test with invalid parameters
  - [ ] Test with cluster connectivity issues
  - [ ] Verify meaningful error messages
- [ ] **8.3** Integration testing
  - [ ] Test with actual External Secrets resources (SecretStore, ExternalSecret)
  - [ ] Verify operator functionality after installation
  - [ ] Test upgrade scenario (install older version, then newer)
- [ ] **8.4** Final validation: Complete end-to-end test on clean cluster

## Validation

### Installation Validation
```bash
# Verify Helm release
helm list -n external-secrets-system

# Verify deployments
kubectl get deployments -n external-secrets-system

# Verify CRDs
kubectl get crd | grep external-secrets

# Verify operator pods
kubectl get pods -n external-secrets-system
```

### Success Criteria
- All deployments show READY status (e.g., 1/1, 2/2)
- All CRDs are created: externalsecrets, secretstores, clustersecretstores, etc.
- Webhook is responding to API requests
- Role can be run multiple times without errors (idempotent)
- Check mode works without making changes
- Uninstallation cleanly removes all resources when cleanup flags are set

### Uninstallation Validation
```bash
# Verify Helm release removed
helm list -n external-secrets-system

# Verify namespace removed (if cleanup enabled)
kubectl get namespace external-secrets-system

# Verify CRDs removed (if cleanup enabled)
kubectl get crd | grep external-secrets
```

## File Structure Reference
```
ibm/mas_devops/roles/external-secrets/
├── README.md
├── defaults/
│   └── main.yml
├── meta/
│   └── main.yml
├── tasks/
│   ├── main.yml
│   ├── install.yml
│   └── uninstall.yml
└── templates/
    ├── namespace.yml.j2
    └── values.yml.j2
```

## Key Implementation Notes
1. Use `kubernetes.core.helm_repository` to add External Secrets Helm repo
2. Use `kubernetes.core.helm` for chart installation/uninstallation
3. Use `kubernetes.core.k8s` for namespace and CRD management
4. Use `kubernetes.core.k8s_info` for wait conditions and verification
5. Follow wait pattern: retries: 30, delay: 60 for critical deployments
6. Include proper error messages with `fail_msg` in assertions
7. Use tags for selective task execution
8. Support both environment variables and direct variable assignment
9. Make role reusable across different environments
10. Ensure all tasks support check mode with `check_mode: no` where needed