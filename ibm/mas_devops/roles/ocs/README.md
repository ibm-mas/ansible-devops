ocs
===

This role provides support to install OpenShift Data Foundation Operator (ODF) (formerly called Openshift Container Storage (OCS)) and the Local Storage Operator (LSO). This role is not used by default when setting up IBM Cloud ROKS clusters because they are automatically provisioned with their own storage plugin already.

Unfortunately, starting from OCP 4.8 IBM/Red Hat have decided to stop supporting OCS on IBMCloud ROKS.  So this role is of limited value to users of ROKS going forward.  If you attempt to install OpenShift Container Storage on ROKS via a Subscription channel you will be met by the following error as the admission webhook has been coded to prevent use of the OCS operator on IBM Cloud ROKS: **Failed to apply object: "admission webhook "validate.managed.openshift.io" denied the request: Installing OpenShift Data Foundation on IBM Cloud by using OperatorHub is not supported. You can install OpenShift Data Foundation by using the IBM Cloud add-on. For more information, see https://cloud.ibm.com/docs/openshift?topic=openshift-ocs-storage-prep.**

Role Variables
--------------

### ocp_release
Set this to e.g. `4.10`, `4.11`, `4.12`.  We need to know what the release level is to know what channel to target the operator subscriptions at. If this is set to `4.10` or less then the `ocs` operator is used, else the `odf` operator is used.

- Environment Variable: `OCP_RELEASE`
- Default Value: `4.12`


Example Playbook
----------------

```yaml
---
- hosts: localhost
  any_errors_fatal: true
  vars:
    ocp_release: "4.12"
  roles:
    - ibm.mas_devops.ocs
```

License
-------

EPL-2.0
