cp4d_wds
==========

It's only for WDS 4.0.x install on the existing CP4D 4.0.x and WDS instance provisioning, and also generated WDScfg (For Assist Install) related yaml to MAS config Directory.

It's also used for WDScfg (For Assist Install) related yaml preparation if you want to use the existing external WDS instance. 

Role Variables
--------------
### wdschannel
The discovery channel used by discovery install. By default the `v4.0`  will be used as channel name for discovery install.  
- Environment Variable: `WDS_CHANNEL`
- Default Value: v4.0

### wdsversion
The discovery version used by discovery install. By default the discovery `4.0.4` version will be installed. 
- Environment Variable: `WDS_CHANNEL`
- Default Value: 4.0.4

### wdsstorageclass
The specific storage class for discovery install, if not specified , the storage class used by CP4D will be auto queried in the cluster and used for discovery.
install. 
Usually Watson Discovery uses the following storage classes. If you don't use these storage classes on your cluster, ensure that you have a storage class with an equivalent definition:
OpenShift Container Storage: `ocs-storagecluster-ceph-rbd` 
IBM Cloud OCP cluster: `ibmc-block-gold`,`ibmc-block-gold-gid`
IBM Spectrum® Scale Container Native: `ibm-spectrum-scale-sc`
Portworx: `portworx-db-gp2-sc`

- Environment Variable: `WDS_STORAGE_CLASS`
- Default Value: None

### mas_instance_id
The instance ID of Maximo Application Suite that the discovery configuration will target.  If this or `mas_config_dir` are not set then the role will not generate a discovery template.

- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_config_dir
Local directory to save the generated discovery configuration files.  This can be used to manually configure a Assist instance to connect to the discovery cluster, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a discovery template.

- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None

If you want to use the existing available external WDS instance(not in the cluster), the below Environment Variables are `required` to generate the Discovery configuration files. Either is missing will cause the failure to use external Discovery.
### assist_wds_url
External Discovery URL for discovery API use
- Environment Variable: `ASSIST_WDS_URL`
- Default Value: None
### assist_wds_admin
External Discovery admin User name
- Environment Variable: `ASSIST_WDS_ADMIN`
- Default Value: None
### assist_wds_pass
External Discovery admin User password
- Environment Variable: `ASSIST_WDS_PASS`
- Default Value: None

Example Playbook
----------------
WDS install and WDS instance in the OCP Env 
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # Create the MAS WDSCfg & Secret resource definitions
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    mas_config_dir: "{{ lookup('env', 'MAS_CONFIG_DIR') }}"
  roles:
    - mas.devops.cp4d_wds
```
Use External WDS instance in the OCP Env 
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    #  Use External WDS instance for assist install
    assist_wds_url: "{{ lookup('env', 'ASSIST_WDS_URL') }}"
    assist_wds_admin: "{{ lookup('env', 'ASSIST_WDS_ADMIN') }}"
    assist_wds_pass: "{{ lookup('env', 'ASSIST_WDS_PASS') }}"

    #  Create the MAS WDSCfg & Secret resource definitions
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    mas_config_dir: "{{ lookup('env', 'MAS_CONFIG_DIR') }}"
  roles:
    - mas.devops.cp4d_wds
```

License
-------

EPL-2.0
