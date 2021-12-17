cos_setup
=============

This role provides support to install Ceph Object Storage on the existing OCS cluster.

It also support to Provision Cloud Object storage instance in IBM cloud.

Note: If you want to install IBM Cloud Object storage , pls install  
`ansible-galaxy collection install ibm.cloudcollection`

Role Variables
--------------

- `IC_API_KEY` An IBM Cloud APIKey to Provision the IBM COS instance 
- `IC_SPACE_NAME` An IBM Cloud Account Space name to Provision the IBM COS instance 
- `IC_ORG_NAME` An IBM Cloud Account Orgnization Name to Provision the IBM COS instance 
- `MAS_CONFIG_DIR` Provide the MAS Config Dir to Save the cos related Config yaml
- `MAS_INSTANCE_ID` Provide the MAS instance ID that will be used in any generated MAS configuration files
- `useibmcos`: Set True if you want to use IBM Cloud object storage


Example Playbook
----------------

Create the Ceph Object store on the existing OCS cluster and prepare the objectstorageCfg yaml to mas_config_dir.
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    mas_config_dir: "{{ lookup('env', 'MAS_CONFIG_DIR') }}"
  roles:
    - ibm.mas_devops.cos_setup
```
Create the IBM Cloud Object storage Instance and prepare the objectstorageCfg yaml to mas_config_dir.
```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # User IBM Cloud Object storage
    useibmcos: true
    ibm_cloud_apikey: "{{ lookup('env', 'IC_API_KEY') }}"  # IBM Cloud apikey
    ibm_cloud_space: "{{ lookup('env', 'IC_SPACE_NAME') }}" # IBM Cloud account space
    ibm_cloud_org: "{{ lookup('env', 'IC_ORG_NAME') }}" # IBM Cloud account org
 
   # MAS instance and config dir
    mas_instance_id: "{{ lookup('env', 'MAS_INSTANCE_ID') }}"
    mas_config_dir: "{{ lookup('env', 'MAS_CONFIG_DIR') }}"
  roles:
    - ibm.mas_devops.cos_setup
```
License
-------

EPL-2.0
