suite_certs_renew
=============

Will run the renewal command and check that a different secret has been created so the renewal has actually taken place. It checks both public and internal certs.

Role Variables
--------------
### mas_instance_id
Required - Defines the instance id that is used in the existing MAS installation, will be used to lookup the existing MAS subscription and targeted Certificates, Issuers and Secrets to be migrated.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

