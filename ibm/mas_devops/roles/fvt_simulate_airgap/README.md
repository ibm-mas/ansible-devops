fvt_simulate_airgap
===================

This role provides to support to configure a cluster for simulated airgap installation testing. This includes disabling newtwork access to public image repositories and sets up the OCP Internal Registry in preparation for image mirroring.

Role Variables
--------------

- `cluster_name` -Gives a name for the provisioned cluster
- `cluster_type` quickburn
- `username` username for fyre api
- `password` password for fyre api

#### Optional facts
- `debugs`: comma separated string of debug output to print


Example Playbook
----------------

```yaml
- hosts: localhost
  vars:
    # General configuration
    cluster_name: "{{ lookup('env', 'CLUSTER_NAME') }}"
    cluster_type: quickburn
    username: "{{ lookup('env', 'FYRE_USERNAME') }}"
    password: "{{ lookup('env', 'FYRE_APIKEY') }}"
    # Airgap control parameters:
    debugs: "registryHosts,mirrorImageResult,configureClusterResult"

  roles:
    - role: ibm.mas_devops.fvt_simulate_airgap
```

License
-------

EPL-2.0
