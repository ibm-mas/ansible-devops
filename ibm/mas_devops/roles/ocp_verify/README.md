ocp_verify
==========

This role will verify that the target OCP cluster is ready to be setup for MAS.

For example, in IBMCloud ROKS we have seen delays of over an hour before the Red Hat Operator catalog is ready to use.  This will cause attempts to install anything from that CatalogSource to fail as the timeouts built into the roles in this collection are designed to catch problems with an install, rather than a half-provisioned cluster that is not properly ready to use yet.


Role Variables
--------------

### verify_cluster
Enable cluster health verification.

- **Optional**
- Environment Variable: `VERIFY_CLUSTER`
- Default: `true`

**Purpose**: Verifies that the OCP cluster is healthy and ready to use by checking the ClusterVersion resource Ready condition.

**When to use**:
- Leave as `true` (default) for comprehensive cluster verification
- Set to `false` only to skip cluster health checks
- Recommended to keep enabled for production deployments

**Valid values**: `true`, `false`

**Impact**: 
- `true`: Verifies cluster Ready condition (fails if not ready within 1 hour)
- `false`: Skips cluster health verification

**Related variables**:
- Other `verify_*` variables control additional verification checks

**Note**: This check ensures the cluster is fully provisioned and ready. In some environments (e.g., IBMCloud ROKS), clusters may take time to become fully ready. The 1-hour timeout accommodates typical provisioning delays.

### verify_catalogsources
Enable catalog source health verification.

- **Optional**
- Environment Variable: `VERIFY_CATALOGSOURCES`
- Default: `true`

**Purpose**: Verifies that all installed OCP catalog sources are healthy and ready to provide operators.

**When to use**:
- Leave as `true` (default) for comprehensive verification
- Set to `false` only to skip catalog source checks
- Critical for ensuring operator installation will succeed

**Valid values**: `true`, `false`

**Impact**: 
- `true`: Verifies all CatalogSources report `lastObservedState` as `READY` (fails if not ready within 30 minutes)
- `false`: Skips catalog source verification

**Related variables**:
- `verify_cluster`: Cluster-level health check
- `verify_subscriptions`: Operator subscription verification

**Note**: Catalog sources must be ready before operators can be installed. In some environments (e.g., IBMCloud ROKS), catalog sources may take time to sync. The 30-minute timeout accommodates typical delays. This check prevents operator installation failures due to unavailable catalogs.

### verify_subscriptions
Enable operator subscription verification.

- **Optional**
- Environment Variable: `VERIFY_SUBSCRIPTIONS`
- Default: `true`

**Purpose**: Verifies that all operator subscriptions are up to date and at their latest known version.

**When to use**:
- Leave as `true` (default) for comprehensive verification
- Set to `false` only to skip subscription checks
- Important for ensuring operators are properly installed

**Valid values**: `true`, `false`

**Impact**: 
- `true`: Verifies all Subscriptions report `state` as `AtLatestKnown` (fails if not ready within 5 hours)
- `false`: Skips subscription verification

**Related variables**:
- `verify_catalogsources`: Catalog source health (prerequisite)
- `verify_workloads`: Workload deployment verification

**Note**: Subscriptions must be at latest known version before operators are fully functional. The 5-hour timeout accommodates operator installation and upgrade processes. This check ensures operators are properly installed and ready to manage resources.

### verify_workloads
Enable workload deployment verification.

- **Optional**
- Environment Variable: `VERIFY_WORKLOADS`
- Default: `true`

**Purpose**: Verifies that all deployments and statefulsets are fully rolled out with all replicas updated and available.

**When to use**:
- Leave as `true` (default) for comprehensive verification
- Set to `false` only to skip workload checks
- Critical for ensuring cluster workloads are healthy

**Valid values**: `true`, `false`

**Impact**: 
- `true`: Verifies all Deployments and StatefulSets have `updatedReplicas` and `availableReplicas` equal to `replicas` (fails if not ready within 10 hours)
- `false`: Skips workload verification

**Related variables**:
- `verify_subscriptions`: Operator subscription verification (prerequisite)
- `verify_cluster`: Cluster-level health check

**Note**: Workloads must be fully deployed before the cluster is ready for MAS installation. The 10-hour timeout accommodates large-scale deployments and rolling updates. This check ensures all pods are running and ready.

### verify_ingress
Enable ingress TLS certificate verification.

- **Optional**
- Environment Variable: `VERIFY_INGRESS`
- Default: `true`

**Purpose**: Verifies that the cluster ingress TLS certificate can be obtained. This certificate is required by multiple roles in the collection.

**When to use**:
- Leave as `true` (default) for comprehensive verification
- Set to `false` only to skip ingress certificate checks
- Required for roles that need cluster ingress certificate

**Valid values**: `true`, `false`

**Impact**: 
- `true`: Verifies ingress TLS certificate can be retrieved
- `false`: Skips ingress certificate verification

**Related variables**:
- `cluster_name`: Cluster name for certificate lookup
- `ocp_ingress_tls_secret_name`: Secret name containing certificate

**Note**: Many roles in this collection require the cluster ingress certificate. This check ensures the certificate is accessible before proceeding with MAS installation.

### cluster_name
Cluster name for ingress certificate lookup.

- **Optional** (only used when `verify_ingress=true`)
- Environment Variable: `CLUSTER_NAME`
- Default: None

**Purpose**: Specifies the cluster name used to determine the default router certificate name in certain cluster configurations.

**When to use**:
- Only required when `verify_ingress=true`
- Set when cluster setup requires cluster name for certificate lookup
- Leave unset if certificate can be found without cluster name

**Valid values**: String matching your cluster name

**Impact**: Used to construct the ingress TLS secret name in cluster configurations where the secret name includes the cluster name.

**Related variables**:
- `verify_ingress`: Must be `true` for this variable to be used
- `ocp_ingress_tls_secret_name`: Alternative way to specify certificate secret

**Note**: Only needed in specific cluster configurations. Most clusters use the default secret name and don't require this variable.

### ocp_ingress_tls_secret_name
Ingress TLS secret name.

- **Optional** (only used when `verify_ingress=true`)
- Environment Variable: `OCP_INGRESS_TLS_SECRET_NAME`
- Default: `router-certs-default`

**Purpose**: Specifies the name of the Kubernetes secret containing the cluster's default router certificate.

**When to use**:
- Only applies when `verify_ingress=true`
- Use default (`router-certs-default`) for most clusters
- Override only if your cluster uses a different secret name

**Valid values**: String matching the secret name in `openshift-ingress` namespace

**Impact**: Determines which secret is checked for the ingress TLS certificate. Incorrect name will cause verification to fail.

**Related variables**:
- `verify_ingress`: Must be `true` for this variable to be used
- `cluster_name`: Alternative way to determine secret name

**Note**: The default `router-certs-default` works for most OCP clusters. Only override if your cluster uses a custom ingress certificate secret name.


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
