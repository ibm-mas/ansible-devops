registry
=======

Create a Docker Registry running on RedHat OpenShift cluster.  The registry will be backed by persistant storage, and accessible via either a clusterIP or loadbalancer service. This role can also be used to delete a docker registry on a cluster for a clean start. See usage below for more information.


Usage
--------------
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
--------------------------
This role can also be used to permanently delete a mirror registry from a given cluster by setting the `registry_action` to `tear-down` and specifying the corresponding `registry_namespace`, if not using the default value.

Note that the tear-down action deletes the registry completely including the PVC storage and the registry namespace. To start up the registry again, the role needs to be run again with the registry_action on default or `setup`. Images previously stored in the registry before the tear-down will no longer be available and will need to be mirrored again once the registry setup has completed. Take precaution when using this function and expect that images can no longer be accessed from the registry that has been torn down. 

**Note:** Recreating the registry will also create a new ca cert for the new registry.

An appropriate time to use this tear-down function is when the registry has too many images that are not being used or when there has been a shift to support newer versions but images of older versions are clogging the registry. The tear-down function frees the disk space and allows for a new registry to be setup.


Role Variables
--------------

### registry_action
The action to perform with this role. Can be set to `tear-down` to remove an existing registry and its namespace. Default is `setup`

- Optional
- Environment Variable: `REGISTRY_ACTION`
- Default Value: `setup`

### registry_namespace
The namespace where the registry to run

- Optional
- Environment Variable: `REGISTRY_NAMESPACE`
- Default Value: `airgap-registry`

### registry_storage_class
Required.  The name of the storage class to configure the MongoDb operator to use for persistent storage in the MongoDb cluster.

- **Required**, unless running in IBM Cloud ROKS, where the storage class will default to `ibmc-block-gold`.
- Environment Variable: `REGISTRY_STORAGE_CLASS`
- Default Value: None

### registry_storage_capacity
The size of the PVC that will be created for data storage in the cluster.

- Optional
- Environment Variable: `REGISTRY_STORAGE_CAPACITY`
- Default Value: `100Gi`

### registry_service_type
The type of service to set up in front of the registry, either `loadbalancer` or `clusterip`.  Using `loadbalancer` will allow you to access the registry from outside of your cluster via the cluster domain on port `32500`.  If you have other loadbalancers on the cluster that already claim port `32500` this role can not be usedbecause currently the loadbalancer port can not be customised.

- Optional
- Environment Variable: `REGISTRY_SERVICE_TYPE`
- Default Value: `loadbalancer`


Example Playbook
----------------

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

License
-------

EPL-2.0
