suite_certs
============


This role iterates through the subdirectories in `$MAS_CONFIG_DIR/certs` which are named as `core` or name of the `apps` like `monitor`, `manage`, `iot` and so on. It looks for tls.crt, tls.key and ca.crt in these subdirectories.
The names of the subdirectories in `$MAS_CONFIG_DIR/certs` are used to construct namespace to create/identify it and also creates the TLS secret with the tls/ca certs in those namespaces. So these subdirectories should be named correctly as the app names used in namespace suffixes.

## Directory structure example,
```
$MAS_CONFIG_DIR/certs/core/tls.crt
$MAS_CONFIG_DIR/certs/core/tls.key
$MAS_CONFIG_DIR/certs/core/ca.crt
$MAS_CONFIG_DIR/certs/<apps>/tls.crt
$MAS_CONFIG_DIR/certs/<apps>/tls.key
$MAS_CONFIG_DIR/certs/<apps>/ca.crt
```

## TLS Secret
`tls.crt`, `tls.key` and `ca.crt` are **mandatory** files in these subdirectories. They are used to create TLS secret in each applications' namespace. The role will fail if an empty app subdirectory is present or an app subdirectory missing a mandatory file

### Note: 
Currently the secret names for core and each app are maintained in `suite_certs/defaults/main.yml`. Any changes to the existing secret name or adding new apps needs to be done here.


Role Variables
--------------

### mas_instance_id
The instance ID of the Maximo Application Suite installation to verify.

- **Required**
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_manual_cert_mgmt
Set this to `True` if you want to enable manual certificate management mode.

- Environment Variable: `MAS_MANUAL_CERT_MGMT`
- Default Value: `False`

### mas_config_dir
Path to the mas config directory. 

- **Required**
- Environment Variable: `MAS_CONFIG_DIR`

Role Variables - CIS as DNS Provider (Optional)
--------------

Optional variables for users using IBM Cloud Internet Services to manage DNS. This role will guarantee that your CNAMES related to MAS routes are created or updated in the informed CIS instance.

### dns_provider
Set this to `cis` if you manage DNS using IBM Cloud Internet. If this variable is informed with a value different than `cis` it results in error (except blank, as it is optional).

- Optional
- Environment Variable: `DNS_PROVIDER`

### mas_workspace_id
Workspace Id will be used as part of CNAMES definition when using `cis` as dns_provider.

- **Required** if dns_provider is defined and is `cis`
- Environment Variable: `MAS_WORKSPACE_ID`

### cis_crn
CRN Key identifying the CIS in IBM Cloud. You can find that information in the page of your CIS instance.

- **Required** if dns_provider is defined and is `cis`
- Environment Variable: `CIS_CRN`

### cis_apikey
API Key used to access the CIS in IBM CLoud.

- **Required** if dns_provider is defined and is `cis`
- Environment Variable: `CIS_APIKEY`

### cis_subdomain
Subdomain will be used as part of CNAMES definition when using `cis` as dns_provider.

- **Required** if dns_provider is defined and is `cis`
- Environment Variable: `CIS_SUBDOMAIN`

### cis_proxy
Set this to `True` if you want enable proxy in your CIS CNames leveraging security rules defined for this software.

- Optional
- Environment Variable: `CIS_PROXY`
- Default Value: `False`

The directory structure for the certificates must be like below
```
$MAS_CONFIG_DIR/certs/core/tls.crt
$MAS_CONFIG_DIR/certs/core/tls.key
$MAS_CONFIG_DIR/certs/core/ca.crt
$MAS_CONFIG_DIR/certs/manage/tls.crt
$MAS_CONFIG_DIR/certs/manage/tls.key
$MAS_CONFIG_DIR/certs/manage/ca.crt
$MAS_CONFIG_DIR/certs/<app>/tls.crt
$MAS_CONFIG_DIR/certs/<app>/tls.key
$MAS_CONFIG_DIR/certs/<app>/ca.crt
```

the subdirectory name in the `$MAS_CONFIG_DIR/certs` directory is used to construct the namespace where the TLS secret will be applied to. So name the directory approriately.


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: masinst1
    mas_manual_cert_mgmt: True
    mas_config_dir: /Users/johnbarnes/Document/masconfig
  roles:
    - ibm.mas_devops.suite_certs

```


More Detailed View of Directory Structure
------------------------------------------


```
MAS_CONFIG_DIR
|
|---certs
|     |
|     |
|     |---core
|     |    |
|     |    |---tls.crt
|     |    |---tls.key
|     |    |---ca.crt
|     |---iot
|     |    |
|     |    |---tls.crt
|     |    |---tls.key
|     |    |---ca.crt
|     |---monitor
|     |    |
|     |    |---tls.crt
|     |    |---tls.key
|     |    |---ca.crt
|     |---manage
|     |    |
|     |    |---tls.crt
|     |    |---tls.key
|     |    |---ca.crt
|     |---add
|     |    |
|     |    |---tls.crt
|     |    |---tls.key
|     |    |---ca.crt
|     |---assist
|     |    |
|     |    |---tls.crt
|     |    |---tls.key
|     |    |---ca.crt
|     |---optimizer
|     |    |
|     |    |---tls.crt
|     |    |---tls.key
|     |    |---ca.crt
|     |---visualinspection
|     |    |
|     |    |---tls.crt
|     |    |---tls.key
|     |    |---ca.crt
```


License
-------

EPL-2.0
