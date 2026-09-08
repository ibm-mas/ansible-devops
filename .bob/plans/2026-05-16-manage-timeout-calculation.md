# Dynamic Manage Configuration Timeout Implementation

## Objective
Implement a Python-based filter to calculate appropriate timeout values for Manage app configuration based on the components being installed, replacing the current fixed 18-hour timeout that causes slow failures.

## Critical Rules
- Must be implemented as an Ansible filter plugin in Python in a new dedicated file
- Create `ibm/mas_devops/plugins/filter/manage_timeouts.py` for better organization
- Must follow existing filter patterns and include `FilterModule` class
- Must not introduce functional changes to existing timeout behavior for non-foundation installations
- Must validate all changes with `black` and `flake8`
- No copyright headers required (existing filters don't have them)

## Context
- Current timeout: `delay=360s * retries=180 = 64,800s (~18 hours)`
- Foundation mode (empty components): Should use `~4 hours = 14,400s`
- Full mode (with components): Should use current `~18 hours = 64,800s`
- Variable `mas_appws_components` structure: `{'base': {'version': 'latest'}, 'health': {'version': 'latest'}}` or `None`/`{}`
- Defined in [../../ibm/mas_devops/roles/suite_app_config/defaults/main.yml:32](../../ibm/mas_devops/roles/suite_app_config/defaults/main.yml#L32)
- Used in [../../ibm/mas_devops/roles/suite_app_config/tasks/main.yml:138-139](../../ibm/mas_devops/roles/suite_app_config/tasks/main.yml#L138-L139)

## Execution Plan

### Phase 1: Create New Filter Plugin File
- [x] **1.1** Create `ibm/mas_devops/plugins/filter/manage_timeouts.py`
  - [x] Add `calculate_manage_timeouts` filter function
  - [x] Accept `mas_appws_components` parameter (dict or None)
  - [x] Return dict with `delay` and `retries` keys
  - [x] Foundation mode (empty/None): `delay=240, retries=60` (4 hours)
  - [x] Full mode (has components): `delay=360, retries=180` (18 hours)
  - [x] Include docstring following existing pattern in filters.py
  - [x] Create `FilterModule` class with `filters()` method
- [x] **1.2** Validate with `black` and `flake8`

### Phase 2: Update Manage Variables
- [x] **2.1** Modify [../../ibm/mas_devops/roles/suite_app_config/vars/manage.yml:7-8](../../ibm/mas_devops/roles/suite_app_config/vars/manage.yml#L7-L8)
  - [x] Replace hardcoded values with filter call
  - [x] Use pattern: `"{{ mas_appws_components | ibm.mas_devops.calculate_manage_timeouts }}"`
  - [x] Extract `delay` and `retries` from returned dict
  - [x] Preserve environment variable override capability

### Phase 3: Create Unit Tests
- [x] **3.1** Create test file `ibm/mas_devops/tests/unit/plugins/filter/test_calculate_manage_timeouts.py`
  - [x] Test foundation mode (None, {}, empty dict)
  - [x] Test full mode (with components)
  - [x] Test return value structure
  - [x] Follow existing test patterns from other filter tests
- [x] **3.2** Run tests to validate implementation - All 7 tests passed

### Phase 4: Validation
- [x] **4.1** Run `black` on modified Python files
- [x] **4.2** Run `flake8` on modified Python files
- [x] **4.3** Verify no syntax errors in YAML files
- [x] **4.4** Review changes ensure backward compatibility

## Validation

### Commands
```bash
# Format and lint Python changes
black ibm/mas_devops/plugins/filter/manage_timeouts.py ibm/mas_devops/tests/unit/plugins/filter/test_calculate_manage_timeouts.py
flake8 ibm/mas_devops/plugins/filter/manage_timeouts.py ibm/mas_devops/tests/unit/plugins/filter/test_calculate_manage_timeouts.py

# Run unit tests
cd ibm/mas_devops/tests
pytest unit/plugins/filter/test_calculate_manage_timeouts.py -v
```

### Success Criteria
- All Python files pass `black` and `flake8` validation
- Unit tests pass with 100% coverage of the new filter
- Foundation mode: timeout = 4 hours (14,400s)
- Full mode: timeout = 18 hours (64,800s)
- Environment variable overrides still work
- No breaking changes to existing behavior