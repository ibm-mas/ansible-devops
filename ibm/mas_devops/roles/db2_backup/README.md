db2_backup
=========

This role runs a backup procedure from Db2uCluster instance and stores the backup files in a targetted local folder.
At the end of the backup process, you will find the required files to run a successful restore process in the chosen `DB2_BACKUP_DIR`:

- DB2 backup files i.e `BLUDB.0.db2inst1.DBPART000.202XXXXXXXXXXX.001`
- DB2 keystore files (.p12 and .sth)
- DB2 instance master key label file (.kdb)

Role Variables
--------------

### db2_backup_dir
Local directory that will store the backup files taken from the DB2 Warehouse instance.

- **Required**
- Environment Variable: `DB2_BACKUP_DIR`
- Default: None

### db2_backup_instance_name
DB2 instance name to take the backup from.

- **Required**
- Environment Variable: `DB2_BACKUP_INSTANCE_NAME`
- Default: None

### db2_namespace
The namespace containing the DB instance to be backed up.

- **Required**
- Environment Variable: `DB2_NAMESPACE`
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
    db2_namespace: "db2u"
    db2_dbname: "BLUDB"

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
