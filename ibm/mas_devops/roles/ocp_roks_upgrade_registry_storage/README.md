ocp_roks_upgrade_registry_storage
===============================================================================

Upgrade the storage capacity of the OpenShift image registry for IBM Cloud Red Hat OpenShift Kubernetes Service (ROKS) clusters. This role uses IBM Cloud APIs to expand the persistent volume backing the internal image registry from the default 100GB to 400GB.

**Purpose**: The default 100GB registry storage is insufficient for comprehensive Cloud Pak for Data installations or environments with many container images. This role prevents registry storage exhaustion that would block image pulls and deployments.

**Important**: This operation is specific to ROKS clusters on IBM Cloud and requires cluster downtime for the registry during the resize operation.


Role Variables
-------------------------------------------------------------------------------

### ibmcloud_apikey
IBM Cloud API key for authentication and volume management.

- **Required**
- Environment Variable: `IBMCLOUD_APIKEY`
- Default: None

**Purpose**: Provides authentication credentials for IBM Cloud APIs to modify the storage volume associated with the OpenShift image registry.

**When to use**: Always required. Must have permissions to manage storage volumes in the IBM Cloud account.

**Valid values**: Valid IBM Cloud API key string (typically 40+ characters).

**Impact**: Used to authenticate with IBM Cloud and perform volume resize operations. Insufficient permissions will cause the operation to fail.

**Related variables**: `image_registry_size`

**Notes**:
- Requires IAM permissions for Block Storage and Kubernetes Service
- API key must have access to the cluster's resource group
- Store securely, never commit to version control
- Create API key in IBM Cloud console: Manage > Access (IAM) > API keys
- Recommended: Use service ID API key rather than user API key

### image_registry_size
Target size for the image registry storage volume in GB.

- Optional
- Environment Variable: None (hardcoded in defaults)
- Default: `400`

**Purpose**: Specifies the target capacity in gigabytes for the image registry persistent volume.

**When to use**: Default 400GB is suitable for most Cloud Pak for Data installations. Adjust if you need more or less storage.

**Valid values**: Integer representing GB capacity. Common values:
- `200` - Minimal CP4D installation
- `400` - Default, suitable for full CP4D with multiple services
- `600` - Large deployments with many custom images
- `1000` - Very large environments with extensive image catalogs

**Impact**: Determines the final size of the registry volume. Larger sizes cost more but provide more capacity for container images.

**Related variables**: `ibmcloud_apikey`

**Notes**:
- Default 400GB is 4x the original 100GB capacity
- Volume can only be expanded, not shrunk
- Expansion requires registry downtime (typically 5-15 minutes)
- Consider image retention policies to manage storage usage
- Monitor registry storage: `oc get pvc -n openshift-image-registry`
- IBM Cloud charges based on provisioned storage capacity


Example Playbook
----------------

```yaml
- hosts: localhost
  roles:
    - ibm.mas_devops.ocp_roks_tuning
```


License
-------

EPL-2.0
