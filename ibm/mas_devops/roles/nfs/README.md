nfs
===============================================================================

This role provides support to install NFS on Fyre IT only. It is not recommended to run this job in existent Fyre Openshift clusters with applications already installed and using the Image Registry PVC. The role must delete the current image registry that comes defined by default when a Fyre Openshift cluster is provisioned. If you already installed NFS and is running this role again along with other roles through playbooks, you can set the variable recreate_image_registry to false to prevent the deletion and recreation of the PVC, impacting on existent applications using it. 

The NFS installation requires the information of the Fyre Infrastructure Node Private IP. If you do not provide that by defining the value of the variable fyre_inf_node_private_ip, you must define the variables fyre_username, fyre_password and cluster_name so the Fyre Infrastructure Nnode Private IP is obtained through a Fyre API call.

Role Variables
-------------------------------------------------------------------------------

### fyre_inf_node_private_ip
Required if fyre_username, fyre_password and cluster_name are not provided.

- Environment Variable: `FYRE_INF_NODE_PRIVATE_IP`
- Default Value: None

### fyre_username
Required if fyre_inf_node_private_ip is not provided.

- Environment Variable: `FYRE_USERNAME`
- Default Value: None

### fyre_password
Required if fyre_inf_node_private_ip is not provided.

- Environment Variable: `FYRE_APIKEY`
- Default Value: None

### cluster_name
Required if fyre_inf_node_private_ip is not provided.

- Environment Variable: `CLUSTER_NAME`
- Default Value: None

### cluster_type
Type the value of the CLUSTER_TYPE, which must be fyre.

- **Required**
- Environment Variable: `CLUSTER_TYPE`
- Default: None

### recreate_image_registry
Required to set false when you are running this job through a playbook to perform other actions instead installing NFS and considering it was already previously installed. When set as true, the Image Registry PVC is going to be deleted and recreated while configuring the NFS storage class.

- Optional.
- Environment Variable: `RECREATE_IMAGE_REGISTRY`
- Default Value: `true`

### image_registry_storage_size
Defines the image registry storage size when configured to use NFS. The size allocated cannot be superior of storage available in the Fyre Infrastructure node.

- Optional.
- Environment Variable: `IMAGE_REGISTRY_STORAGE_SIZE`
- Default: `100Gi`


License
-------

EPL-2.0
