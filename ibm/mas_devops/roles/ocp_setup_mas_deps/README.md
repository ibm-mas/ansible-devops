ocp_setup_mas_deps
==================

This role provides support to install operators that are required by MAS to work. The role will deploy Service Binding Operator in all namespaces and Cert Manager in the cert-manager namespace.  The role declares a dependency on `ocp_verify` to ensure that the RedHat Operator Catalog is installed and ready before we try to install the Service Binding Operator from that catalog.


Role Variables
--------------

- `sbo_channel` Catalog channel used to obtain the Service Binding Operator.
- `sbo_startingcsv` Starting version for the Service Binding Operator subscription.
- `sbo_plan_approval` Update strategy for the Service Binding Operator subscription.


Example Playbook
----------------

```yaml
TODO: Add example
```

License
-------

EPL-2.0
