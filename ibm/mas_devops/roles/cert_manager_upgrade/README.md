cert_manager_upgrade
=============

This role will migrate the cert-manager resources used by the existing MAS 8.6 instance from JetStack cert-manager (under cert-manager namespace) to IBM Certificate Manager (under ibm-common-services namespace) used in MAS 8.7+
When running this role, note this will affect all of the applications in your Openshift Cluster that use cluster issuers to sign for certificates.

Here are the list of events that will happen as part of this role:

1. Cert-manager Jetstack deployments (under cert-manager namespace) will be deleted and IBM Certificate Manager (under ibm-common-services namespace) will be installed. Only one Certificate Manager must be running in the cluster to avoid conflicts. Note: It won't fully uninstall existing cert-manager nor remove its namespace/resources, however when this step is done, existing cert-manager won't be running anymore as it will be replaced by the new IBM Certificate Manager, therefore before running this role, be sure you know what you are doing to avoid disruptions in other services deployed in your cluster. 
2. Cert-manager resources for your targeted MAS instance such as Issuers, Certificates and Secrets will be moved from cert-manager namespace to the ibm-common-services namespace, that is needed so the new IBM Certificate Manager can continue to manage your MAS certificates after 8.7 upgrade.

Cert-manager resources that will be moved to the new IBM Certificate Manager namespace (`cert-public` resources will only exist if MAS is using self-signed certificates):

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
Having a cluster issuer or not will determine which resources will be migrated to the new IBM Certificate Manager namespace.
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
```