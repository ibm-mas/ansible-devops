# Fix suite_upgrade Channel Change Logic

**Created:** 2026-06-05  
**Status:** Planning

## Objective

Fix the [`suite_upgrade`](../../ibm/mas_devops/roles/suite_upgrade/tasks/upgrade.yml) role to handle channel changes that don't result in version upgrades (e.g., lateral moves between non-GA channels like `9.1.x-dev` to `9.1.x-feature` where both have the same CSV version).

## Problem Analysis

### Current Failing Logic
At [`ibm/mas_devops/roles/suite_upgrade/tasks/upgrade.yml:21-33`](../../ibm/mas_devops/roles/suite_upgrade/tasks/upgrade.yml#L21-L33), the task waits for BOTH conditions:

```yaml
until:
  - updated_suite_sub_info.resources[0].status.installPlanGeneration > suite_sub_info.resources[0].status.installPlanGeneration
  - updated_suite_sub_info.resources[0].status.state == "AtLatestKnown"
```

### Why It Fails
- When changing to a channel with the same CSV version already installed, OLM doesn't generate a new install plan
- `installPlanGeneration` remains unchanged
- Subscription reaches `AtLatestKnown` state (correct behavior)
- Task times out waiting for impossible condition (both requirements)

### Scenarios That Fail
1. Non-GA channels (`-dev`, `-feature`) with same version
2. Lateral channel moves (e.g., `9.1.x-dev` → `9.1.x-feature`)
3. Any channel where latest version is already installed

### Comparison with suite_app_upgrade
The [`suite_app_upgrade`](../../ibm/mas_devops/roles/suite_app_upgrade/tasks/upgrade.yml) role doesn't have this wait logic - it updates the subscription and immediately waits for the OperatorCondition (lines 19-43). This simpler approach works because:
- It doesn't assume version changes
- Relies on operator reconciliation status
- Handles both upgrade and no-upgrade scenarios

## Critical Rules

- Preserve all existing validation and health checks
- Do not introduce functional changes beyond fixing the wait condition
- Maintain backward compatibility with existing upgrade scenarios
- Keep the same retry/delay timing strategy
- Ensure the fix works for both upgrade and no-upgrade scenarios

## Solution Design

### Approach: Conditional Wait Logic

Modify the wait condition at [`ibm/mas_devops/roles/suite_upgrade/tasks/upgrade.yml:21-33`](../../ibm/mas_devops/roles/suite_upgrade/tasks/upgrade.yml#L21-L33) to handle two scenarios:

**Scenario A: Version Upgrade Occurred**
- New install plan generated (`installPlanGeneration` incremented)
- Subscription reaches `AtLatestKnown`

**Scenario B: No Version Change**
- No new install plan (`installPlanGeneration` unchanged)
- Subscription reaches `AtLatestKnown`
- Current CSV matches installed CSV (confirms no upgrade needed)

### Implementation Strategy

Replace the existing `until` condition with logic that succeeds when:

```yaml
until: >-
  (updated_suite_sub_info.resources[0].status.installPlanGeneration > suite_sub_info.resources[0].status.installPlanGeneration
   and updated_suite_sub_info.resources[0].status.state == "AtLatestKnown")
  or
  (updated_suite_sub_info.resources[0].status.installPlanGeneration == suite_sub_info.resources[0].status.installPlanGeneration
   and updated_suite_sub_info.resources[0].status.state == "AtLatestKnown"
   and updated_suite_sub_info.resources[0].status.currentCSV == updated_suite_sub_info.resources[0].status.installedCSV)
```

This ensures:
- Existing upgrade scenarios continue to work (Scenario A)
- Channel changes without upgrades succeed (Scenario B)
- We don't proceed if subscription is stuck or failing

## Execution Plan

### Phase 1: Implement Fix
- [x] **1.1** Modify wait condition at [`ibm/mas_devops/roles/suite_upgrade/tasks/upgrade.yml:31-33`](../../ibm/mas_devops/roles/suite_upgrade/tasks/upgrade.yml#L31-L33)
  - [x] Replace simple AND condition with OR-based conditional logic
  - [x] Add CSV comparison for no-upgrade scenario
  - [x] Ensure proper YAML multiline formatting
  - [x] Add inline comment explaining the two scenarios

- [x] **1.2** Add debug output after subscription check
  - [x] Insert debug task after line 33 to show subscription state
  - [x] Include: `installPlanGeneration` (before/after), `state`, `currentCSV`, `installedCSV`
  - [x] Helps troubleshooting and confirms which scenario occurred

### Phase 2: Documentation
- [ ] **2.1** Update inline comments in [`upgrade.yml`](../../ibm/mas_devops/roles/suite_upgrade/tasks/upgrade.yml)
  - [ ] Document the two scenarios at the wait condition
  - [ ] Explain why both paths are needed
  - [ ] Reference this plan document

- [ ] **2.2** Consider updating role README if needed
  - [ ] Check if [`suite_upgrade/README.md`](../../ibm/mas_devops/roles/suite_upgrade/README.md) exists
  - [ ] Add note about channel change behavior if appropriate

### Phase 3: Validation
- [ ] **3.1** Review the fix
  - [ ] Verify YAML syntax is correct
  - [ ] Confirm logic handles both scenarios
  - [ ] Check that existing upgrade paths still work
  - [ ] Ensure no unintended side effects

## Validation Criteria

### Success Criteria
1. Channel changes with version upgrades continue to work (existing behavior)
2. Channel changes without version upgrades succeed (new behavior)
3. Task fails appropriately if subscription enters error state
4. Debug output clearly shows which scenario occurred

### Test Scenarios
1. **Upgrade scenario**: Change from `9.0.x` to `9.1.x` (version change expected)
2. **Lateral move**: Change from `9.1.x-dev` to `9.1.x-feature` (same version)
3. **Already at latest**: Change to channel where latest version is installed

## Notes

- The `suite_app_upgrade` role uses a simpler approach without this wait logic
- Consider aligning both roles in future refactoring
- This fix is surgical - only changes the wait condition logic
- All downstream validation (OperatorCondition, Suite CR health) remains unchanged