# ingress
This role will tune the Ingress operator in the target OCP cluster.

## Role Variables
### ingress_client_timeout
specifies how long a connection is held open while waiting for a client response

- Optional
- Environment Variable: `INGRESS_CLIENT_TIMEOUT`
- Default Value: `30s`

### ingress_server_timeout
specifies how long a connection is held open while waiting for a server response

- Optional
- Environment Variable: `INGRESS_SERVER_TIMEOUT`
- Default Value: `30s`

## Example Playbook
After installing the Ansible Collection you can include this role in your own custom playbooks.

```yaml
- hosts: localhost
  roles:
    - ibm.mas_devops.ingress
```


## Run Role Playbook
After installing the Ansible Collection you can easily run the role standalone using the `run_role` playbook provided.

```bash
ROLE_NAME=ingress ansible-playbook ibm.mas_devops.run_role
```


## License
EPL-2.0
