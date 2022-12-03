sbo
===

!!! important
    **Deprecated**  This role will be removed following the release of MAS 8.10 in early 2023.

This role provides support to install RedHat Service Binding Operator.  The role declares a dependency on `ocp_verify` to ensure that the RedHat Operator Catalog is installed and ready before we try to install the Service Binding Operator from that catalog.

- For MAS 8.7 the stable channel will be used instead, with automatic updates enabled.  In both cases, the operator will be installed in the `openshift-operators` namespace with cluster scope.
- For MAS 8.8 the Service Binding Operator is no longer required, calling this role with `mas_channel` set to 8.8 (or later) will result in no action taken.  This is also the default if no value is provided for `mas_channel`.


Role Variables
--------------
### mas_channel
Used to determine whether to install SBO stable channel and the IBM badged cert-manager.

- Optional, but if this is not set (or is set to any value other than `8.7.x`) SBO will not be installed
- Environment Variable: `MAS_CHANNEL`
- Default Value: `8.9.x`


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
