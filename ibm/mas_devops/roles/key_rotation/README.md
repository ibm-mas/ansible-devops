# key_rotation

Create a new API key for a user in a cloud account and delete the existing one.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`cluster_type`](#cluster_type) | Yes | None |
| [`ibmcloud_apikey`](#ibmcloud_apikey) | Yes (ROKS) | None |
| [`ibmcloud_keyname`](#ibmcloud_keyname) | Yes (ROKS) | None |
| [`ibmcloud_output_keydir`](#ibmcloud_output_keydir) | No | `/tmp` |
| [`aws_region`](#aws_region) | Yes (ROSA/IPI-AWS) | `us-east-1` |
| [`aws_username`](#aws_username) | Yes (ROSA/IPI-AWS) | None |
| [`aws_access_key_id`](#aws_access_key_id) | Yes (ROSA/IPI-AWS) | None |
| [`aws_secret_access_key`](#aws_secret_access_key) | Yes (ROSA/IPI-AWS) | None |

### Cluster Selection

#### cluster_type

Specify the cluster type.

- **Required**
- Environment Variable: `CLUSTER_TYPE`
- Default: None

Supported values are `roks` and `rosa`.

### ROKS Variables

Used when `cluster_type` is `roks`.

#### ibmcloud_apikey

IBM Cloud API key — a new key will be created and this key will be deleted.

- **Required** when `cluster_type` is `roks`
- Environment Variable: `IBMCLOUD_APIKEY`
- Default: None

#### ibmcloud_keyname

Name for the newly created IBM Cloud API key — a new key will be created and the existing key deleted.

- **Required** when `cluster_type` is `roks`
- Environment Variable: `IBMCLOUD_KEYNAME`
- Default: None

#### ibmcloud_output_keydir

Directory where the newly created key is written.

- **Optional**
- Environment Variable: `IBMCLOUD_OUTPUT_KEYDIR`
- Default: `/tmp`

### ROSA and IPI/AWS Variables

Used when `cluster_type` is `rosa`, or `cluster_type` is `ipi` with `ipi_platform` set to `aws`.

#### aws_region

AWS region of the cluster.

- **Required** when `cluster_type` is `rosa` or `ipi` (with `ipi_platform = aws`)
- Environment Variable: `AWS_REGION`
- Default: `us-east-1`

#### aws_username

AWS user for which the access key is rotated.

- **Required** when `cluster_type` is `rosa` or `ipi` (with `ipi_platform = aws`)
- Environment Variable: `AWS_USERNAME`
- Default: None

#### aws_access_key_id

AWS access key ID — a new key will be created and this key will be deleted.

- **Required** when `cluster_type` is `rosa` or `ipi` (with `ipi_platform = aws`)
- Environment Variable: `AWS_ACCESS_KEY_ID`
- Default: None

#### aws_secret_access_key

AWS secret access key matching `aws_access_key_id`.

- **Required** when `cluster_type` is `rosa` or `ipi` (with `ipi_platform = aws`)
- Environment Variable: `AWS_SECRET_ACCESS_KEY`
- Default: None

## Example Playbook

```yaml
- hosts: localhost
  vars:
    cluster_type: roks
    ibmcloud_apikey: ################
    ibmcloud_keyname:  myapikeyname

  roles:
    - ibm.mas_devops.key_rotation
```

## License

EPL-2.0
