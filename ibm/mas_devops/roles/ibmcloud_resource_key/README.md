ibmcloud_resource_key
=========

Create IBM Cloud resource keys (apikeys for specific services associated to the account)


Role Variables
--------------

### service_instance
Name of the service that the key will be referencing. (Eg: DB2, Mongo, cp4d, etc)

- Required
- Environment Variable: `SERVICE_INSTANCE`

### service_resource_key_name
Name of the key to either create or delete. If unset will be dervied from the `service_instance` as "`service_instance`_resource-key"

- Optional
- Environment Variable: `SERVICE_RESOURCE_KEY_NAME`

### delete_service_key
Set this to true to force deletion of the `service_resource_key_name` provided

- Optional
- Environment Variable: `DELETE_SERVICE_KEY`
- Default: false

### output_service_key_details_to_file
If set will output a json file with the full service key details and credentials as "service-key_`service_resource_key_name`.json"

- Optional
- Environment Variable: `OUTPUT_SERVICE_KEY_DETAILS_TO_FILE`
- Default: false

### output_dir
Location to output the service key details json file if `output_service_key_details_to_file` is set

- Optional
- Environment Variable: `OUTPUT_DIR`
- Default: `.` (which will set the directory file in ibm/mas_devops)


Example Playbook
----------------

```yaml
---
- hosts: localhost
  any_errors_fatal: true
  vars:
    ibmcloud_apikey: xxx
    service_instance: xxx
    service_resource_key_name: xxx
    output_service_key_details_to_file: True OR False
    delete_service_key: True OR False
  roles:
    - ibmcloud_resource_key
```

License
-------

EPL-2.0
