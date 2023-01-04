suite_manage_import_certs_config
===
This role extends support for importing certificates into **Manage** application's workspace.
**Note:** This role should be executed **after** Manage application is deployed and activated as it needs Manage up and running prior importing new certificates.

You can run this as standalone role, providing a local path for a file that contains the Manage certificates definition (`manage_certificates_file_path_local` variable).

Or you can invoke this role inside another playbook/role, passing the Manage certificates content as a list variable (`manage_certificates`) and an alias prefix as a string variable (`manage_certificates_alias_prefix`). The certificate alias name will be concatenated with the alias prefix plus auto incremented accordingly to the number of certificates provided i.e If you provide a list with 3 certificates, and define `manage_certificates_alias_prefix: myaliasprefixpart`, then the alias name will be `myaliasprefixpart1; myaliasprefixpart2; myaliasprefixpart3`

Role Variables
--------------

### mas_instance_id
Required. The instance ID of Maximo Application Suite. This will be used to lookup for Manage application resources.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_workspace_id
Required. The workspace ID of Maximo Application Suite. This will be used to lookup for Manage application resources.

- Environment Variable: `MAS_WORKSPACE_ID`
- Default Value: None

### manage_workspace_cr_name
Optional. Name of the `ManageWorkspace` Custom Resource that will be targeted to import the new certificates.

- Environment Variable: `MANAGE_WORKSPACE_CR_NAME`
- Default Value: `$MAS_INSTANCE_ID-$MAS_WORKSPACE_ID`

### manage_certificates_file_path_local
Required if running as standalone role. This defines a local path pointing the certificates definition from a custom file. Sample file definition can be found in `files/manage-certs-sample.yml`.

- Environment Variable: `MANAGE_CERTIFICATES_FILE_PATH_LOCAL`
- Default Value: None

Example Playbook
----------------
The following sample can be used to import Manage certificates for an existing Manage instance, using a local path pointing the certificates definition from a custom file.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    manage_certificates_file_path_local: /my-path/manage-certs.yml
  roles:
    - ibm.mas_devops.suite_manage_import_certs_config
```

The following sample can be used to import Manage certificates for an existing Manage instance, passing the certificates and prefix from a variable.

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_workspace_id: masdev
    manage_certificates: ['-----BEGIN CERTIFICATE----- << your-cert-content >> -----END CERTIFICATE-----']
    manage_certificates_alias_prefix: "myaliasprefixpart"
  roles:
    - ibm.mas_devops.suite_manage_import_certs_config
```

Run Role Playbook
----------------
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
export MAS_INSTANCE_ID=masinst1
export MAS_WORKSPACE_ID=masdev
export MANAGE_CERTIFICATES_FILE_PATH_LOCAL=/my-path/manage-certs.yml
ROLE_NAME='suite_manage_import_certs_config' ansible-playbook playbooks/run_role.yml

License
-------

EPL-2.0
