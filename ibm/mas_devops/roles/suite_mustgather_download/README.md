suite_mustgather_download
===============

Downloads the result from IBM AI Applications' Must Gather tool that is run against a MAS instance. This role is to be used when the `suite_mustgather` role is run from within a pipeline, and the user needs to download the result to a local machine. If you run the `suite_mustgather` role locally then there is no need to run this role as the output is already available to you locally.

Role Variables
--------------

### local_output_dir
Required.  Location on the local disk to save the must-gather file.

- Environment Variable: `LOCAL_OUTPUT_DIR`
- Default Value: None

### mustgather_namespace
Required.  The openshift namespace that the pipeline, that ran the suite_mustgather task, was executed in.

- Environment Variable: `MUSTGATHER_NAMESPACE`
- Default Value: None

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mustgather_namespace: mas-samples-pipelines
    local_output_dir: ~/mas/mustgather

  roles:
    - ibm.mas_devops.suite_mustgather_download
```

License
-------

EPL-2.0
