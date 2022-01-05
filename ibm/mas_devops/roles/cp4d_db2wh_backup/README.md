cp4d_db2wh_backup
==========

This role runs a backup procedure from a CloudPak for Data DB2 Warehouse instance and stores the backup files in a targetted local folder.
At the end of the backup process, you will find the required files to run a successful restore process in the chosen `DB2WH_BACKUP_DIR`:

- DB2 backup files i.e `BLUDB.0.db2inst1.DBPART000.202XXXXXXXXXXX.001`
- DB2 keystore files (.p12 and .sth)
- DB2 instance master key label file (.kdb)

Role Variables
--------------

### db2wh_backup_dir
Required. Local directory that will store the backup files taken from the DB2 Warehouse instance i.e `/Users/Documents/db_backup`.

- Environment Variable: `DB2WH_BACKUP_DIR`
- Default: None

### cpd_meta_namespace_source
Required. CloudPak for Data namespace for the source DB2 Warehouse instance where you want to take the backup from, i.e `cpd-meta-ops`.

- Environment Variable: `CPD_NAMESPACE_SOURCE`
- Default: None

### db2wh_instance_id_source
Required. DB2 Warehouse source instance to take the backup from i.e `db2wh-1641225392061945`.

- Environment Variable: `DB2WH_INSTANCE_ID_SOURCE`
- Default: None

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2wh_backup_folder: "{{ lookup('env', 'DB2WH_BACKUP_DIR') }}"
    cpd_meta_namespace_source: "{{ lookup('env', 'CPD_NAMESPACE_SOURCE') }}"
    db2wh_instance_id_source: "{{ lookup('env', 'DB2WH_INSTANCE_ID_SOURCE') }}"
  roles:
    - ibm.mas_devops.cp4d_db2wh_backup
```

License
-------

EPL-2.0
