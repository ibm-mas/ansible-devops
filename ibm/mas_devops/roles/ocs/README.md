ocs
===

This role provides support to install/update OpenShift Data Foundation Operator (ODF) (formerly called Openshift Container Storage (OCS)) and the Local Storage Operator (LSO). This role is not used by default when setting up IBM Cloud ROKS clusters because they are automatically provisioned with their own storage plugin already.

The OCP Version is autodetected and if it is found to be at version `4.10` or less then the `ocs` operator is used, else the `odf` operator is used.

Unfortunately, starting from OCP 4.8 IBM/Red Hat have decided to stop supporting OCS on IBMCloud ROKS.  So this role is of limited value to users of ROKS going forward.  If you attempt to install OpenShift Container Storage on ROKS via a Subscription channel you will be met by the following error as the admission webhook has been coded to prevent use of the OCS operator on IBM Cloud ROKS: **Failed to apply object: "admission webhook "validate.managed.openshift.io" denied the request: Installing OpenShift Data Foundation on IBM Cloud by using OperatorHub is not supported. You can install OpenShift Data Foundation by using the IBM Cloud add-on. For more information, see https://cloud.ibm.com/docs/openshift?topic=openshift-ocs-storage-prep.**

Role Variables
--------------

### lso_device_path
Set this value with your actual local disk filepath to be used in the LocalVolume for block storage using the localblock storageclass.

- Environment Variable: `LSO_DEVICE_PATH`
- Default Value: `/dev/vdb`

### ocs_action
Set this value to the required action for `install` or `upgrade`. If set to install, the local storage and OCF/ODF storage operators will be installed with their storage cluster. If set to upgrade, the operators and storage cluster will be updated based on the ocp version in the cluster.

- Environment Variable: `OCS_ACTION`
- Default Value: `install`


Example Playbook
----------------

```yaml
---
- hosts: localhost
  any_errors_fatal: true
  roles:
    - ibm.mas_devops.ocs
```

License
-------

EPL-2.0
