# ocs

Install and configure OpenShift Data Foundation (ODF) Operator, formerly known as OpenShift Container Storage (OCS), along with the Local Storage Operator (LSO) for persistent storage in OpenShift clusters.

This role provides automated installation and upgrade of ODF/OCS with local storage backend. The role automatically detects the OpenShift version and installs the appropriate operator version.

## Version Detection

- **OCP 4.10 and earlier**: Installs OCS operator
- **OCP 4.11 and later**: Installs ODF operator

## Platform Limitations

!!! warning "IBM Cloud ROKS Limitation"
    Starting from OCP 4.8, IBM/Red Hat no longer support OCS/ODF installation via OperatorHub on IBM Cloud ROKS clusters. ROKS clusters are automatically provisioned with their own storage plugin.

    If you attempt to install ODF on ROKS via OperatorHub, you will encounter this error:

    **"Failed to apply object: admission webhook 'validate.managed.openshift.io' denied the request: Installing OpenShift Data Foundation on IBM Cloud by using OperatorHub is not supported. You can install OpenShift Data Foundation by using the IBM Cloud add-on."**

    For ROKS deployments, use the [IBM Cloud add-on](https://cloud.ibm.com/docs/openshift?topic=openshift-ocs-storage-prep) instead.

## Features

- **Automatic Version Detection**: Installs OCS or ODF based on OpenShift version
- **Local Storage Integration**: Configures Local Storage Operator for block storage
- **Storage Cluster Setup**: Creates and configures ODF/OCS storage cluster
- **Upgrade Support**: Can upgrade existing ODF/OCS installations

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`lso_device_path`](#lso_device_path) | Yes | `/dev/vdb` |
| [`ocs_action`](#ocs_action) | No | `install` |

### Local Storage

#### lso_device_path

Local disk device path for block storage, used by the Local Storage Operator (e.g. `/dev/vdb` on virtual machines, `/dev/sdc` on physical servers, `/dev/nvme0n1` for NVMe drives — verify with `lsblk` on the worker nodes).

- **Required**
- Environment Variable: `LSO_DEVICE_PATH`
- Default: `/dev/vdb`

!!! danger
    The disk must be unformatted, not in use, available on all worker nodes designated for storage, and have sufficient capacity — **all data on the specified disk will be permanently erased** during storage cluster setup.

### Installation

#### ocs_action

Action to perform on the ODF/OCS installation.

- **Optional**
- Environment Variable: `OCS_ACTION`
- Default: `install`

`install` performs a fresh installation of the Local Storage Operator, ODF/OCS operator, and storage cluster; `upgrade` updates the operator subscriptions and storage cluster configuration to versions compatible with the current OpenShift version — run it after OpenShift cluster upgrades to keep storage in sync, and always back up data first.

## Example Playbook

### Fresh Installation

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    lso_device_path: /dev/vdb
    ocs_action: install
  roles:
    - ibm.mas_devops.ocs
```

### Upgrade Existing Installation

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    lso_device_path: /dev/vdb
    ocs_action: upgrade
  roles:
    - ibm.mas_devops.ocs
```

### Custom Disk Path

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    lso_device_path: /dev/nvme0n1
    ocs_action: install
  roles:
    - ibm.mas_devops.ocs
```

## License

EPL-2.0
