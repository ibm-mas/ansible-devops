ocp_idms
===============================================================================
Installs an **ImageDigestMirrorSet** (IDMS)for IBM Maximo Application Suite's Maximo Operator Catalog.  Optionally can also install a second IDMS suitable for the Red Hat Operator Catalogs created by [mirror_ocp](mirror_ocp.md).  If there are legacy **ImageContentSourcePolicies** installed by previous versions of this role, they will be deleted.

!!! warning
    This role doesn't work on IBMCloud ROKS.  IBM Cloud RedHat OpenShift Service does not implement support for `ImageDigestMirrorSet`.  If you want to use image mirroring you must manually configure each worker node individually using the IBM Cloud command line tool.


IBM Maximo Operator Catalog Content
-------------------------------------------------------------------------------
All content used in the MAS install is sourced from three registries: **icr.io**, **cp.icr.io**, & **quay.io**:

- **icr.io/cpopen** All IBM operators
- **icr.io/ibm-truststore-mgr** IBM truststore manager worker image
- **icr.io/ibm-sls** IBM SLS content
- **icr.io/ibm-uds** IBM UDS content
- **icr.io/db2u** IBM Db2 Universal operator content
- **cp.icr.io/cp** All IBM entitled container images
- **quay.io/opencloudio** IBM common services
- **quay.io/mongodb** MongoDb Community Edition Operator & associated container images
- **quay.io/amlen** Eclipse Amlen - Message Broker for IoT/Mobile/Web
- **quay.io/ibmmas** Non-product IBM Maximo Application Suite images (e.g. MAS CLI)

Red Hat Operator Catalog Content
-------------------------------------------------------------------------------
All content from the subset of the Red Hat operator catalogs supported by [mirror_ocp](mirror_ocp.md) is sourced from eight registries: **icr.io**, **docker.io**, **quay.io**, **gcr.io**, **ghcr.io**, **nvcr.io**, **registry.connect.redhat.com**, and **registry.redhat.io**:

- **icr.io/cpopen**
- **docker.io/grafana**
- **quay.io/community-operator-pipeline-prod**
- **quay.io/operator-pipeline-prod**
- **quay.io/openshift-community-operators**
- **quay.io/strimzi**
- **quay.io/rh-marketplace**
- **gcr.io/kubebuilder**
- **ghcr.io/grafana**
- **ghcr.io/open-telemetry**
- **nvcr.io/nvidia**
- **registry.connect.redhat.com/crunchydata**
- **registry.connect.redhat.com/nvidia**
- **registry.connect.redhat.com/turbonomic**
- **registry.connect.redhat.com/rh-marketplace**
- **registry.redhat.io/openshift4**
- **registry.redhat.io/source-to-image**
- **registry.redhat.io/odf4**
- **registry.redhat.io/cert-manager**
- **registry.redhat.io/rhceph**
- **registry.redhat.io/amq-streams**
- **registry.redhat.io/ubi8**
- **registry.redhat.io/openshift-pipelines**
- **registry.redhat.io/openshift-serverless-1**
- **registry.redhat.io/lvms4**

!!! note
    A content source policy for this content is only configured when **setup_redhat_catalogs** is set to `True`.

If you are managing the Red Hat Operator Catalogs yourself the content therein may well be different depending how you have configured mirroring.


Role Variables
-------------------------------------------------------------------------------
### setup_redhat_release
Instruct the role to setup **ImageDigestMirrorSet** for the mirrored release content generated by [mirror_ocp](mirror_ocp.md).  This will create an additional policy named `ibm-mas-redhat-release`.

- **Required**
- Environment Variable: `SETUP_REDHAT_RELEASE`
- Default: `False`

### setup_redhat_catalogs
Instruct the role to setup **CatalogSources** and **ImageDigestMirrorSet** for the mirror catalogs generated by [mirror_ocp](mirror_ocp.md).  This will create an additional policy named `ibm-mas-redhat-catalogs`.

- **Required**
- Environment Variable: `SETUP_REDHAT_CATALOGS`
- Default: `False`


Role Variables - Target Registry
-------------------------------------------------------------------------------
### registry_private_host
The private hostname for the target registry

- **Required**
- Environment Variable: `REGISTRY_PRIVATE_HOST`
- Default: None

### registry_private_port
The private port number for the target registry

- Optional
- Environment Variable: `REGISTRY_PRIVATE_PORT`
- Default: None

### registry_private_ca_file
The CA certificate presented by the registry on it's private endpoint.

- **Required**
- Environment Variable: `REGISTRY_PRIVATE_CA_FILE`
- Default: None

### registry_username
The username for the target registry.

- **Required**
- Environment Variable: `REGISTRY_USERNAME`
- Default: None

### registry_password
The password for the target registry.

- **Required**
- Environment Variable: `REGISTRY_PASSWORD`
- Default: None

### registry_prefix
Optional additional path prefixed to all image repositories related to the IBM Maximo Operator Catalog in the target registry.  We recommend the use of the catalog datestamp for this prefix to organize your registry, e.g. `mas-241107`, `mas-241205`.  This should match the value used when you mirrored the images with [mirror_images](mirror_images.md).

- Optional
- Environment Variable: `REGISTRY_PREFIX`
- Default: None

### registry_prefix_redhat
Optional additional path prefixed to all image repositories related to the Red Hat Release and Operator Catalogs in the target registry.  We recommend the use of the OpenShift release for this prefix to organize your registry, e.g. `ocp-412`, `ocp-414`.  This should match the value used when you mirrored the images with [mirror_ocp](mirror_ocp.md).

- **Required**
- Environment Variable: `REGISTRY_PREFIX_REDHAT`
- Default: None

### redhat_catalogs_prefix
An optional prefix to apply to the catalog sources names for the 3 Red Hat catalogs supported by this role. For example, setting a value of `ibm-mas` will result in three catalog sources named `ibm-mas-certified-operator-index`, `ibm-mas-community-operator-index`, `ibm-mas-redhat-operator-index` being created.

- Optional
- Environment Variable: `REDHAT_CATALOGS_PREFIX`
- Default: None


Example Playbook
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  vars:
    registry_private_host: myocp-5f1320191125833da1cac8216c06779e-0000.us-south.containers.appdomain.cloud
    registry_private_port: 32500
    registry_private_ca_file: ~/registry-ca.crt

    registry_username: admin
    registry_password: 8934jk77s862!  # Not a real password, don't worry security folks

    setup_redhat_catalogs: true

  roles:
    - ibm.mas_devops.ocp_contentsourcepolicy
```


License
-------------------------------------------------------------------------------

EPL-2.0