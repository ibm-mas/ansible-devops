suite_app_verify
============

Verify if a MAS application is ready to use. This is done by verifying if Workspace CR is in READY state. If CR is not in READY state, it repeats verification every minute for ten minutes (you can override this rule and add more time if needed, check Role Variables section for more details)

Role Variables
--------------

<!-- TODO
mas_instance_id: masinst1
mas_workspace_id: masdev
mas_app_ws_apiversion: apps.mas.ibm.com/v1
mas_app_ws_kind: ManageWorkspace
mas_app_namespace: mas-masinst1-manage -->

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    mas_app_ws_apiversion: apps.mas.ibm.com/v1
    mas_app_ws_kind: ManageWorkspace
    mas_app_namespace: mas-masinst1-manage
  roles:
    - ibm.mas_devops.suite_app_verify
```

License
-------

EPL-2.0
