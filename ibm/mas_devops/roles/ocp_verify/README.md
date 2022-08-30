ocp_verify
==========

This role will verify that the target OCP cluster is ready to be setup for MAS.

For example, in IBMCloud ROKS we have seen delays of over an hour before the Red Hat Operator catalog is ready to use.  This will cause attempts to install anything from that CatalogSource to fail as the timeouts built into the roles in this collection are designed to catch problems with an install, rather than a half-provisioned cluster that is not properly ready to use yet.


Role Variables
--------------

### cluster_name
Specify the name of the cluster, in some cluster setups this name is required to determine the name of the default router certificate.

- Optional
- Environment Variable: `CLUSTER_NAME`
- Default Value: None

### cluster ingres tls secret name
Specify the name of the cluster's ingres tls secret which contains the default router certificate.

- Optional
- Environment Variable: `OCP_INGRESS_TLS_SECRET_NAME`
- Default Value: router-certs-default


Example Playbook
----------------

```yaml
- hosts: localhost
  roles:
    - ibm.mas_devops.ocp_verify
```


License
-------

EPL-2.0
