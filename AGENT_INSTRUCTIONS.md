# ansible-devops AI Coding Instructions

## Project Overview
Ansible playbook automation for IBM Maximo DevOps tasks. Implements role-based architecture for infrastructure provisioning, configuration, and deployment. Integrates Python for advanced logic and generates documentation from code.

## Architecture
- **ibm/mas_devops/**: Main role directory structure
  - **roles/**: Ansible roles grouped by function
    - `tasks/main.yml`: Role task definitions
    - `vars/main.yml`: Role variables (defaults)
    - `handlers/`: Handlers for state changes
    - `templates/`: Jinja2 templates for config files
    - `files/`: Static files distributed by role
  - **[role-name]/**: Individual role directory (e.g., `db2`, `kafka`, `openshift`)
- **docs/**: MkDocs documentation site for playbooks
  - `playbooks/`: Documented playbook usage
  - `execution-environment.md`: Container/EE configuration
- **build/**: Build system
  - `bin/`: Build scripts
  - `ee/`: Execution Environment definitions (Docker, bindep)
  - `scripts/`: Utility scripts
- **site/**: Generated documentation (output, don't edit)
- **Makefile**: Build targets for roles, docs, EE

## Key Patterns
- **Role-Based Architecture**: Playbooks call roles; each role is independently testable
  - Roles handle idempotent operations (safe to run multiple times)
  - Role variables define configuration; override at playbook level
  - Handlers trigger configuration reloads only on change
- **Jinja2 Templating**: Config files use `{{ variable }}` syntax
  - Accessed from role `vars/main.yml` or playbook input
  - Templates preserve file permissions and ownership
- **Execution Environments (EE)**: Playbooks run in container; `ee/` defines dependencies
  - `Dockerfile`: Base container image and Python packages
  - `bindep.txt`: System-level dependencies
  - Image must include all required Ansible collections and tools
- **Documentation Generation**: `site/gen_role_docs.py` auto-generates role documentation
  - Documents tasks, handlers, variables from role files
  - Run to regenerate after role changes

## Development Workflow
```bash
make build              # Build execution environment image
make roles-doc          # Generate role documentation
make lint               # Run yamllint on playbooks/roles (uses yamllint.yaml config)
make serve              # MkDocs dev server (localhost:8000)
ansible-playbook -i inventory.yml playbook.yml  # Test playbooks
```

## Important Conventions
- **YAML Structure**: Follow Ansible best practices (see yamllint.yaml rules)
  - Proper indentation (2 spaces), quoted strings where needed
  - Handler names must match `notify:` references exactly
- **Variable Naming**: Use snake_case; role-specific prefixes (e.g., `role_name_variable`)
- **Idempotence**: All roles must be idempotent (same result running 1x or 10x)
- **Error Handling**: Use `failed_when`, `changed_when` to control task outcome
- **Templating**: Config files in `templates/` use `j2` extension; preserve mode/owner
- **Task Names**: Clear, descriptive task names (shown in output); avoid generic names

## Testing Roles
- Run individual role: `ansible-playbook playbook.yml --tags role_name`
- Use Execution Environment for consistency: `ansible-playbook --inside-container` (if tool supports)
- Verify idempotence: run twice, second run should show no changes
- Check generated docs: `site/[role-name].md` reflects actual role structure

## Integration Points
- **Execution Environment**: Changes to role dependencies require updating `ee/bindep.txt` or `Dockerfile`
- **Playbook Composition**: Roles called from top-level playbooks; new roles must be added to playbook task lists
- **Variable Hierarchy**: Playbook variables override role defaults; document expected overrides
- **Documentation**: Role changes should regenerate docs via `make roles-doc`

## Common Tasks
- **Adding a Role**: Create `ibm/mas_devops/roles/role_name/{tasks,vars,handlers,templates}/`, run `make roles-doc`
- **Updating Dependencies**: Modify `ee/Dockerfile` or `ee/bindep.txt`, rebuild with `make build`
- **Extending Playbook**: Add role calls in top-level playbook, test with target environment


## Python Testing Environment

### Development Environment Setup
- **Virtual Environment Location**: `~/ibm-mas/ansible-devops/.venv`
- **Python Version**: 3.12.12
- **Platform**: WSL (Windows Subsystem for Linux)
- **Activation**: `source ~/ibm-mas/ansible-devops/.venv/bin/activate`

### Running Python Commands
When executing Python commands or tests in this project:
1. Always use WSL environment (not Windows CMD)
2. **Use `wsl bash -c "command"` format when running from Windows context**
3. Activate the virtual environment first
4. Example command format:
   ```bash
   wsl bash -c "cd ~/ibm-mas/ansible-devops && source .venv/bin/activate && cd ibm/mas_devops/tests && python -m pytest unit/plugins/action/ -v"
   ```

**Important**: When using execute_command tool, always prefix with `wsl bash -c` and wrap the entire command in double quotes.

### Python Testing Framework
- **Framework**: pytest with pytest-mock
- **Test Location**: `ibm/mas_devops/tests/`
- **Configuration**: `ibm/mas_devops/tests/pytest.ini`
- **Requirements**: `ibm/mas_devops/tests/requirements-test.txt`
- **Mock Helpers**: `ibm/mas_devops/tests/mocks/` (kubernetes_mocks, mas_devops_mocks, external_api_mocks)

### Testing Approach for Action Plugins
- ✅ Use REAL `mas.devops` functions (from ../python-devops package)
- ✅ Mock only external dependencies (Kubernetes API, HTTP requests)
- ❌ Do NOT mock `mas.devops.*` functions (they are part of code under test)
- Install python-devops in editable mode: `pip install -e ../python-devops`

### Running Tests
```bash
# From tests directory
cd ibm/mas_devops/tests
python -m pytest unit/plugins/action/ -v

# Run specific test file
python -m pytest unit/plugins/action/test_get_catalog_info.py -v

# Run with coverage
python -m pytest unit/plugins/action/ --cov=../plugins/action --cov-report=html
```

### Python 3.12 Compatibility
- **Important**: Python 3.12 removed `distutils` module
- **Solution**: `setuptools>=65.0.0` provides distutils compatibility
- Already included in requirements-test.txt

### Test Structure
- Each test file follows AAA pattern (Arrange-Act-Assert)
- Test files use direct imports: `import module_name`
- Mock helpers available in `mocks/` directory
- Fixtures defined in `conftest.py` files
- File naming: `test_<action_name>.py`
- Class naming: `Test<ActionName>`
- Method naming: `test_<scenario>_<expected_outcome>`

### Import Path Resolution
- Action plugin path added in `tests/unit/plugins/action/conftest.py`
- Relative path: `../../../../plugins/action`
- Import style: `import module_name` (direct import, not package-style)
- Mock helpers path added in `tests/conftest.py`

### Common Python Testing Issues
- **ModuleNotFoundError for action plugins**: Path is set up in conftest.py, use direct imports
- **distutils not found (Python 3.12)**: Install setuptools: `pip install setuptools`
- **mas.devops import errors**: Install python-devops in editable mode: `pip install -e ../python-devops`
- **Tests fail with async errors**: mock_task fixture sets `async_val = False` in conftest.py

### Test Documentation
- `ibm/mas_devops/tests/README.md` - Testing guide (407 lines)
- `ibm/mas_devops/tests/TEST_PLAN.md` - Test strategy (717 lines)
- `ibm/mas_devops/tests/TEST_IMPLEMENTATION_SUMMARY.md` - Progress tracking
