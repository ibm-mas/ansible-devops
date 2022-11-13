registry
=======

Create a Docker Registry running on RedHat OpenShift cluster.  The registry will be backed by persistant storage, and accessible via either a clusterIP or loadbalancer service.


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


Role Variables
--------------

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
    - ibm.mas_airgap.registry
```

License
-------

EPL-2.0
