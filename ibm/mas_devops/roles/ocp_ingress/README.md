# ocp_ingress
This role will tune the Ingress operator in the target OCP cluster. The following Ingress tuning parameters can be modified to avoid request failures due to timeout for long running requests.

## Role Variables
### ocp_ingress_client_timeout
Specifies how long a connection is held open while waiting for a client response

- Optional
- Environment Variable: `OCP_INGRESS_CLIENT_TIMEOUT`
- Default Value: `30s`

### ocp_ingress_server_timeout
Specifies how long a connection is held open while waiting for a server response

- Optional
- Environment Variable: `OCP_INGRESS_SERVER_TIMEOUT`
- Default Value: `30s`

## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  roles:
    - ibm.mas_devops.ocp_ingress
```


## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
ROLE_NAME=ocp_ingress ansible-playbook ibm.mas_devops.run_role
```


## License
EPL-2.0
