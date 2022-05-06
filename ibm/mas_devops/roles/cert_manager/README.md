cert_manager
============

Deploy a Certificate Manager Operator into the target OCP cluster.  For MAS 8.6 (or earlier) JetStack cert-manager v1.2 is installed into the `cert-manager` namespace.  When used for MAS 8.7+ IBM Certificate Manager will instead be installed in the `ibm-common-services` namespace.


Role Variables
--------------
### mas_channel
Used to determine whether to install SBO stable channel and the IBM badged cert-manager.

- Optional, if not provided then the IBM Certificate Manager will be installed.
- Environment Variable: `MAS_CHANNEL`
- Default Value: None


Example Playbook
----------------

```yaml
- hosts: localhost
  roles:
    - ibm.mas_devops.cert_manager
```


License
-------

EPL-2.0
