suite_manage_birt_report_config
===

This role extends support for configuring Birt Report in **Manage** application as a separate and dedicated **report** bundle server workload.

The following Manage properties will be added to every and each Manage server bundle:

- `mxe.report.birt.viewerurl`= `https://{{ mas_workspace_id }}-{{ manage_report_bundle_server_name }}.manage.{{ mas_domain }}`
- `mxe.report.birt.disablequeuemanager`= 0 (if bundle type = `report`) or 1 (if bundle type != `report`)

The goal for this role is to setup the specific Manage Report route to be the endpoint for the generated reports in Manage (which will forward the report workload to the dedicated `report` type bundle pod).

Role Variables
--------------
### mas_instance_id
Required. The instance ID of Maximo Application Suite. This will be used to lookup for Manage application resources.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_workspace_id
Required. The workspace ID of Maximo Application Suite. This will be used to lookup for Manage application resources.

- Environment Variable: `MAS_WORKSPACE_ID`
- Default Value: None

### manage_workspace_cr_name
Optional. Name of the `ManageWorkspace` Custom Resource that will be targeted to configure the new PVC definitions.

- Environment Variable: `MANAGE_WORKSPACE_CR_NAME`
- Default Value: `$MAS_INSTANCE_ID-$MAS_WORKSPACE_ID`

### manage_report_bundle_server_name
Optional. Name of the Manage report bundle server.
It will be used to configure the Manage's report bundle server and its corresponding route.
Not needed if the report bundle server is already configured.

- Environment Variable: `MANAGE_REPORT_BUNDLE_SERVER_NAME`
- Default Value: `rpt`

Example Playbook
----------------
The following sample can be used to configure BIRT report for an existing Manage application instance.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: main
  roles:
    - ibm.mas_devops.suite_manage_birt_report_config
```

Run Role Playbook
----------------
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export MAS_INSTANCE_ID=masinst1
export MAS_WORKSPACE_ID=main
export MANAGE_REPORT_BUNDLE_SERVER_NAME=report
ROLE_NAME='suite_manage_birt_report_config' ansible-playbook playbooks/run_role.yml

License
-------

EPL-2.0
