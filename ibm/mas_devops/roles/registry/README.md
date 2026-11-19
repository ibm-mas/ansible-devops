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

| Variable | Required | Default |
|----------|----------|---------|
| [`registry_action`](#registry_action) | No | `setup` |
| [`registry_namespace`](#registry_namespace) | No | `airgap-registry` |
| [`registry_username`](#registry_username) | Conditional | None |
| [`registry_password`](#registry_password) | Conditional | None |
| [`registry_storage_class`](#registry_storage_class) | Conditional | None |
| [`registry_storage_capacity`](#registry_storage_capacity) | No | `2000Gi` |
| [`registry_service_type`](#registry_service_type) | No | `loadbalancer` |

`registry_username` and `registry_password` are required for the `setup` action. `registry_storage_class` is required on all clusters except IBM Cloud ROKS, where it defaults to `ibmc-block-gold`.

### Registry Deployment

#### registry_action

Action to perform with the registry deployment — `setup` to install and configure the registry (default), or `tear-down` to permanently delete the registry, namespace, and all stored images.

- **Optional**
- Environment Variable: `REGISTRY_ACTION`
- Default: `setup`

!!! warning
    The `tear-down` action is destructive and irreversible. All images stored in the registry will be lost, the PVC storage will be deleted, and a new CA certificate will be generated if the registry is recreated — Docker clients will need to trust the new CA certificate after recreation, and you must re-mirror all required images.

Use tear-down when the registry contains too many unused images or when migrating to newer versions; see the Usage section above for more details.

#### registry_namespace

Namespace where the Docker registry will be deployed — any valid Kubernetes namespace name (lowercase alphanumeric and hyphens).

- **Optional**
- Environment Variable: `REGISTRY_NAMESPACE`
- Default: `airgap-registry`

All registry resources (deployment, service, PVC, secrets) are created in this namespace, which is deleted during tear-down operations. Override the default if you have namespace naming conventions or need multiple registries in the same cluster, and ensure the name doesn't conflict with existing namespaces in your cluster.

### Registry Authentication

#### registry_username

Username for authenticating pushes to the registry, used to generate the htpasswd authentication file.

- **Required** for the `setup` action
- Environment Variable: `REGISTRY_USERNAME`
- Default: None

#### registry_password

Password for authenticating pushes to the registry, used together with `registry_username` to generate the htpasswd authentication file.

- **Required** for the `setup` action
- Environment Variable: `REGISTRY_PASSWORD`
- Default: None

### Storage

#### registry_storage_class

Storage class for the registry's persistent volume — any storage class name available in your cluster that supports ReadWriteOnce (RWO) access mode. Common examples: **IBM Cloud ROKS** `ibmc-block-gold`, `ibmc-block-silver`, `ibmc-block-bronze`; **AWS** `gp2`, `gp3`, `io1`; **Azure** `managed-premium`, `managed-standard`; on-premises depends on your storage provider.

- **Required** (except on IBM Cloud ROKS where it defaults to `ibmc-block-gold`)
- Environment Variable: `REGISTRY_STORAGE_CLASS`
- Default: None (IBM Cloud ROKS: `ibmc-block-gold`)

Must be specified for all non-ROKS clusters; on ROKS the default is usually appropriate unless you have specific performance requirements. Verify the storage class exists before deployment with `oc get storageclass` — it cannot be changed after initial deployment without recreating the registry.

#### registry_storage_capacity

Size of the persistent volume claim for registry storage — any valid Kubernetes storage size (e.g., `100Gi`, `500Gi`, `1Ti`) supported by your storage class.

- **Optional**
- Environment Variable: `REGISTRY_STORAGE_CAPACITY`
- Default: `2000Gi`

Determines how many images can be stored before the registry runs out of space; insufficient capacity will cause push operations to fail. Plan for growth — container images can be large (1-5GB each) — monitor usage with `oc get pvc -n <registry_namespace>`, and note that expanding the PVC after deployment depends on your storage class capabilities. For airgap environments, calculate the total size of all images to be mirrored plus a 20% buffer.

### Service Exposure

#### registry_service_type

Service type for exposing the registry — `loadbalancer` to expose the registry externally via the cluster domain on port 32500 (default), or `clusterip` for internal cluster access only (requires port-forwarding for external access).

- **Optional**
- Environment Variable: `REGISTRY_SERVICE_TYPE`
- Default: `loadbalancer`

`loadbalancer` enables direct external access via `<cluster-domain>:32500`; `clusterip` is more secure (no external exposure) but requires `oc port-forward` for each push operation. With either service type you must configure Docker trust for the registry's CA certificate on your client (see the Usage section).

!!! warning
    The loadbalancer port (32500) cannot be customized. If port 32500 is already in use by another service, you must use `clusterip` mode.

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
