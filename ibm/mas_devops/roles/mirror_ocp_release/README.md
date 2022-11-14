mirror_ocp_release
===============================================================================
This role mirrors container images for a specified OpenShift release to a target registry.

When mirroring is complete, you can view the content of your registry:

```bash
curl -k https://$REGISTRY_PUBLIC_HOST/v2/_catalog | jq
```


Requirements
-------------------------------------------------------------------------------
- `oc` tool must be installed


Role Variables
-------------------------------------------------------------------------------
### openshift_release_version
The OpenShift release to mirror.

- **Required**
- Environment Variable: `OPENSHIFT_RELEASE_VERSION`
- Default Value: None

### mirror_mode

- **Required**
- Environment Variable: `MIRROR_MODE`
- Default Value: None

### mirror_working_dir

- **Required** unless `mirror_mode` is set to `direct`
- Environment Variable: `MIRROR_WORKING_DIR`
- Default Value: None

### registry_public_host

- **Required** unless `mirror_mode` is set to `to-filesystem`
- Environment Variable: `REGISTRY_PUBLIC_HOST`
- Default Value: None

### registry_public_port

- **Required** unless `mirror_mode` is set to `to-filesystem`
- Environment Variable: `REGISTRY_PUBLIC_PORT`
- Default Value: None

### registry_username

- **Required** unless `mirror_mode` is set to `to-filesystem`
- Environment Variable: `REGISTRY_USERNAME`
- Default Value: None

### registry_password

- **Required** unless `mirror_mode` is set to `to-filesystem`
- Environment Variable: `REGISTRY_PASSWORD`
- Default Value: None

### redhat_pullsecret
Obtain your pull secret from [https://console.redhat.com/openshift/install/pull-secret](https://console.redhat.com/openshift/install/pull-secret).

- **Required** unless `mirror_mode` is set to `from-filesystem`
- Environment Variable: `REDHAT_PULLSECRET`
- Default Value: None


Example Playbook
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  vars:
    openshift_release_version: 4.10.0
    registry_public_host: myocp-5f1320191125833da1cac8216c06779e-0000.us-south.containers.appdomain.cloud
    registry_public_port: 32500

    registry_username: user
    registry_password: passwd

    mirror_mode: direct
    redhat_pullsecret: /home/me/redhat-pullsecret.json

  roles:
    - ibm.mas_devops.mirror_ocp_release
```


License
-------------------------------------------------------------------------------

EPL-2.0
