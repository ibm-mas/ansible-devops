suite_upgrade
=============

This role supports an in-place upgrade from MAS 8.6 to 8.7 in an OpenShift Cluster, this upgrade covers a number of facets beyond just upgrading the MAS operators themselves:

- Dependency checks to ensure the environment is ready to be upgraded
- Upgrade to cert-manager v1.5 (IBM badged version), required by CP4D v4
- Upgrade to CP4D v4
- Upgrade of MAS Core
- Upgrade of all installed MAS applications (optional)
- Upgrade of OCP to v4.8 (optional)
- Upgrade of SBO to v1.0 (optional)


Role Variables
--------------

TODO: Finish documentation


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  roles:
    - ibm.mas_devops.suite_upgrade
```

License
-------

EPL-2.0
