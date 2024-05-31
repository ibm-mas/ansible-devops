eck
=====

This role provides support to install [Elastic Cloud on Kubernetes](https://www.elastic.co/guide/en/cloud-on-k8s/master/index.html) (ECK).

Elasticsearch is configured with a default user named `elastic`, you can obtain the password for this user by running the following command:

```
oc -n eck get secret mas-es-elastic-user -o go-template='{{.data.elastic | base64decode}}'; echo
```


Role Variables
--------------
### eck_action
Action to be performed by the role. Valid values are `install` and `uninstall`.

- Environment Variable: `KAFKA_ACTION`
- Default Value: `install`



Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
  roles:
    - ibm.mas_devops.eck
```


License
-------

EPL-2.0
