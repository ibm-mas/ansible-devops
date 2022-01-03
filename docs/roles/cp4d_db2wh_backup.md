cp4d_db2wh_backup
==========

This role runs a backup procedure from a CloudPak for Data DB2 Warehouse instance and stores the backup files in a targetted local folder.
At the end of the backup process, you will find the required files to run a successful restore process in the chosen `DB2WH_BACKUP_DIR`:

- DB2 backup files i.e `BLUDB.0.db2inst1.DBPART000.202XXXXXXXXXXX.001`
- DB2 keystore files (.p12 and .sth)
- DB2 instance master key label file (.kdb)

Role Variables
--------------

### Required Variables

- `DB2WH_BACKUP_DIR` Local directory that will store the backup files taken from the DB2 Warehouse instance i.e `/Users/Documents/db_backup`
- `CPD_NAMESPACE_SOURCE` CloudPak for Data namespace for the source DB2 Warehouse instance where you want to take the backup from, i.e `cpd-meta-ops`
- `DB2WH_INSTANCE_ID_SOURCE` DB2 Warehouse source instance to take the backup from i.e `db2wh-1641225392061940`

Example Playbook - Backup process only
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

### Optional Variables

In addition to the above, these are the optional variables you can set before running a playbook to run an end-to-end DB2 backup & restore process:

- `CPD_NAMESPACE_TARGET` CloudPak for Data namespace for the target DB2 Warehouse instance where you want to restore the backup to, i.e `cpd-services`
- `DB2WH_INSTANCE_ID_TARGET` DB2 Warehouse source instance to restore the backup to, i.e `db2wh-1641225392061935`
- `OC_LOGIN_TARGET` Optionally, provide Openshift login command for the target cluster where you want to restore the backup to. Only needed if you want to run the backup and restore process end-to-end and target DB2 Warehouse instance is hosted in different cluster than the source DB2 Warehouse instance.

Example Playbook - Backup & Restore (End-to-end process) 
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2wh_backup_folder: "{{ lookup('env', 'DB2WH_BACKUP_DIR') }}"
    cpd_meta_namespace_source: "{{ lookup('env', 'CPD_NAMESPACE_SOURCE') }}"
    db2wh_instance_id_source: "{{ lookup('env', 'DB2WH_INSTANCE_ID_SOURCE') }}"
    cpd_meta_namespace_target: "{{ lookup('env', 'CPD_NAMESPACE_TARGET') }}"
    db2wh_instance_id_target: "{{ lookup('env', 'DB2WH_INSTANCE_ID_TARGET') }}"
    oc_login_target: "{{ lookup('env', 'OC_LOGIN_TARGET') }}" # only needed if source and target db2wh instances are in different clusters
  roles:
    - ibm.mas_devops.cp4d_db2wh_backup
    - ibm.mas_devops.cp4d_db2wh_restore
```

License
-------

EPL-2.0
