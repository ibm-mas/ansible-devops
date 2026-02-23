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

### longhorn_namespace
Namespace for Longhorn installation.

- **Optional**
- Environment Variable: `LONGHORN_NAMESPACE`
- Default: `longhorn-system`

**Purpose**: Specifies the OpenShift namespace where Longhorn components will be deployed.

**When to use**: Use default unless you have specific namespace requirements or multiple Longhorn instances.

**Valid values**: Valid Kubernetes namespace name (lowercase alphanumeric with hyphens)

**Impact**: All Longhorn resources (deployments, services, storage classes) will be created in this namespace.

**Related variables**: None

**Notes**:
- Default `longhorn-system` is the standard namespace for Longhorn
- Namespace will be created if it doesn't exist
- Longhorn UI will be accessible at `https://longhorn-ui-{namespace}.{clusterdomain}`
- Storage classes are cluster-wide regardless of namespace

### longhorn_replica_count
Number of data replicas for Longhorn volumes.

- **Optional**
- Environment Variable: `LONGHORN_REPLICA_COUNT`
- Default: `3`

**Purpose**: Determines how many copies of volume data are stored across different nodes in the cluster, directly impacting data availability and resilience.

**When to use**:
- Use default `3` for production deployments requiring high availability
- Set to `2` for moderate availability with reduced storage overhead
- Set to `1` for development/testing environments to minimize storage requirements

**Valid values**: Integer between `1` and the number of worker nodes. Common values:
- `3` - Production (tolerates 2 node failures, recommended)
- `2` - Moderate availability (tolerates 1 node failure)
- `1` - Development only (no redundancy, data loss if node fails)

**Impact**:
- **Availability**: Higher replica count = better fault tolerance
- **Storage**: Each replica consumes storage space (3 replicas = 3x storage usage)
- **Performance**: More replicas may impact write performance slightly
- **Node Requirements**: Replica count cannot exceed number of available nodes

**Related variables**: None

**Notes**:
- Default `3` allows system to tolerate up to 2 replica failures while maintaining data integrity
- Setting to `1` sacrifices resilience for reduced storage requirements (development only)
- Replicas are distributed across different nodes for fault tolerance
- Cannot change replica count after volumes are created (requires volume recreation)
- Ensure cluster has sufficient nodes for desired replica count
- Consider storage capacity when setting replica count (3 replicas = 3x storage consumption)


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
