db2_restore
===========

This role runs a restore procedure onto a Db2uCluster instance.  In order to begin the restore process, you must have the required files to run a successful restore process in the chosen `db2_restore_dir`:

- DB2 backup files i.e `BLUDB.0.db2inst1.DBPART000.202XXXXXXXXXXX.001`
- DB2 keystore files (.p12 and .sth)
- DB2 instance master key label file (.kdb)

Note: These files are generated automatically if you run `ibm.mas_devops.db2_backup` role. If any of the above files are not found in the directory specified by `db2_restore_dir` the restore process will fail.

Role Variables
--------------

### db2_restore_dir
Local directory that stores the backup files to be used in the DB2 Warehouse restore process

- **Required**
- Environment Variable: `DB2WH_RESTORE_DIR`
- Default: None

### db2_restore_instance_name
DB2 Warehouse target instance to restore the backup to.

- **Required**
- Environment Variable: `DB2_RESTORE_INSTANCE_NAME`
- Default: None

### db2_dbname
Name of the database within the instance.

- Optional
- Environment Variable: `DB2_DBNAME`
- Default: `BLUDB`

Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    # Backup mydb1 and restore it to mydb2
    db2_backup_dir: "/tmp/db2backup"
    db2_backup_instance_name: "mydb1"

    db2_restore_dir: "/tmp/db2backup"
    db2_restore_instance_name: "mydb2"
  roles:
    - ibm.mas_devops.db2_backup
    - ibm.mas_devops.db2_restore
```

License
-------

EPL-2.0
