uninstall_cr
=============
This role performs a common task to delete a custom resource.
It is useful to be used across different playbooks where uninstalling a service or an application is required.

Role Variables
--------------

### cr_namespace
Optional. Defines the Custom Resources's namespace. Used to lookup the refered CR to be deleted.

- Environment Variable: `CR_NAMESPACE`
- Default Value: None

### cr_apiversion
Optional. Defines the Custom Resource's API Version. Used to lookup the refered CSV to be deleted.

- Environment Variable: `CSV_APIVERSION`
- Default Value: None

### cr_kind
Optional. Defines the Custom Resource's kind. Used to lookup the refered CR to be deleted.

- Environment Variable: `CR_KIND`
- Default Value: None

### cr_name
Optional. Defines the Custom Resource's name. Used to lookup the refered CR to be deleted.

- Environment Variable: `CR_NAME`
- Default Value: None

### cr_label_selector
Optional. Defines the Custom Resource's label. Used to lookup the refered CR to be deleted.

- Environment Variable: `CR_LABEL_SELECTOR`
- Default Value: None


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  roles:
    - ibm.mas_devops.uninstall_cr
```
