# ocp_verify

This role will verify that the target OCP cluster is ready to be setup for MAS.

For example, in IBMCloud ROKS we have seen delays of over an hour before the Red Hat Operator catalog is ready to use.  This will cause attempts to install anything from that CatalogSource to fail as the timeouts built into the roles in this collection are designed to catch problems with an install, rather than a half-provisioned cluster that is not properly ready to use yet.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`verify_cluster`](#verify_cluster) | No | `true` |
| [`verify_catalogsources`](#verify_catalogsources) | No | `true` |
| [`verify_subscriptions`](#verify_subscriptions) | No | `true` |
| [`verify_workloads`](#verify_workloads) | No | `true` |
| [`verify_ingress`](#verify_ingress) | No | `true` |
| [`cluster_name`](#cluster_name) | Conditional | None |
| [`ocp_ingress_tls_secret_name`](#ocp_ingress_tls_secret_name) | No | `router-certs-default` |
| [`olm_approval_mode`](#olm_approval_mode) | No | `Automatic` |
| [`olm_approval_timeout`](#olm_approval_timeout) | No | `7200` |

`cluster_name` is only used when `verify_ingress` is `true`, and is only needed in specific cluster configurations.

### OLM Install Plan Approval

#### olm_approval_mode

- **Optional**
- Environment Variable: `OLM_APPROVAL_MODE`
- Default: `Automatic`

When set to `Manual`, this role waits (cluster-wide) for any install plans awaiting human approval before checking subscription status — this is the gate for subscriptions that roll implicitly after a catalog digest update. The role never approves an install plan automatically. See [OLM Manual Install Plan Approvals](https://ibm-mas.github.io/ansible-devops/olm-manual-approvals/) for the full details.

#### olm_approval_timeout

- **Optional**
- Environment Variable: `OLM_APPROVAL_TIMEOUT`
- Default: `7200`

Seconds to wait for each individual install plan approval (per namespace) before the role fails (2 hours by default).

### Verification Checks

#### verify_cluster

Enable cluster health verification — `true` to verify the cluster is healthy and ready by checking the ClusterVersion resource Ready condition, `false` to skip (default `true`).

- **Optional**
- Environment Variable: `VERIFY_CLUSTER`
- Default: `true`

Fails if the cluster is not ready within 1 hour. This check ensures the cluster is fully provisioned and ready; in some environments (e.g., IBMCloud ROKS), clusters may take time to become fully ready, and the 1-hour timeout accommodates typical provisioning delays. Recommended to keep enabled for production deployments.

#### verify_catalogsources

Enable catalog source health verification — `true` to verify that all installed OCP catalog sources are healthy and ready to provide operators, `false` to skip (default `true`).

- **Optional**
- Environment Variable: `VERIFY_CATALOGSOURCES`
- Default: `true`

Verifies that all CatalogSources report `lastObservedState` as `READY`, failing if not ready within 30 minutes. Catalog sources must be ready before operators can be installed — this check prevents operator installation failures due to unavailable catalogs, and the 30-minute timeout accommodates typical sync delays (e.g., on IBMCloud ROKS).

#### verify_subscriptions

Enable operator subscription verification — `true` to verify that all operator subscriptions are up to date and at their latest known version, `false` to skip (default `true`).

- **Optional**
- Environment Variable: `VERIFY_SUBSCRIPTIONS`
- Default: `true`

Verifies that all Subscriptions report `state` as `AtLatestKnown`, failing if not ready within 2 hours — the timeout accommodates operator installation and upgrade processes, ensuring operators are properly installed and ready to manage resources.

#### verify_workloads

Enable workload deployment verification — `true` to verify that all deployments and statefulsets are fully rolled out, `false` to skip (default `true`).

- **Optional**
- Environment Variable: `VERIFY_WORKLOADS`
- Default: `true`

Verifies that all Deployments and StatefulSets have `updatedReplicas` and `availableReplicas` equal to `replicas`, failing if not ready within 3 hours. Workloads must be fully deployed before the cluster is ready for MAS installation; the timeout accommodates large-scale deployments and rolling updates.

#### verify_ingress

Enable ingress TLS certificate verification — `true` to verify that the cluster ingress TLS certificate can be obtained, `false` to skip (default `true`).

- **Optional**
- Environment Variable: `VERIFY_INGRESS`
- Default: `true`

Many roles in this collection require the cluster ingress certificate; this check ensures the certificate is accessible before proceeding with MAS installation.

### Ingress Certificate Lookup

#### cluster_name

Cluster name used to determine the default router certificate name in certain cluster configurations — a string matching your cluster name.

- **Optional** (only used when `verify_ingress=true`)
- Environment Variable: `CLUSTER_NAME`
- Default: None

Used to construct the ingress TLS secret name in cluster configurations where the secret name includes the cluster name. Only needed in specific configurations — most clusters use the default secret name and don't require this variable.

#### ocp_ingress_tls_secret_name

Name of the Kubernetes secret in the `openshift-ingress` namespace containing the cluster's default router certificate.

- **Optional** (only used when `verify_ingress=true`)
- Environment Variable: `OCP_INGRESS_TLS_SECRET_NAME`
- Default: `router-certs-default`

The default `router-certs-default` works for most OCP clusters — only override it if your cluster uses a custom ingress certificate secret name; an incorrect name will cause verification to fail.

## Example Playbook

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

## License

EPL-2.0
