# cert_manager
Deploy the **IBM Certificate Manager Operator** into the target OCP cluster in the `ibm-common-services` namespace.


## Prerequisites
To run this role successfully you must have already installed a CatalogSource that contains IBM Certificate Manager and installed the **IBM Cloud Pak Foundational Services Operator**.  These tasks can be achieved using the [ibm_catalogs](ibm_catalogs.md) and [common_services](common_services.md) roles in this collection.


## Role Variables
None


## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  roles:
    - ibm.mas_devops.ibm_catalogs
    - ibm.mas_devops.common_services
    - ibm.mas_devops.cert_manager
```


## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
ROLE_NAME=cert_manager ansible-playbook ibm.mas_devops.run_role
```


# License
EPL-2.0
