# Role Name

Provision role creates an openshift cluster using OCP+ apis. Only quickburn cluster is supported at the moment, the plan is to include ROKS and Product Id clusters.

## Requirements
- Fyre platform account
- Access to a Product Group
- Quick Burn access
- 
## Role Variables
- `cluster_name`: Name of the cluster
- `cluster_type`: Type of the cluster (only quickburn is supported at present)
- `username`: Username to authenticate with cluster provider
- `password`: Password to authenticate with cluster provider
- `ocp_version`: OCP Version string
- `fyre_cluster_size`: Size of cluster (medium|large), only used when cluster_type is quickburn
- `fyre_product_id`: Fyre Product ID, only used when cluster_type is quickburn

## Dependencies
None

## Example Playbook
```yaml
---
- hosts: localhost
  vars:
    cluster_name: mycluster
    cluster_type: quickburn
    username: xxx
    password: xxx
    ocp_version: 4.6.16
    fyre_cluster_size: medium
    fyre_product_id: 123
  roles:
    - mas.devops.provision
```

## License
Internal use only