sbo
===

This role provides support to install RedHat Service Binding Operator.  The role declares a dependency on `ocp_verify` to ensure that the RedHat Operator Catalog is installed and ready before we try to install the Service Binding Operator from that catalog.

For MAS 8.6 or earlier (or when running MAS 8.7 on OCP 4.6) Service Binding Operator v0.8 will be installed from the preview channel.  It is important not to upgrade to later preview builds as they are incompatible with MAS due to breaking API changes in SBO.  For MAS 8.7 the stable channel will be used instead, with automatic updates enabled.  In both cases, the operator will be installed in the `openshift-operators` namespace with cluster scope.

For MAS 8.8 the Service Binding Operator is no longer required, calling this role with `mas_channel` set to 8.8 (or later) will result in no action taken.  This is also the default if no value is provided for `mas_channel`.


Role Variables
--------------
### mas_channel
Used to determine whether to install SBO stable channel and the IBM badged cert-manager.

- Optional, but if this is not set SBO will not be installed
- Environment Variable: `MAS_CHANNEL`
- Default Value: None


Example Playbook
----------------

```yaml
- hosts: localhost
  roles:
    - ibm.mas_devops.sbo
```


License
-------

EPL-2.0
