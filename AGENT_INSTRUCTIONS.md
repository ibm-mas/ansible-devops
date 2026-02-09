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
