key_rotation
===============================================================================

Create new apikey for user in cloud account and delete the existing one.

Role Variables
-------------------------------------------------------------------------------
### cluster_type
Required.  Specify the cluster type, supported values are `roks`, and `rosa`.

- Environment Variable: `CLUSTER_TYPE`
- Default Value: None


Role Variables - ROKS
-------------------------------------------------------------------------------
### ibmcloud_apikey

- Required. A new key will be created and this key will be deleted.
- Environment Variable: `IBMCLOUD_APIKEY`
- Default: None

### ibmcloud_keyname

- Required. A new key will be created and this key will be deleted.
- Environment Variable: `IBMCLOUD_KEYNAME`
- Default: None

### ibmcloud_output_keydir

- Optional.
- Environment Variable: `IBMCLOUD_OUTPUT_KEYDIR`
- Default: '/tmp'


Role Variables - ROSA or IPI/AWS
-------------------------------------------------------------------------------
The following variables are used when `cluster_type = rosa` or `cluster_type=ipe` and `cluster_platform=aws`.

### aws_region

- **Required** when `cluster_type = rosa` or `cluster_type = ipi` and `ipi_platform = aws` 
- Environment Variable: `AWS_REGION`
- Default Value: us-east-1

### aws_username

- Required.
- Environment Variable: `AWS_USERNAME`
- Default: None

### aws_access_key_id

- Required. A new key will be created and this key will be deleted.
- Environment Variable: `AWS_ACCESS_KEY_ID`
- Default: None

### aws_secret_access_key

- Required. A new key will be created and this key will be deleted.
- Environment Variable: `AWS_SECRET_ACCESS_KEY`
- Default: None


Example Playbook
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  vars:
    cluster_type: roks
    ibmcloud_apikey: ################
    ibmcloud_keyname:  myapikeyname

  roles:
    - ibm.mas_devops.key_rotation
```

License
-------------------------------------------------------------------------------

EPL-2.0
