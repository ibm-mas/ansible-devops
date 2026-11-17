# ocp_roks_upgrade_registry_storage

Upgrade the storage capacity of the OpenShift image registry for IBM Cloud Red Hat OpenShift Kubernetes Service (ROKS) clusters. This role uses IBM Cloud APIs to expand the persistent volume backing the internal image registry from the default 100GB to 400GB.

The default 100GB registry storage is insufficient for comprehensive Cloud Pak for Data installations or environments with many container images; this role prevents the registry storage exhaustion that would block image pulls and deployments.

!!! important
    This operation is specific to ROKS clusters on IBM Cloud and requires cluster downtime for the registry during the resize operation (typically 5-15 minutes).

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`ibmcloud_apikey`](#ibmcloud_apikey) | Yes | None |
| [`image_registry_size`](#image_registry_size) | No | `400` |

### IBM Cloud Access

#### ibmcloud_apikey

IBM Cloud API key for authentication and volume management.

- **Required**
- Environment Variable: `IBMCLOUD_APIKEY`
- Default: None

The key must have IAM permissions for Block Storage and Kubernetes Service, and access to the cluster's resource group. A service ID API key is recommended over a user API key; keys can be created in the IBM Cloud console under Manage > Access (IAM) > API keys.

### Registry Storage

#### image_registry_size

Target size for the image registry storage volume, in GB.

- **Optional**
- Environment Variable: None (hardcoded in defaults)
- Default: `400`

Common values are `200` (minimal CP4D installation), `400` (default, suitable for full CP4D with multiple services), `600` (large deployments with many custom images), and `1000` (very large environments with extensive image catalogs). The volume can only be expanded, not shrunk; IBM Cloud charges based on provisioned capacity. Usage can be monitored with `oc get pvc -n openshift-image-registry`.

## Example Playbook

```yaml
- hosts: localhost
  roles:
    - ibm.mas_devops.ocp_roks_tuning
```

## License

EPL-2.0
