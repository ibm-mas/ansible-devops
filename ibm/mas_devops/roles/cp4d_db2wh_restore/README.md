cp4d_db2wh_restore
==========

This role runs a restore procedure onto a CloudPak for Data DB2 Warehouse instance.
In order to begin the restore process, you must have the required files to run a successful restore process in the chosen `DB2WH_BACKUP_DIR`:

- DB2 backup files i.e `BLUDB.0.db2inst1.DBPART000.202XXXXXXXXXXX.001`
- DB2 keystore files (.p12 and .sth)
- DB2 instance master key label file (.kdb)

Note: These files are generated automatically if you run `ibm.mas_devops.cp4d_db2wh_backup` role. If any of the above files are not found in the `DB2WH_BACKUP_DIR`, the restore process will fail.

Role Variables
--------------

### db2wh_backup_dir
Required. Local directory that stores the backup files to be used in the DB2 Warehouse restore process, i.e `/Users/Documents/db_backup`.

- Environment Variable: `DB2WH_BACKUP_DIR`
- Default: None

### cpd_meta_namespace_target
Required. CloudPak for Data namespace for the target DB2 Warehouse instance where you want to restore the backup to, i.e `cpd-services`.

- Environment Variable: `CPD_NAMESPACE_TARGET`
- Default: None

### db2wh_instance_id_target
Required. DB2 Warehouse target instance to restore the backup to, i.e `db2wh-1641225392061935`.

- Environment Variable: `DB2WH_INSTANCE_ID_TARGET`
- Default: None

### oc_login_target
Optional. Openshift login command for the target cluster where you want to restore the backup to. Only needed if you want to run the backup and restore process end-to-end and target DB2 Warehouse instance is hosted in different cluster than the source DB2 Warehouse instance.

- Environment Variable: `OC_LOGIN_TARGET`
- Default: None

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2wh_backup_folder: "{{ lookup('env', 'DB2WH_BACKUP_DIR') }}"
    cpd_meta_namespace_target: "{{ lookup('env', 'CPD_NAMESPACE_TARGET') }}"
    db2wh_instance_id_target: "{{ lookup('env', 'DB2WH_INSTANCE_ID_TARGET') }}"
  roles:
    - ibm.mas_devops.cp4d_db2wh_restore
```

License
-------

EPL-2.0
