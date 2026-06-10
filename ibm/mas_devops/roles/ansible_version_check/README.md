# ansible_version_check

Internal-use role that all other roles in the collection declare a dependency upon to ensure that the minimum supported level of Ansible is used.

## Role Variables

This role has no configurable variables.


## Example Playbook

```yaml
- hosts: localhost
  vars:
    # Add required variables here
  roles:
    - ibm.mas_devops.ansible_version_check
```

## License

EPL-2.0
