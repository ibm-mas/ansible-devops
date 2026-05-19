# Custom Specifications Directory

This directory contains Jinja2 templates that define application-specific component configurations for MAS applications.

## Files

### `manage_components.yml.j2`
Defines the component configuration for IBM Maximo Manage application.

## Usage

These templates are loaded dynamically during application pre-configuration. The loading mechanism uses a variable-based path pattern:

**Location:** [`tasks/manage/pre-config/main.yml`](../../tasks/manage/pre-config/main.yml)

```yaml
set_fact:
  "mas_app_components_{{ mas_app_id }}": "{{ lookup('ansible.builtin.template', 'vars/customspecs/{{ mas_app_id }}_components.yml.j2') | from_yaml }}"
```

When `mas_app_id` is set to `"manage"`, this resolves to:
- Template: `vars/customspecs/manage_components.yml.j2`
- Fact created: `mas_app_components_manage`

The template is rendered, parsed as YAML, and stored as an Ansible fact for use during application configuration.

## Conditions

The component loading only occurs when:
- `mas_appws_spec` is not already defined
- During Manage-specific pre-configuration phase

## Adding New Application Components

To add component specifications for other MAS applications, create a new template file following the naming pattern:
```
<app_id>_components.yml.j2
```

Where `<app_id>` matches the value of `mas_app_id` variable (e.g., `monitor`, `predict`, etc.).