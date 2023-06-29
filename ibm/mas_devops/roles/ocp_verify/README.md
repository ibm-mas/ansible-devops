ocp_verify
==========

This role will verify that the target OCP cluster is ready to be setup for MAS.

For example, in IBMCloud ROKS we have seen delays of over an hour before the Red Hat Operator catalog is ready to use.  This will cause attempts to install anything from that CatalogSource to fail as the timeouts built into the roles in this collection are designed to catch problems with an install, rather than a half-provisioned cluster that is not properly ready to use yet.


Role Variables
--------------

### verify_cluster
Enables verification that the cluster is healthy and ready to use.  This check runs against the `ClusterVersion` resource and expects the `Ready` condition to be set to true.  If the cluster is not ready within 1 hour the verification will fail.

- Optional
- Environment Variable: `VERIFY_CLUSTER`
- Default Value: `True`

### verify_catalogsources
Enables verification that all installed catalog sources are healthy.  If any `CatalogSources` are not reporting `lastObservedState` as `READY` after 30 minutes then the verification will fail.

- Optional
- Environment Variable: `VERIFY_CATALOGSOURCES`
- Default Value: `True`

### verify_subscriptions
Enables verification that all operator subscriptions are up to date.  If any `Subscriptions` are not reporting `state` as `AtLatestKnown` after 5 hours then the verification will fail.

- Optional
- Environment Variable: `VERIFY_SUBSCRIPTIONS`
- Default Value: `True`

### verify_workloads
Enables verification that all operator subscriptions are up to date.  If any `Deployments` or `StatefulSets` are not reporting `updatedReplicas` & `availableReplicas` equal to `replicas`after 10 hours then the verification will fail.

- Optional
- Environment Variable: `VERIFY_WORKLOADS`
- Default Value: `True`

### verify_ingress
Enables verification that the cluster ingress TLS certificate can be ontained.  This is required by a number of roles in the collection.

- Optional
- Environment Variable: `VERIFY_INGRESS`
- Default Value: `True`

### cluster_name
Specify the name of the cluster, in some cluster setups this name is required to determine the name of the default router certificate.

- Optional, only used when `verify_ingress` is enabled
- Environment Variable: `CLUSTER_NAME`
- Default Value: None

### ocp_ingress_tls_secret_name
Specify the name of the cluster's ingres tls secret which contains the default router certificate.

- Optional, only used when `verify_ingress` is enabled
- Environment Variable: `OCP_INGRESS_TLS_SECRET_NAME`
- Default Value: `router-certs-default`


Example Playbook
----------------

```yaml
- hosts: localhost
  vars:
    verify_cluster: True
    verify_catalogsources: True
    verify_subscriptions: True
    verify_workloads: True
    verify_ingress: True
  roles:
    - ibm.mas_devops.ocp_verify
```


License
-------

EPL-2.0
