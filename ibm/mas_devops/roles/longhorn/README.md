# longhorn

Deploy Longhorn distributed block storage system for Kubernetes, providing both ReadWriteMany (RWX) and ReadWriteOnce (RWO) storage for Maximo Application Suite.

Longhorn is a lightweight, reliable, and easy-to-use distributed block storage system for Kubernetes. Originally developed by Rancher Labs, it is now an incubating project of the Cloud Native Computing Foundation (CNCF).

## Features

- **Unified Storage Solution**: Provides both RWX and RWO storage classes for MAS
- **High Availability**: Configurable replica count for data redundancy
- **Web UI**: Management interface available at `https://longhorn-ui-longhorn-system.{clusterdomain}` (OpenShift OAuth authentication)
- **Dynamic Provisioning**: Automatic volume provisioning for MAS workloads
- **Snapshot Support**: Built-in backup and snapshot capabilities

## Deployed Components

After installation, the following deployments will be available:

```bash
oc -n longhorn-system get deployments
NAME                       READY   UP-TO-DATE   AVAILABLE   AGE
csi-attacher               3/3     3            3           38m
csi-provisioner            3/3     3            3           38m
csi-resizer                3/3     3            3           38m
csi-snapshotter            3/3     3            3           38m
longhorn-driver-deployer   1/1     1            1           40m
longhorn-ui                2/2     2            2           40m
```

## Storage Classes

Two storage classes are automatically created:

```bash
oc get storageclass | grep longhorn
longhorn (default)          driver.longhorn.io   Delete          Immediate           true                   40m
longhorn-static             driver.longhorn.io   Delete          Immediate           true                   40m
```

**Note**: MAS uses dynamic provisioning with the `longhorn` storage class. The `longhorn-static` storage class is not used by MAS.

## Additional Resources

- [What is Longhorn?](https://longhorn.io/docs/latest/what-is-longhorn/)
- [Longhorn Helm Chart Settings](https://longhorn.io/docs/latest/references/helm-values/)
- [Longhorn on OpenShift](https://github.com/longhorn/longhorn/blob/master/chart/ocp-readme.md)

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`longhorn_namespace`](#longhorn_namespace) | No | `longhorn-system` |
| [`longhorn_replica_count`](#longhorn_replica_count) | No | `3` |

### Longhorn Deployment

#### longhorn_namespace

Namespace for the Longhorn installation (valid Kubernetes namespace name; created if it doesn't exist).

- **Optional**
- Environment Variable: `LONGHORN_NAMESPACE`
- Default: `longhorn-system`

All Longhorn resources (deployments, services, storage classes) are created in this namespace, and the UI is accessible at `https://longhorn-ui-{namespace}.{clusterdomain}`. Storage classes are cluster-wide regardless of namespace.

#### longhorn_replica_count

Number of data replicas for Longhorn volumes — an integer between `1` and the number of worker nodes.

- **Optional**
- Environment Variable: `LONGHORN_REPLICA_COUNT`
- Default: `3`

`3` (production, tolerates 2 node failures) is recommended; `2` tolerates 1 node failure with reduced storage overhead; `1` is development only with no redundancy. Each replica consumes storage (3 replicas = 3x storage usage) and replicas are distributed across different nodes, so ensure the cluster has enough nodes and capacity. The replica count cannot be changed after volumes are created without recreating them.

## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    longhorn_namespace: longhorn-system
    longhorn_replica_count: 3
  roles:
    - ibm.mas_devops.longhorn
```

For development environments with reduced storage requirements:

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    longhorn_namespace: longhorn-system
    longhorn_replica_count: 1
  roles:
    - ibm.mas_devops.longhorn
```

## License

EPL-2.0
