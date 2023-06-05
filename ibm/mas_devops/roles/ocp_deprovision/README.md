ocp_deprovision
===============================================================================
Deprovision OCP cluster in Fyre, IBM Cloud, & ROSA.

Role Variables
-------------------------------------------------------------------------------
### cluster_type
Required.  Specify the cluster type, supported values are `roks` and `quickburn`.

- **Required**
- Environment Variable: `CLUSTER_TYPE`
- Default Value: None

### cluster_name
Required.  Specify the name of the cluster

- **Required**
- Environment Variable: `CLUSTER_NAME`
- Default Value: None


Role Variables - ROKS
-------------------------------------------------------------------------------
### ibmcloud_apikey
The APIKey to be used by ibmcloud login comand.

- **Required** if `cluster_type = roks`
- Environment Variable: `IBMCLOUD_APIKEY`
- Default Value: None


Role Variables - ROSA
-------------------------------------------------------------------------------
### rosa_token
The Token used to authenticate with the ROSA service.

- **Required** if `cluster_type = rosa`
- Environment Variable: `ROSA_TOKEN`
- Default Value: None


Role Variables - FYRE
-------------------------------------------------------------------------------
### fyre_username
Username to authenticate with the Fyre API.

- **Required** if `cluster_type = quickburn`.
- Environment Variable: `FYRE_USERNAME`
- Default Value: None

### fyre_apikey
API key to authenticate with the Fyre API.

- **Required** if `cluster_type = quickburn`.
- Environment Variable: `FYRE_APIKEY`
- Default Value: None


Role Variables - IPI
-------------------------------------------------------------------------------
The following variables are only used when `cluster_type = ipi`.

### ipi_install_dir
The directory that is used to store the `openshift-install` executable, its configuration, & generated log files.

- Optional when `cluster_type = aws-ipi`
- Environment Variable: `IPI_DIR`
- Default Value: `~/openshift-install`


Role Variables - AWS
-------------------------------------------------------------------------------
The following variables are only used when `cluster_type = ipi` and `ipi_platform = aws`.

### aws_access_key_id
AWS access key associated with an IAM user or role.

- **Required** when `cluster_type = ipi` and `ipi_platform = aws`
- Environment Variable: `AWS_ACCESS_KEY_ID`
- Default Value: None

### aws_secret_access_key
AWS secret access key associated with an IAM user or role. Make sure the access key has permissions
to delete instances.

- **Required** when `cluster_type = ipi` and `ipi_platform = aws`
- Environment Variable: `AWS_SECRET_ACCESS_KEY`
- Default Value: None

Role Variables - GCP
-------------------------------------------------------------------------------
The following variables are only used when `cluster_type = ipi` and `ipi_platform = gcp`.

### gcp_service_account_file
GCP service account file path. Make sure the service account has permissions to create instances.

- **Required** when `cluster_type = ipi` and `ipi_platform = gcp`
- Environment Variable: `GOOGLE_APPLICATION_CREDENTIALS`
- Default Value: None


Example Playbook
-------------------------------------------------------------------------------

```yaml
- hosts: localhost
  vars:
    cluster_name: mycluster
    cluster_type: roks

    ibmcloud_apikey: xxxxx
  roles:
    - ibm.mas_devops.ocp_deprovision
```

License
-------------------------------------------------------------------------------

EPL-2.0
