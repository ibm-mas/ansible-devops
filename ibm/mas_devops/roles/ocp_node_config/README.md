# ocp_node_config

Configure individual OpenShift nodes with custom labels and taints to control workload placement. This role enables creation of dedicated nodes for specific workloads (e.g., Db2, MongoDB, compute-intensive applications) by applying Kubernetes node selectors and taints.

Use labels to direct workloads to specific nodes and taints to prevent unwanted workloads from running on dedicated nodes. This is essential for performance isolation, resource management, and meeting specific hardware requirements.

**Verification**: Use the following command to verify labels and taints:
```bash
oc get pods --all-namespaces -o wide --field-selector spec.nodeName=<node-name>
```


## Role Variables - Node Selection

**Important**: Specify either `ocp_node_name` OR `ocp_node_index` to identify the target node. If both are specified, `ocp_node_index` takes priority. If neither is specified, the role will fail.

## Role Variables

### ocp_node_name
Node name to configure with labels and/or taints.

- Optional (but one of `ocp_node_name` or `ocp_node_index` is required)
- Environment Variable: `OCP_NODE_NAME`
- Default: None

**Purpose**: Identifies a specific node by its name for label and taint configuration.

**When to use**: Use when you know the exact node name. Preferred method for production environments where node names are predictable.

**Valid values**: Valid OpenShift node name (e.g., `worker-0.example.com`, `10.172.168.89`).

**Impact**: The specified node will be configured with the provided labels and taints. Incorrect node name will cause the role to fail.

**Related variables**: `ocp_node_index` (alternative selection method)

**Notes**:
- Get node names with: `oc get nodes`
- Node names may be hostnames, IP addresses, or cloud provider identifiers
- If both `ocp_node_name` and `ocp_node_index` are set, index takes priority

### ocp_node_index
Zero-based index of the node in the cluster's node list.

- Optional (but one of `ocp_node_name` or `ocp_node_index` is required)
- Environment Variable: `OCP_NODE_INDEX`
- Default: None

**Purpose**: Identifies a node by its position in the sorted list of cluster nodes.

**When to use**: Useful in automation scenarios where node names are not known in advance, or when configuring nodes sequentially.

**Valid values**: Non-negative integer starting from 0 (e.g., `0` for first node, `1` for second node).

**Impact**: The node at the specified index position will be configured. Index out of range will cause the role to fail.

**Related variables**: `ocp_node_name` (alternative selection method)

**Notes**:
- Index 0 refers to the first node in alphabetically sorted list
- Node order may change if nodes are added/removed
- Takes priority over `ocp_node_name` if both are set
- Less reliable than node name for production use


## Role Variables - Node Labels

### ocp_node_label_keys
Comma-separated list of label keys to add to the selected node.

- Optional
- Environment Variable: `OCP_NODE_LABEL_KEYS`
- Default: None

**Purpose**: Defines the label keys that will be applied to the node. Labels are used by pod node selectors to direct workloads to specific nodes.

**When to use**: Use to categorize nodes by workload type, hardware capabilities, or any custom classification scheme.

**Valid values**: Comma-separated list of valid Kubernetes label keys (e.g., `workload`, `storage-type,gpu-enabled`). Label keys must:
- Start and end with alphanumeric characters
- Contain only alphanumeric, dash, underscore, or dot characters
- Be 63 characters or less

**Impact**: Labels enable pod scheduling based on node selectors. Pods with matching node selectors will prefer or require these nodes.

**Related variables**: `ocp_node_label_values` (must have same number of values as keys)

**Notes**:
- Number of keys must match number of values
- Common label keys: `workload`, `node-role`, `storage-type`, `hardware-type`
- Labels are additive; existing labels are not removed
- Use with pod `nodeSelector` or `nodeAffinity` for workload placement

### ocp_node_label_values
Comma-separated list of label values corresponding to the label keys.

- Optional
- Environment Variable: `OCP_NODE_LABEL_VALUES`
- Default: None

**Purpose**: Provides the values for each label key specified in `ocp_node_label_keys`.

**When to use**: Required when `ocp_node_label_keys` is set. Must provide exactly one value for each key.

