common_services
===============

This will result in the following operators being installed in the `ibm-common-services` namespace

- IBM Cloud Pak Foundational Services
- IBM NamespaceScope Operator
- Operand Deployment Lifecycle Manager

Also, an operator group will be created in the namespace if one does not already exist.


Example Playbook
----------------

```yaml
- hosts: localhost
  roles:
    - ibm.mas_devops.common_services
```


License
-------

EPL-2.0
