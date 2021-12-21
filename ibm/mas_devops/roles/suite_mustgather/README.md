suite_mustgather
===============

Run IBM AI Applications' Must Gather tool against a MAS instance

Role Variables
--------------

### mas_instance_id
Required.  MAS instance ID to run against.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### base_output_dir
Required.  Location on the local disk to save the must-gather file.

- Environment Variable: `BASE_OUTPUT_DIR`
- Default Value: None

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    base_output_dir: ~/mas/mustgather

  roles:
    - ibm.mas_devops.suite_mustgather
```

License
-------

EPL-2.0
