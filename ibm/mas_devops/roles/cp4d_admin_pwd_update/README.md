cp4d_admin_pwd_update
======================

This role will update the password on an existing cp4d instance. By default it will update the password to a randomly generated new password only when the instance is still using the 'initial_admin_password' although using the 'cp4d_admin_password_force_update' variable referenced below will override this to update the password regardless of the current one being used. The new password will be added to the same yaml file that the 'initial_admin_password' was generated into - 'admin-user-details' by default.


Role Variables
--------------

### mas_instance_id
The instance ID of Maximo Application Suite that the cp4d password updater will target.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### cp4d_namespace
The instance of cp4d in your cluster that the cp4d password updater will target - defaults to 'ibm-cpd'.

- Environment Variable: `CP4D_NAMESPACE`
- Default Value: 'ibm-cpd'

### cp4d_admin_credentials_secret_name
The secret inside your cp4d instance that stores the intial admin password - defaults to 'admin-user-details'.

- Environment Variable: `CP4D_ADMIN_CREDENTIALS_SECRET_NAME`
- Default Value: 'admin-user-details'

### cp4d_admin_username
The username for your cp4d instance - defaults to 'admin'.

- Environment Variable: `CP4D_ADMIN_USERNAME`
- Default Value: 'admin'

### cp4d_admin_password
The password for your cp4d insrance - an optional addition as the password updater will attempt to collect this value from the 'cp4d_admin_credentials_secret_name' secret.

- Optional
- Environment Variable: `CP4D_ADMIN_PASSWORD`
- Default Value: None

### cp4d_admin_password_force_update
Typically the password updater will only update the password if the cp4d instance is using the initial password provided in the secret - setting this value to 'True' will ensure that is resets the password regardless.

- Environment Variable: `CP4D_ADMIN_PASSWORD_FORCE_UPDATE`
- Default Value: 'False'



Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    cp4d_namespace: ibm-cpd
    cp4d_admin_credentials_secret_name: admin-user-details

    cp4d_admin_username: admin
    cp4d_admin_password: password123
    cp4d_admin_password_force_update: True

  roles:
    - ibm.mas_devops.cp4d_admin_pwd_update
```