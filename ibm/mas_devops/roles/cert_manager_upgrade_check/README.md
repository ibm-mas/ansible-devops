cert_manager_upgrade_check
=============
This role requires `cert_manager_upgrade` role to have been executed prior. This will check and validate that MAS 8.6 instance continues to be in a fully working state after the cert-manager resources are migrated to new IBM Certificate Manager version. 

Here are the list of events that will happen as part of this role:

1. It will update your targeted MAS 8.6 instance Suite CR to use `ibm-common-services` namespace to lookup for IBM Certificate Manager, instead of `cert-manager` namespace, then wait for MAS 8.6 operator to reconcile this change. 
2. It will make necessary assertions to ensure the new IBM Certificate Manager is able to handle certificate management against the targeted MAS instance.
3. If all assertions are satisfied, then it will delete and clean up the old and not used cert-manager resources under `cert-manager` namespace:

- `secret/{{ mas_instance_id }}-cert-internal-ca`
- `secret/{{ mas_instance_id }}-cert-public-ca` (only exists if MAS is using self-signed certificates)
- `issuer.cert-manager.io/{{ mas_instance_id }}-core-internal-ca-issuer`
- `issuer.cert-manager.io/{{ mas_instance_id }}-core-public-ca-issuer` (only exists if MAS is using self-signed certificates)
- `certificate.cert-manager.io/{{ mas_instance_id }}-cert-internal-ca`
- `certificate.cert-manager.io/{{ mas_instance_id }}-cert-public-ca` (only exists if MAS is using self-signed certificates)

For more information, please refer to [Upgrading Maximo Application Suite](https://www.ibm.com/docs/en/mas87/8.7.0?topic=upgrading) documentation.

Role Variables
--------------
### mas_instance_id
Required - Defines the instance id that is used in the existing MAS installation, will be used to lookup the existing MAS subscription and targeted Certificates, Issuers and Secrets to be migrated.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### custom_cluster_issuer
Optional - Only required if the targeted MAS 8.6 instance is configured with a custom cluster issuer (i.e Let's Encrypt).
Having a cluster issuer or not will determine which resources will be migrated and cleaned up from the old and existing `cert-manager` namespace.
Not required if your MAS instance is installed and configured using self-signed certificates.

- Environment Variable: `MAS_CUSTOM_CLUSTER_ISSUER`
- Default Value: None

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  roles:
    - ibm.mas_devops.suite_upgrade_check
    - ibm.mas_devops.cert_manager_upgrade
    - ibm.mas_devops.cert_manager_upgrade_check
```

If you have cluster issuer, and have setup CIS webhook in your existing instance, you will need also to reinstall CIS webhook in `ibm-common-services` namespace. 
Therefore, you might want to use the following playbook sample to accomplish this.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    is_suite_upgrade: true # this will tell 'ibm.mas_devops.suite_dns' to reinstall cis webhook under 'ibm-common-services' ns if 'MAS_CUSTOM_CLUSTER_ISSUER' is set
  roles:
    - ibm.mas_devops.suite_upgrade_check
    - ibm.mas_devops.cert_manager_upgrade
    - ibm.mas_devops.suite_dns
    - ibm.mas_devops.cert_manager_upgrade_check
```