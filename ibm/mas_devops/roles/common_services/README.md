common_services
===============

This will result in the following operators being installed in the `ibm-common-services` namespace

- IBM Cloud Pak Foundational Services
- IBM NamespaceScope Operator
- Operand Deployment Lifecycle Manager

Also, an operator group will be created in the namespace if one does not already exist.


Role Variables
--------------
### common_services_catalog_source
Used to override the operator catalog source used when creating the `ibm-common-service-operator` subscription.

- Optional
- Environment Variable: `COMMON_SERVICES_CATALOG_SOURCE`
- Default Value: `ibm-operator-catalog`


Example Playbook
----------------

```yaml
- hosts: localhost
  roles:
    - ibm.mas_devops.common_services
```


Tekton Task
-----------
Start a run of the **mas-devops-common-services** Task as below, you must have already prepared the namespace:

```
cat <<EOF | oc create -f -
apiVersion: tekton.dev/v1beta1
kind: TaskRun
metadata:
  generateName: mas-devops-common-services-
spec:
  taskRef:
    kind: Task
    name: mas-devops-common-services
  resources: {}
  serviceAccountName: pipeline
  timeout: 24h0m0s
EOF
```


License
-------

EPL-2.0
