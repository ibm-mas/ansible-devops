# ocp_node_config

Configure individual OpenShift nodes with custom labels and taints to control workload placement. This role enables creation of dedicated nodes for specific workloads (e.g., Db2, MongoDB, compute-intensive applications) by applying Kubernetes node selectors and taints.

Use labels to direct workloads to specific nodes and taints to prevent unwanted workloads from running on dedicated nodes. This is essential for performance isolation, resource management, and meeting specific hardware requirements.

**Verification**: Use the following command to verify labels and taints:

```bash
oc get pods --all-namespaces -o wide --field-selector spec.nodeName=<node-name>
```

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`ocp_node_name`](#ocp_node_name) | Conditional | None |
| [`ocp_node_index`](#ocp_node_index) | Conditional | None |
| [`ocp_node_label_keys`](#ocp_node_label_keys) | No | None |
| [`ocp_node_label_values`](#ocp_node_label_values) | No | None |
| [`ocp_node_taint_keys`](#ocp_node_taint_keys) | No | None |
| [`ocp_node_taint_values`](#ocp_node_taint_values) | No | None |
| [`ocp_node_taint_effects`](#ocp_node_taint_effects) | No | None |

Either `ocp_node_name` or `ocp_node_index` must be set to identify the target node. When `ocp_node_label_keys` or `ocp_node_taint_keys` are set, the corresponding values/effects variables must provide the same number of entries.

### Node Selection

#### ocp_node_name

Node name to configure with labels and/or taints — a valid OpenShift node name, for example `worker-0.example.com` or `10.172.168.89`. Node names may be hostnames, IP addresses, or cloud provider identifiers; list them with `oc get nodes`.

- **Optional** (but one of `ocp_node_name` or `ocp_node_index` is required)
- Environment Variable: `OCP_NODE_NAME`
- Default: None

Use when you know the exact node name — the preferred method for production environments where node names are predictable. An incorrect node name will cause the role to fail.

!!! important
    Specify either `ocp_node_name` OR `ocp_node_index` to identify the target node. If both are specified, `ocp_node_index` takes priority. If neither is specified, the role will fail.

#### ocp_node_index

Zero-based index of the node in the cluster's node list — a non-negative integer, where `0` refers to the first node in the alphabetically sorted list.

- **Optional** (but one of `ocp_node_name` or `ocp_node_index` is required)
- Environment Variable: `OCP_NODE_INDEX`
- Default: None

Useful in automation scenarios where node names are not known in advance, or when configuring nodes sequentially. Takes priority over `ocp_node_name` if both are set. An index out of range will cause the role to fail; the node order may change if nodes are added or removed, so this is less reliable than node name for production use.

### Node Labels

#### ocp_node_label_keys

Comma-separated list of label keys to add to the selected node — valid Kubernetes label keys (alphanumeric plus dash, underscore, or dot; 63 characters or less), for example `workload` or `storage-type,gpu-enabled`.

- **Optional**
- Environment Variable: `OCP_NODE_LABEL_KEYS`
- Default: None

Labels are used by pod node selectors (`nodeSelector` or `nodeAffinity`) to direct workloads to specific nodes. The number of keys must match the number of values in [`ocp_node_label_values`](#ocp_node_label_values). Common label keys: `workload`, `node-role`, `storage-type`, `hardware-type`. Labels are additive — existing labels are not removed.

#### ocp_node_label_values

Comma-separated list of label values corresponding to the label keys — valid Kubernetes label values (alphanumeric plus dash, underscore, or dot; 63 characters or less), for example `db2` or `ssd,true`.

- **Optional**
- Environment Variable: `OCP_NODE_LABEL_VALUES`
- Default: None

Required when [`ocp_node_label_keys`](#ocp_node_label_keys) is set, providing exactly one value for each key. Order matters — the first value pairs with the first key, and so on. For example, keys=`workload,storage` with values=`db2,ssd` creates the labels `workload=db2` and `storage=ssd`. Common label values: `db2`, `mongodb`, `compute`, `storage`.

### Node Taints

#### ocp_node_taint_keys

Comma-separated list of taint keys to add to the selected node — valid Kubernetes taint keys, for example `dedicatedDb2Node` or `gpu-workload,high-memory`.

- **Optional**
- Environment Variable: `OCP_NODE_TAINT_KEYS`
- Default: None

Taints prevent pods without matching tolerations from being scheduled on the node, and are more restrictive than labels. The number of keys must match the number of entries in [`ocp_node_taint_values`](#ocp_node_taint_values) and [`ocp_node_taint_effects`](#ocp_node_taint_effects). Common taint keys: `dedicatedDb2Node`, `dedicatedMongoNode`, `gpu-required`.

#### ocp_node_taint_values

Comma-separated list of taint values corresponding to the taint keys — for example `masinst1` or `prod-db,gpu-cluster`, typically identifying which workload or instance the node is dedicated to.

- **Optional**
- Environment Variable: `OCP_NODE_TAINT_VALUES`
- Default: None

Required when [`ocp_node_taint_keys`](#ocp_node_taint_keys) is set, providing exactly one value for each key — the counts must match across keys, values, and effects. For example, key=`dedicatedDb2Node` with value=`masinst1` and effect=`NoExecute` dedicates the node to masinst1's Db2.

#### ocp_node_taint_effects

Comma-separated list of taint effects defining how each taint impacts pod scheduling — `NoSchedule`, `PreferNoSchedule`, or `NoExecute`.

- **Optional**
- Environment Variable: `OCP_NODE_TAINT_EFFECTS`
- Default: None

Required when [`ocp_node_taint_keys`](#ocp_node_taint_keys) is set, with one effect per key:

- `NoSchedule`: new pods without tolerations will not be scheduled, but existing pods remain — common for gradual migration to dedicated nodes
- `PreferNoSchedule`: the scheduler tries to avoid placing pods without tolerations, but it is not guaranteed — least restrictive, useful for soft preferences
- `NoExecute`: new pods without tolerations will not be scheduled, and existing pods without tolerations are evicted — the strongest enforcement, and the most disruptive; use it for Db2 dedicated nodes to ensure no other workloads run

## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # Turn this worker node into a dedicated Db2 worker node
    ocp_node_name: "10.172.168.89"

    # Add the label that will be applied to all dedicated Db2 nodes
    # this will be used to direct Db2 workloads to these nodes
    ocp_node_label_keys: workload
    ocp_node_label_values: db2

    # Set a taint preventing anything other than Db2 workloads for masinst1 running
    # on this node specific Db2 node
    ocp_node_taint_keys: dedicatedDb2Node
    ocp_node_taint_values: masinst1
    ocp_node_taint_effects: NoExecute

  roles:
    - ibm.mas_devops.ocp_node_config
```

## License

EPL-2.0
