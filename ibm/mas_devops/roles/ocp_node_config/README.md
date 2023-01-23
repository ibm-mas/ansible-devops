ocp_node_config
===============================================================================
Use the following command to verify the effect of any labels and taints that you apply to a node:

```
oc get pods --all-namespaces -o wide --field-selector spec.nodeName=xxx
```


Role Variables - Node Selection
-------------------------------------------------------------------------------
Use either `ocp_node_name` or `ocp_node_index` to identify the node to be modified.  If you specify both then the index will take priority over the name, if you specify neither then the role will fail to execute.

### ocp_node_name
The name of the node to work with

- Optional
- Environment Variable: `OCP_NODE_NAME`
- Default: None

### ocp_node_index
The index (in the list of nodes) of the node to work with.  Note that the index starts at 0 (so use `ocp_node_index=0` if you want to work with the first node).

- Optional
- Environment Variable: `OCP_NODE_INDEX`
- Default: None


Role Variables - Node Labels
-------------------------------------------------------------------------------
### ocp_node_label_keys
A comma-seperated list of labels to add to the selected node

- Optional
- Environment Variable: `OCP_NODE_LABEL_KEYS`
- Default: None

### ocp_node_label_values
A comma-seperated list of values for the labels being created

- Optional
- Environment Variable: `OCP_NODE_LABEL_VALUES`
- Default: None


Role Variables - Node Taints
-------------------------------------------------------------------------------
### ocp_node_taint_keys
A comma-seperated list of taints to add to the selected node

- Optional
- Environment Variable: `OCP_NODE_TAINT_KEYS`
- Default: None

### ocp_node_taint_values
A comma-seperated list of values for the taints being created

- Optional
- Environment Variable: `OCP_NODE_TAINT_VALUES`
- Default: None

### ocp_node_taint_effects
A comma-seperated list of taint effects to set:

- `NoSchedule`: New pods will not be scheduled onto the node
- `PreferNoSchedule`: New pods *try* not to be scheduled onto the node
- `NoExecute`: New pods are not schedules onto the node, existing pods are removed

- Optional
- Environment Variable: `OCP_NODE_TAINT_EFFECTS`
- Default: None


Example Playbook
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    ocp_node_label_keys: label1,label2
    ocp_node_label_values: value1,value2

    ocp_node_taint_keys: taint1,taint2
    ocp_node_taint_values: value1,value2
    ocp_node_taint_effects: NoExecute,NoSchedule

  roles:
    - ibm.mas_devops.ocp_node_config
```


License
-------------------------------------------------------------------------------

EPL-2.0
