Role Name
=========

Install IBM Manage app, using OLM

Requirements
------------


Openshift Cluster 4.X
MAS 8.4

Role Variables
--------------

- instance_id: MAS instance Id
- manage_namespace: Manage namespace
- cp: Host to cp registry
- cpopen: Host to cpopen registry
- entitlement_username: username entitled to manage
- entitlement_key: apikey entitled to manage
- entitlement_server: entitled server
- artifactory_username: artifactory username
- artifactory_apikey: artifactory apikey
- manage_version: Manage version to be installed
- workspace_id: MAS workspace ID
- jdbc_url: Jdbc connection url
- jdbc_secret_name: secret name to hold jdbc credentials
- jdbc_username: jdbc service username
- jdbc_password: jdbc service password

Dependencies
------------

- community.kubernetes


Example Playbook
----------------

```
---
- hosts: localhost
  vars:
    instance_id: xxx
    manage_namespace: xxx
    cp: wiotp-docker-local.artifactory.swg-devops.com
    cpopen: wiotp-docker-local.artifactory.swg-devops.com
    entitlement_username: xxx
    entitlement_key: xxx
    entitlement_server: wiotp-docker-local.artifactory.swg-devops.com
    artifactory_username: xxx
    artifactory_apikey: xxx
    manage_version: 8.0.0
    workspace_id: xxx
    jdbc_url: xxx
    jdbc_secret_name: xxx
    jdbc_username: xxx
    jdbc_password: xxx
  roles:
    - mas.devops.manage
```

License
-------

Internal use only

