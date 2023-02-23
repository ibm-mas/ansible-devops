key_rotation
===============================================================================

Create new apikeys for cluster.

Role Variables
-------------------------------------------------------------------------------
### cluster_type
Required.  Specify the cluster type, supported values are `roks`, and `rosa`.

- Environment Variable: `CLUSTER_TYPE`
- Default Value: None

### vault_role_id
Required.  Specify the role id

- Environment Variable: `VAULT_ROLE_ID`
- Default Value: None

### vault_secret_id
Required.  Specify the secret id

- Environment Variable: `VAULT_SECRET_ID`
- Default Value: None

### vault_addr
Required.  Specify the addr

- Environment Variable: `VAULT_ADDR`
- Default Value: None


Role Variables - ROSA or IPI/AWS
-------------------------------------------------------------------------------
The following variables are used when `cluster_type = rosa` or `cluster_type=ipe` and `cluster_platform=aws`.

- **Required** when `cluster_type = rosa` or `cluster_type = ipi` and `ipi_platform = aws` 
- Environment Variable: `AWS_REGION`
- Default Value: us-east-1

Example Playbook
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  vars:
    cluster_type: roks
    vault_role_id: myrole
    vault_secret_id: mysecret
    vault_addr: XXX.XXX.XXX.XXX

  roles:
    - ibm.mas_devops.key_rotation
```

License
-------------------------------------------------------------------------------

EPL-2.0
