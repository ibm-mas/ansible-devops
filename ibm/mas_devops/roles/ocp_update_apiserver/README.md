ocp_update_apiserver
====================

This role will update APIServer custom resource to custom tlsSecurityProfile to accommodate ciphers supported by IBM Java Semeru runtime. This is required for allowing the Java applications using Semeru runtime to run in FIPS mode.


Role Variables
--------------

### cluster_type
Specify the cluster type, supported values are `fyre`, `roks`, `rosa`, and `ipi`.

- Required
- Environment Variable: `CLUSTER_TYPE`
- Default Value: None

### ocp_fips_enabled
Specify the cluster is fips enabled or not.

- Required
- Environment Variable: `OCP_FIPS_ENABLED`
- Default Value: false


Example Playbook
----------------

```yaml
- hosts: localhost
  roles:
    - ibm.mas_devops.ocp_update_apiserver
```


License
-------

EPL-2.0
