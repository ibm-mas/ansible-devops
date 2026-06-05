# Plan: Add targeted_mas_upgrade_channel Variable

## Objective
Add a new variable `targeted_mas_upgrade_channel` to the `suite_app_upgrade` role to allow users to specify a target upgrade channel when `skip_compatibility_check` is enabled. This addresses the limitation where non-GA channels (like `-dev`, `-feature`) cannot automatically determine the next upgrade channel from the compatibility matrix.

## Critical Rules
- Preserve all existing functionality and behavior when `skip_compatibility_check` is `false`
- The new variable should only be used when `skip_compatibility_check` is `true`
- Maintain backward compatibility - existing playbooks should continue to work without changes
- Follow existing variable naming conventions and patterns in the role
- Update documentation to clearly explain when and how to use the new variable
- Validate that the variable is provided when required (skip_compatibility_check=true and mas_app_channel is not set)

## Context Analysis

### Current Behavior
From [../../ibm/mas_devops/roles/suite_app_upgrade/tasks/main.yml#L33-L39](../../ibm/mas_devops/roles/suite_app_upgrade/tasks/main.yml#L33-L39):
- When `mas_app_channel` is not provided and `skip_compatibility_check` is `false`, the role automatically determines the target channel from the compatibility matrix based on the installed MAS core version
- When `skip_compatibility_check` is `true`, this automatic determination is skipped (line 36)
- The role then falls back to using `mas_app_channel` if provided (lines 41-45)

### Problem
For non-GA channels (e.g., `9.1.x-dev`, `9.2.x-feature`), the compatibility matrix may not have complete upgrade path information, making automatic channel determination unreliable. Users need a way to explicitly specify the target upgrade channel when bypassing compatibility checks.

### Solution Design
Add `targeted_mas_upgrade_channel` variable that:
1. Takes precedence over automatic channel determination when `skip_compatibility_check` is `true`
2. Allows users to explicitly specify the target upgrade channel
3. Falls back to existing `mas_app_channel` behavior if not provided
4. Is documented as the recommended approach when using `skip_compatibility_check=true`

## Execution Plan

### Phase 1: Add Variable Definition
- [ ] **1.1** Add `targeted_mas_upgrade_channel` to [../../ibm/mas_devops/roles/suite_app_upgrade/defaults/main.yml#L12](../../ibm/mas_devops/roles/suite_app_upgrade/defaults/main.yml#L12)
  - [ ] Define variable with environment variable lookup: `TARGETED_MAS_UPGRADE_CHANNEL`
  - [ ] Set default to empty string to maintain backward compatibility
  - [ ] Add inline comment explaining its purpose

### Phase 2: Update Task Logic
- [ ] **2.1** Modify channel determination logic in [../../ibm/mas_devops/roles/suite_app_upgrade/tasks/main.yml#L33-L45](../../ibm/mas_devops/roles/suite_app_upgrade/tasks/main.yml#L33-L45)
  - [ ] Add new task to set `mas_app_upgrade_target_channel` from `targeted_mas_upgrade_channel` when:
    - `skip_compatibility_check` is `true`
    - `targeted_mas_upgrade_channel` is defined and not empty
  - [ ] Insert this task before the existing fallback to `mas_app_channel` (before line 41)
  - [ ] Ensure proper precedence: `targeted_mas_upgrade_channel` > automatic determination > `mas_app_channel`

### Phase 3: Update Documentation
- [ ] **3.1** Add new variable section to [../../ibm/mas_devops/roles/suite_app_upgrade/README.md#L136](../../ibm/mas_devops/roles/suite_app_upgrade/README.md#L136)
  - [ ] Document `targeted_mas_upgrade_channel` variable
  - [ ] Include: Required/Optional status, Environment Variable, Default value
  - [ ] Explain purpose: explicit channel specification when skipping compatibility checks
  - [ ] Provide usage guidance: when to use (non-GA channels, skip_compatibility_check=true)
  - [ ] Add valid values and examples
  - [ ] Note relationship with `skip_compatibility_check` and `mas_app_channel`
  - [ ] Include warning about using with skip_compatibility_check

- [ ] **3.2** Update `skip_compatibility_check` documentation in [../../ibm/mas_devops/roles/suite_app_upgrade/README.md#L112-L136](../../ibm/mas_devops/roles/suite_app_upgrade/README.md#L112-L136)
  - [ ] Add note recommending use of `targeted_mas_upgrade_channel` when skipping checks
  - [ ] Cross-reference the new variable

### Phase 4: Add Example Usage
- [ ] **4.1** Update example playbook in [../../ibm/mas_devops/roles/suite_app_upgrade/README.md#L138-L149](../../ibm/mas_devops/roles/suite_app_upgrade/README.md#L138-L149)
  - [ ] Add second example showing usage with `skip_compatibility_check` and `targeted_mas_upgrade_channel`
  - [ ] Use a non-GA channel example (e.g., `9.2.x-feature`)

## Validation

### Test Scenarios
1. **Backward Compatibility**
   - Run upgrade without `targeted_mas_upgrade_channel` - should work as before
   - Verify existing playbooks continue to function

2. **New Variable Usage**
   - Set `skip_compatibility_check=true` and `targeted_mas_upgrade_channel=9.2.x-feature`
   - Verify upgrade proceeds to specified channel
   - Confirm no compatibility checks are performed

3. **Variable Precedence**
   - Test with both `targeted_mas_upgrade_channel` and `mas_app_channel` set
   - Verify `targeted_mas_upgrade_channel` takes precedence when `skip_compatibility_check=true`

4. **Edge Cases**
   - Empty `targeted_mas_upgrade_channel` - should fall back to `mas_app_channel`
   - Both variables empty with `skip_compatibility_check=true` - should handle gracefully

### Validation Commands
```bash
# Verify role syntax
ansible-playbook --syntax-check ibm/mas_devops/playbooks/mas_upgrade.yml

# Test with new variable (dry-run)
MAS_INSTANCE_ID=test1 \
MAS_APP_ID=manage \
SKIP_COMPATIBILITY_CHECK=true \
TARGETED_MAS_UPGRADE_CHANNEL=9.2.x-feature \
MAS_UPGRADE_DRYRUN=true \
ansible-playbook ibm/mas_devops/playbooks/mas_upgrade.yml