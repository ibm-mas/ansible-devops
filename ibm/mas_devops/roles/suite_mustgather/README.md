suite_mustgather
===============

Run IBM AI Applications' Must Gather tool against a MAS instance

Role Variables
--------------

- `mas_instance_id` MAS instance ID to run against
- `base_output_dir` Location on the local disk to save the must-gather file


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    base_output_dir: "{{ lookup('env', 'BASE_OUTPUT_DIR') }}"

  roles:
    - ibm.mas_devops.suite_mustgather
```

License
-------

EPL-2.0
