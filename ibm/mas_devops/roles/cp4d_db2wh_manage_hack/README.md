cp4d_db2wh_manage_hack
======================

This role shouldn't need to exist, it should be part of the Manage operator, but is not so we have to do it as a seperate step in the install flow for now.  The role will perform some initial setup on the Db2 instance that is needed to prepare it for use with the Manage application and supports both CP4D version 3.5 and 4.0.

Role Variables
--------------
### cpd_version
Users may **optionally** pass this parameter to explicitly control the version of CP4D used, if this is not done then the role will attempt to locate the `cpd-meta-ops` namespace associated with CP4D v3.5, if this namespace if located then we will switch to CP4D v3.5 mode, in all other cases the role will assume CP4D v4 is in use.

- Environment Variable: `CPD_VERSION`
- Default Value: None

### db2wh_instancename
Required.  The name of the db2 instance to execute the hack in.  We will use this to derive the instance ID.  Note that for CP4D v3.5 instances we are only able to support those created by the [cp4d_db2wh](cp4d_db2wh.md) role; custom metadata is created by that role which is required by this role to dervice the instance ID from a named database instance.

- Environment Variable: `DB2WH_INSTANCE_NAME`
- Default Value: None

### db2wh_username
The username that will be used to connect to the database specified by `db2wh_dbname`.

- Environment Variable: None
- Default Value: `db2inst1`

### db2wh_dbname
The name of the database in the instance to connect to when executing the hack script.

- Environment Variable: None
- Default Value: `BLUDB`

### db2wh_schema
The name of the Manage schema where the hack should be targeted in.

- Environment Variable: None
- Default Value: `maximo`


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2wh_instancename: mydb2
  roles:
    - ibm.mas_devops.cp4d_db2wh_manage_hack
```


License
-------

EPL-2.0
