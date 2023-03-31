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

### collect_certificates
Optional. collects certificates from secrets and configmaps

- Environment Variable: `COLLECT_CERTIFICATES`
- Default Value: false

### additional_namespaces
Optional. Collects data in the specified namespaces (comma separated list). 

- Environment Variable: `ADDITIONAL_NAMESPACES`
- Default Value: None



Example Playbook
----------------

### Collect data from all MAS namespaces
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    base_output_dir: ~/mas/mustgather

  roles:
    - ibm.mas_devops.suite_mustgather
```

### Collect all data and certificates from all mas-dev-core, mongoce and ibm-sls namespaces
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    base_output_dir: ~/mas/mustgather
    collect_certificates: true
    additional_namespaces: mas-dev-core,mongoce,ibm-sls

  roles:
    - ibm.mas_devops.suite_mustgather
```
License
-------

EPL-2.0
