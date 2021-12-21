suite_mustgather
===============

Run IBM AI Applications' Must Gather tool against a MAS instance

Role Variables
--------------

- `mas_instance_id` MAS instance ID to run against, will default to the value of the `MAS_INSTANCE_ID` environment variable
- `base_output_dir` Location on the local disk to save the must-gather file, will default to the value of the `BASE_OUTPUT_DIR` environment variable


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
