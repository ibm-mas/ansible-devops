# registry

Create a Docker Registry running on RedHat OpenShift cluster.  The registry will be backed by persistant storage, and accessible via either a clusterIP or loadbalancer service. This role can also be used to delete a docker registry on a cluster for a clean start. See usage below for more information.


## Usage
If you set up the registry with a **loadbalancer** service you will be able to push to the registry via the cluster's hostname, but before you can use the registry you will need to install the registry's CA certificate and restart the Docker daemon so that your client trusts the new registry:

```bash
CACERT=$(oc -n airgap-registry get secret airgap-registry-certificate -o jsonpath='{.data.ca\.crt}' | base64 -d)
DOMAIN=$(oc get ingress.config cluster -o jsonpath='{.spec.domain}')
sudo mkdir -p /etc/docker/certs.d/$DOMAIN\:32500/
sudo echo "$CACERT" > /etc/docker/certs.d/$DOMAIN\:32500/ca.crt
sudo service docker restart
```

You can now use the registry as normal:

```bash
DOMAIN=$(oc get ingress.config cluster -o jsonpath='{.spec.domain}')
docker pull registry.access.redhat.com/ubi8/ubi-minimal
docker tag registry.access.redhat.com/ubi8/ubi-minimal $DOMAIN:32500/ubi8/ubi-minimal
docker push $DOMAIN:32500/ubi8/ubi-minimal
```

If you set up the registry with a **clusterip** service you will only be able to push to the registry after using port forwarding:

```bash
oc -n airgap-registry port-forward deployment/airgap-registry 9000:5000

docker pull registry.access.redhat.com/ubi8/ubi-minimal
docker tag registry.access.redhat.com/ubi8/ubi-minimal localhost:9000/ubi8/ubi-minimal
docker push localhost:9000/ubi8/ubi-minimal
```

However, you will still need to set up Docker trust for the "local" registry:

```bash
CACERT=$(oc -n airgap-registry get secret airgap-registry-certificate -o jsonpath='{.data.ca\.crt}' | base64 -d)
sudo mkdir -p /etc/docker/certs.d/$DOMAIN\:32500/
sudo mkdir /etc/docker/certs.d/localhost\:9000
sudo echo "$CACERT" > /etc/docker/certs.d/localhost\:9000/ca.crt
sudo service docker restart
```

Usage for tear-down action
This role can also be used to permanently delete a mirror registry from a given cluster by setting the `registry_action` to `tear-down` and specifying the corresponding `registry_namespace`, if not using the default value.

Note that the tear-down action deletes the registry completely including the PVC storage and the registry namespace. To start up the registry again, the role needs to be run again with the registry_action on default or `setup`. Images previously stored in the registry before the tear-down will no longer be available and will need to be mirrored again once the registry setup has completed. Take precaution when using this function and expect that images can no longer be accessed from the registry that has been torn down.

**Note:** Recreating the registry will also create a new ca cert for the new registry.

An appropriate time to use this tear-down function is when the registry has too many images that are not being used or when there has been a shift to support newer versions but images of older versions are clogging the registry. The tear-down function frees the disk space and allows for a new registry to be setup.


## Role Variables

### registry_action
Action to perform with the registry deployment.

- Optional
- Environment Variable: `REGISTRY_ACTION`
- Default: `setup`

**Purpose**: Controls whether to set up a new registry or tear down an existing one.

**When to use**: Set to `tear-down` when you need to completely remove a registry to free disk space or start fresh. Use default `setup` for normal installation.

**Valid values**:
- `setup` - Install and configure the registry
- `tear-down` - Permanently delete the registry, namespace, and all stored images

**Impact**: The `tear-down` action is destructive and irreversible. All images stored in the registry will be lost, and the PVC storage will be deleted. A new CA certificate will be generated if the registry is recreated.

