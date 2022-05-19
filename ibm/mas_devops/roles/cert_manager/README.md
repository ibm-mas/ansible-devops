cert_manager
============

Deploy a Certificate Manager Operator into the target OCP cluster.  For MAS 8.6 (or earlier) JetStack cert-manager v1.2 is installed into the `cert-manager` namespace.  When used for MAS 8.7+ IBM Certificate Manager will instead be installed in the `ibm-common-services` namespace.


Role Variables
--------------
### mas_channel
Used to determine whether to install SBO stable channel and the IBM badged cert-manager.

- Optional, if not provided then the IBM certificate manager will be preferred to the JetStack certificate manager.
- Environment Variable: `MAS_CHANNEL`
- Default Value: None


Example Playbook
----------------

```yaml
- hosts: localhost
  vars:
    mas_channel: 8.8.x
  roles:
    - ibm.mas_devops.cert_manager
```


Tekton Task
-----------
Start a run of the **mas-devops-cert-manager** Task as below, you must have already prepared the namespace:

```
cat <<EOF | oc create -f -
apiVersion: tekton.dev/v1beta1
kind: TaskRun
metadata:
  generateName: mas-devops-cert-manager-
spec:
  taskRef:
    kind: Task
    name: mas-devops-cert-manager
  params:
  - name: mas_channel
    value: 8.8.x
  resources: {}
  serviceAccountName: pipeline
  timeout: 24h0m0s
EOF
```


License
-------

EPL-2.0
