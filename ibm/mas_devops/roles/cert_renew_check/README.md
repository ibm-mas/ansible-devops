cert_renew_check
=============

Will run the renewal command and check that a different secret has been created so the renewal has actually taken place. It checks both public and internal certs.

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
