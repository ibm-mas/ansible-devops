Role Name
=========

Install Maximo Application Suite using OLM

Requirements
------------

Openshift 4.X

Role Variables
--------------
- cluster_name: target cluster name
- instance_id: MAS instance Id
- mas_namespace: Target namespace
- cp: CP registry
- cpopen: CPOPEN Registry
- domain: Domain to be used for that MAS instance
- entitlement_username: Entitled username
- entitlement_key: Entitled user apikey
- entitlement_server: Entitled server
- artifactory_username: Artifactory username
- artifactory_apikey: Artifactory APIKey
- mas_version: MAS Version to be deployed

- mongo_username: MongoDB Username
- mongo_password: MongoDB Password

- ldap_bind_password: the ldap bind password

- workspace_id: Workspace Id
- sls_registration_key: SLS Registration Key
- sls_url: SLS Url

Dependencies
------------

community.kubernetes

Example Playbook
----------------

````
---
- hosts: localhost
  vars:
    cluster_name: xxx
    instance_id: xxx
    mas_namespace: xxx
    cp: xxx
    cpopen: wiotp-docker-local.artifactory.swg-devops.com
    domain: "xxx.apps.xxx.cp.fyre.ibm.com"
    entitlement_username: xxx
    entitlement_key: xxx
    entitlement_server: wiotp-docker-local.artifactory.swg-devops.com
    artifactory_username: xxx
    artifactory_apikey: xxx
    mas_version: 8.4.0

    # MongoDB
    mongo_username: xxx
    mongo_password: xxx

l   dap_bind_password: xxx
    # MAS Config
    workspace_id: xxx
    sls_registration_key: xxx
    sls_url: https://xxx
  roles:
    - mas.devops.suite
````

License
-------

Internal use only
