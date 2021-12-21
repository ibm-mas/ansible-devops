suite_mustgather
===============

Run IBM AI Applications' Must Gather tool against a MAS instance

Role Variables
--------------
| Variable        | Env Var           | Default | Description |
| --------------- | ------------------| ------- | ----------- |
| mas_instance_id | MAS_INSTANCE_ID   | -       | Required.  MAS instance ID to run against |
| base_output_dir | BASE_OUTPUT_DIR   | -       | Required.  Location on the local disk to save the must-gather file |


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
