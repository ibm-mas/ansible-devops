ocp_setup_mas_deps
==================

This role provides support to install operators that are required by MAS to work. The role will deploy Service Binding Operator in all namespaces and Cert Manager in the cert-manager namespace.  The role declares a dependency on `ocp_verify` to ensure that the RedHat Operator Catalog is installed and ready before we try to install the Service Binding Operator from that catalog.

For MAS 8.6 or earlier JetStack cert-manager v1.2 is installed into the `cert-manager` namespace.  When used for MAS 8.7+ this role will result in the following operators being installed in the ibm-common-services namespace:
- IBM Cert Manager
- IBM Cloud Pak Foundational Services
- IBM NamespaceScope Operator
- Operand Deployment Lifecycle Manager

For MAS 8.6 or earlier (or when running MAS 8.7 on OCP 4.6) Service Binding Operator v0.8 will be installed from the preview channel.  It is important not to upgrade to later preview builds as they are incompatible with MAS due to breaking API changes in SBO.  For MAS 8.7 or later the stable channel will be used instead, with automatic updates enabled.  In both cases, the operator will be installed in the `openshift-operators` namespace with cluster scope.


Role Variables
--------------
### ocp_disable_upgrade
Set this to `true` to instruct the role to disable automatic OCP upgrades in the cluster.

- Environment Variable: None
- Default Value: `false`

### mas_channel
Used to determine whether to install SBO stable channel and the IBM badged cert-manager.

- Environment Variable: `MAS_CHANNEL`
- Default Value: `8.x`


Example Playbook
----------------

```yaml
- hosts: localhost
  roles:
    - ibm.mas_devops.ocp_setup_mas_deps
```


License
-------

EPL-2.0
