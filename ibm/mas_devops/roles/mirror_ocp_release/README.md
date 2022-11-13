case_mirror
===========
This role uses the specifed OpenShift Release to mirror the OpenShift release container images to the mirror registry and configure the cluster to pull images from this mirror.

When mirroring is complete, you can view the content of your registry:

```bash
curl -k https://$REGISTRY_PUBLIC_HOST/v2/_catalog | jq
```

Requirements
------------
- `oc` tool must be installed


Role Variables
--------------

- `openshift_release_version` The version of standard operators to be mirrored.
- `log_dir` The directory to write output log.
- `ibm_entitlement_key` The entitlement key for mirroring container images from cp.icr.io.
- `redhat_connect_username` The username for accessing Red Hat docker images.
- `redhat_connect_password` The password for accessing Red Hat docker images.
- `registry_public_host` The public hostname for the target registry (defaults to the value of the REGISTRY_PUBLIC_HOST environment variable).
- `registry_public_port` The public port number for the target registry (defaults to the value of the REGISTRY_PUBLIC_PORT environment variable).
- `registry_username` The username for the target registry (defaults to the value of the REGISTRY_USERNAME environment variable).
- `registry_password` The password for the target registry (defaults to the value of the REGISTRY_PASSWORD environment variable).


Example Playbook
----------------

```yaml
- hosts: localhost
  vars:
    openshift_release_version: 4.8.39
    registry_public_host: myocp-5f1320191125833da1cac8216c06779e-0000.us-south.containers.appdomain.cloud
    registry_public_port: 32500

  roles:
    - ibm.mas_airgap.ocp_release_mirror
```


License
-------

EPL-2.0
