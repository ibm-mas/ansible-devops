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

### lso_device_path
Local disk device path for block storage.

- **Required**
- Environment Variable: `LSO_DEVICE_PATH`
- Default: `/dev/vdb`

**Purpose**: Specifies the local disk device path to be used by the Local Storage Operator for block storage provisioning.

**When to use**: Always required when installing ODF/OCS. Must point to an available, unformatted local disk on worker nodes.

**Valid values**: Valid Linux block device path (e.g., `/dev/vdb`, `/dev/sdc`, `/dev/nvme0n1`)

**Impact**: This disk will be used for ODF/OCS storage cluster. All data on the disk will be erased during setup.

**Related variables**: [`ocs_action`](#ocs_action)

**Notes**:
- **Critical**: Disk must be unformatted and not in use
- All data on the specified disk will be permanently erased
- Disk must be available on all worker nodes designated for storage
- Verify disk path: `lsblk` on worker nodes
- Common paths: `/dev/vdb` (virtual machines), `/dev/sdc` (physical servers)
- For NVMe drives, use format `/dev/nvme0n1`, `/dev/nvme1n1`, etc.
- Ensure disk has sufficient capacity for your storage requirements

### ocs_action
Action to perform on ODF/OCS installation.

- **Optional**
- Environment Variable: `OCS_ACTION`
- Default: `install`

**Purpose**: Controls whether to perform a fresh installation or upgrade of ODF/OCS operators and storage cluster.

**When to use**:
- Use `install` (default) for new ODF/OCS deployments
- Use `upgrade` to update existing ODF/OCS installation to match current OpenShift version

**Valid values**:
- `install` - Fresh installation of Local Storage Operator, ODF/OCS operator, and storage cluster
- `upgrade` - Upgrade existing operators and storage cluster based on OpenShift version

**Impact**:
- **install**: Creates new LSO and ODF/OCS operators, configures local storage, creates storage cluster
- **upgrade**: Updates operator subscriptions and storage cluster configuration to match OpenShift version

**Related variables**: [`lso_device_path`](#lso_device_path)

**Notes**:
- Default `install` is for new deployments
- Use `upgrade` after OpenShift cluster upgrades to keep storage in sync
- Upgrade process updates operators to versions compatible with current OCP version
- Always backup data before performing upgrades
- Verify cluster health before and after upgrade operations


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

