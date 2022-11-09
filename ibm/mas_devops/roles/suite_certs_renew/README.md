suite_certs_renew
===============================================================================

Will run the renewal command and check that a different secret has been created so the renewal has actually taken place. It checks both public and internal certs.


Prerequisites
-------------------------------------------------------------------------------

### cmctl

This role utilises the cert-manager `cmctl renew` command which requires installing `cmctl` and adding it to your `$PATH`.

From the [cert-manager documentation](https://cert-manager.io/docs/usage/cmctl/):


>    You need the `cmctl.tar.gz` file for the platform you're using, these can be found on our [GitHub releases page](https://github.com/cert-manager/cert-manager/releases). In order to use `cmctl` you need its binary to be accessible under the name `cmctl` in your `$PATH`. Run the following commands to set up the CLI. Replace OS and ARCH with your systems equivalents:
>
>     OS=$(go env GOOS); ARCH=$(go env GOARCH); curl -sSL -o cmctl.tar.gz https://github.com/cert-manager/cert-manager/releases/download/v1.7.2/cmctl-$OS-$ARCH.tar.gz
>     tar xzf cmctl.tar.gz
>     sudo mv cmctl /usr/local/bin


Role Variables
-------------------------------------------------------------------------------

### mas_instance_id
Required - Defines the instance id that is used in the existing MAS installation, will be used to lookup the existing MAS subscription and targeted Certificates, Issuers and Secrets to be migrated.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None


Example Playbook
-------------------------------------------------------------------------------
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: instance1
  roles:
    - ibm.mas_devops.suite_certs_renew
```