**Related variables**: [`registry_namespace`](#registry_namespace)

**Notes**:
- Use tear-down when the registry contains too many unused images or when migrating to newer versions
- After tear-down, you must re-mirror all required images
- Docker clients will need to trust the new CA certificate after recreation

### registry_namespace
Namespace where the Docker registry will be deployed.

- Optional
- Environment Variable: `REGISTRY_NAMESPACE`
- Default: `airgap-registry`

**Purpose**: Isolates the registry resources in a dedicated namespace for organization and access control.

**When to use**: Override the default if you have namespace naming conventions or need multiple registries in the same cluster.

**Valid values**: Any valid Kubernetes namespace name (lowercase alphanumeric and hyphens)

**Impact**: All registry resources (deployment, service, PVC, secrets) will be created in this namespace. The namespace will be deleted during tear-down operations.

**Related variables**: [`registry_action`](#registry_action)

**Notes**: Ensure the namespace name doesn't conflict with existing namespaces in your cluster.

### registry_storage_class
Storage class for the registry's persistent volume.

- **Required** (except on IBM Cloud ROKS where it defaults to `ibmc-block-gold`)
- Environment Variable: `REGISTRY_STORAGE_CLASS`
- Default: None (IBM Cloud ROKS: `ibmc-block-gold`)

**Purpose**: Provides persistent storage for container images stored in the registry.

**When to use**: Must be specified for all non-ROKS clusters. On ROKS, the default is usually appropriate unless you have specific performance requirements.

**Valid values**: Any storage class name available in your cluster that supports ReadWriteOnce (RWO) access mode. Common examples:
- IBM Cloud ROKS: `ibmc-block-gold`, `ibmc-block-silver`, `ibmc-block-bronze`
- AWS: `gp2`, `gp3`, `io1`
- Azure: `managed-premium`, `managed-standard`
- On-premises: Depends on your storage provider

**Impact**: Determines the performance characteristics and availability of the registry storage. The storage class must support RWO access mode.

**Related variables**: [`registry_storage_capacity`](#registry_storage_capacity)

**Notes**:
- Verify the storage class exists before deployment: `oc get storageclass`
- The storage class cannot be changed after initial deployment without recreating the registry

### registry_storage_capacity
Size of the persistent volume claim for registry storage.

- Optional
- Environment Variable: `REGISTRY_STORAGE_CAPACITY`
- Default: `100Gi`

**Purpose**: Allocates disk space for storing container images in the registry.

**When to use**: Increase from the default based on the number and size of images you plan to store. Consider your mirroring requirements and image retention policies.

**Valid values**: Any valid Kubernetes storage size (e.g., `100Gi`, `500Gi`, `1Ti`). Must be supported by your storage class.

**Impact**: Determines how many images can be stored before the registry runs out of space. Insufficient capacity will cause push operations to fail.

**Related variables**: [`registry_storage_class`](#registry_storage_class)

**Notes**:
- Plan for growth - container images can be large (1-5GB each)
- Monitor usage regularly: `oc get pvc -n <registry_namespace>`
- Expanding PVC size after deployment depends on your storage class capabilities
- For airgap environments, calculate total size of all images to be mirrored plus 20% buffer

### registry_service_type
Service type for exposing the registry.

- Optional
- Environment Variable: `REGISTRY_SERVICE_TYPE`
- Default: `loadbalancer`

**Purpose**: Controls how the registry is exposed for access from Docker clients.

**When to use**:
- Use `loadbalancer` (default) when you need to push images from outside the cluster
- Use `clusterip` when you only need internal cluster access or will use port-forwarding

**Valid values**:
- `loadbalancer` - Exposes registry externally via cluster domain on port 32500
- `clusterip` - Internal cluster access only (requires port-forwarding for external access)

**Impact**:
- **loadbalancer**: Enables direct external access via `<cluster-domain>:32500`, but requires port 32500 to be available
- **clusterip**: More secure (no external exposure) but requires `oc port-forward` for each push operation

**Related variables**: None

**Notes**:
- **LIMITATION**: The loadbalancer port (32500) cannot be customized. If port 32500 is already in use by another service, you must use `clusterip` mode
- With loadbalancer, you must install the registry's CA certificate on your Docker client (see Usage section)
- With clusterip, you still need to configure Docker trust for localhost:9000 (see Usage section)


## Example Playbook

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    registry_storage_class: ibmc-block-gold
    registry_storage_capacity: 500Gb
    registry_service_type: loadbalancer
  roles:
    - ibm.mas_devops.registry
```

## License

EPL-2.0