**Valid values**: Comma-separated list of valid Kubernetes label values (e.g., `db2`, `ssd,true`). Label values must:
- Start and end with alphanumeric characters
- Contain only alphanumeric, dash, underscore, or dot characters
- Be 63 characters or less

**Impact**: Combined with keys, creates complete labels (key=value pairs) on the node.

**Related variables**: `ocp_node_label_keys` (must have same number of keys as values)

**Notes**:
- Number of values must exactly match number of keys
- Order matters: first value pairs with first key, etc.
- Common label values: `db2`, `mongodb`, `compute`, `storage`
- Example: keys=`workload,storage` values=`db2,ssd` creates labels `workload=db2` and `storage=ssd`


## Role Variables - Node Taints

### ocp_node_taint_keys
Comma-separated list of taint keys to add to the selected node.

- Optional
- Environment Variable: `OCP_NODE_TAINT_KEYS`
- Default: None

**Purpose**: Defines the taint keys that will prevent pods without matching tolerations from being scheduled on the node.

**When to use**: Use to dedicate nodes to specific workloads by preventing other pods from running on them.

**Valid values**: Comma-separated list of valid Kubernetes taint keys (e.g., `dedicatedDb2Node`, `gpu-workload,high-memory`).

**Impact**: Pods without matching tolerations will not be scheduled on this node. Existing pods may be evicted depending on taint effect.

**Related variables**: `ocp_node_taint_values`, `ocp_node_taint_effects` (must have same number of entries)

**Notes**:
- Number of keys must match number of values and effects
- Taints are more restrictive than labels
- Common taint keys: `dedicatedDb2Node`, `dedicatedMongoNode`, `gpu-required`
- Pods must have matching tolerations to run on tainted nodes

### ocp_node_taint_values
Comma-separated list of taint values corresponding to the taint keys.

- Optional
- Environment Variable: `OCP_NODE_TAINT_VALUES`
- Default: None

**Purpose**: Provides the values for each taint key, typically identifying which workload or instance the node is dedicated to.

**When to use**: Required when `ocp_node_taint_keys` is set. Must provide exactly one value for each key.

**Valid values**: Comma-separated list of taint values (e.g., `masinst1`, `prod-db,gpu-cluster`).

**Impact**: Combined with keys and effects, creates complete taints that control pod scheduling.

**Related variables**: `ocp_node_taint_keys`, `ocp_node_taint_effects` (must have same number of entries)

**Notes**:
- Number of values must exactly match number of keys and effects
- Values often identify specific instances or workload identifiers
- Example: key=`dedicatedDb2Node` value=`masinst1` effect=`NoExecute` dedicates node to masinst1's Db2

### ocp_node_taint_effects
Comma-separated list of taint effects defining how the taint impacts pod scheduling.

- Optional
- Environment Variable: `OCP_NODE_TAINT_EFFECTS`
- Default: None

**Purpose**: Specifies the enforcement level for each taint, controlling both new pod scheduling and existing pod eviction.

**When to use**: Required when `ocp_node_taint_keys` is set. Choose effect based on desired behavior.

**Valid values**: Comma-separated list of taint effects:
- `NoSchedule` - New pods without tolerations will not be scheduled; existing pods remain
- `PreferNoSchedule` - Scheduler tries to avoid placing pods without tolerations; not guaranteed
- `NoExecute` - New pods without tolerations will not be scheduled; existing pods without tolerations are evicted

**Impact**:
- `NoSchedule`: Prevents new workloads but preserves existing ones
- `PreferNoSchedule`: Soft constraint, may be overridden by scheduler
- `NoExecute`: Strongest enforcement, evicts non-tolerating pods immediately

**Related variables**: `ocp_node_taint_keys`, `ocp_node_taint_values` (must have same number of entries)

**Notes**:
- Number of effects must exactly match number of keys and values
- `NoExecute` is most disruptive but ensures dedicated nodes
- `NoSchedule` is common for gradual migration to dedicated nodes
- `PreferNoSchedule` is least restrictive, useful for soft preferences
- Example: Use `NoExecute` for Db2 dedicated nodes to ensure no other workloads run


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
