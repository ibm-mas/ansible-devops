suite_verify
============

Verify a MAS installation is ready to use.  This role will also print out the Admin Dashboard URL and the username and password of the superuser.  If you want to disable these credentials being written to the output set the `mas_hide_superuser_credentials` to `True`.

Role Variables
--------------

### mas_instance_id
Required.  The instance ID of the Maximo Application Suite installation to verify.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_hide_superuser_credentials
Set this to `True` if you want to disable the display of the superuser credentials as part of the verify.  When this is enabled the debug will only identify the name of the secret containing the credentials rather than displaying the actual values.

- Environment Variable: `MAS_HIDE_SUPERUSER_CREDENTIALS`
- Default Value: `False`


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_hide_superuser_credentials: True
  roles:
    - ibm.mas_devops.suite_verify

```


License
-------

EPL-2.0
