manage_publiccert
============

Sets public certificate management mode to manual mode in suite level. Creates public TLS secret with the certificate provided in core namespace. To use manual certificate management mode, set `mas_manual_cert_mgmt` to True and use `mas_public_cert_data_path` to pass the own certificate data yml file path, file must be in below format, replace `<base64 encoded>` to the respective base64 encoded values.
```yaml
data:
  tls.crt: <base64 encoded crt>
  tls.key: <base64 encoded key>
  ca.crt: <base64 encoded ca>
```

Role Variables
--------------

### mas_instance_id
Required.  The instance ID of the Maximo Application Suite installation to verify.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_manual_cert_mgmt
Set this to `True` if you want to enable manual certificate management mode.

- Environment Variable: `MAS_MANUAL_CERT_MGMT`
- Default Value: `False`

### mas_public_cert_data_path
Set this to the path of the own certificate data yml file

- Environment Variable: `MAS_PUBLIC_CERT_DATA_PATH`
- Default Value: `\"\"`


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_manual_cert_mgmt: True
    mas_public_cert_data_path: /Users/johnbarnes/Document/myowntlscert.yml
  roles:
    - ibm.mas_devops.manage_publiccert

```

License
-------

EPL-2.0
