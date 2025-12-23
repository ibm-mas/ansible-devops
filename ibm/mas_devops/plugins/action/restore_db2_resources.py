#!/usr/bin/env python3
import logging
import urllib3

from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.utils.display import Display
from kubernetes.dynamic import DynamicClient
from kubernetes.dynamic.exceptions import NotFoundError

from ansible_collections.ibm.mas_devops.plugins.module_utils.backuprestore import createBackupDirectories, backupSecret, getSubscription, getDb2uInstance, getDb2VersionFromCR, isDb2uReady

import yaml
import os
import base64

from mas.devops.ocp import createNamespace, apply_resource

urllib3.disable_warnings()  # Disabling warnings will prevent InsecureRequestWarnings from dynClient
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

display = Display()

def checkBackupDirectoryExists(db2_backup_path: str, db2_backup_version: str):

    if not os.path.exists(db2_backup_path):
        raise AnsibleError(f"DB2 Backup path {db2_backup_path} does not exist.")
    
    db2_resources_path = os.path.join(db2_backup_path, "resources")

    if not os.path.exists(db2_resources_path):
        raise AnsibleError(f"Db2 instance resources backup path {db2_resources_path} does not exist.")

    cr_path = os.path.join(db2_resources_path, "cr.yaml")
    if not os.path.exists(cr_path):
        raise AnsibleError(f"Db2 instance CR backup file {cr_path} does not exist.")
    
    db2_secrets_path = os.path.join(db2_resources_path, "secrets")
    if not os.path.exists(db2_secrets_path):
        raise AnsibleError(f"Db2 instance resources secrets backup path {db2_secrets_path} does not exist.")

    return True


class ActionModule(ActionBase):
    
    """
    Usage Example
    -------------
    tasks:
      - name: "Restore Db2u instance resources (CR, secrets, configmaps, issuers, certificates)"
        ibm.mas_devops.restore_db2_instance:
    """
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        # Initialize DynamicClient and grab the task args
        host = self._task.args.get('host', None)
        api_key = self._task.args.get('api_key', None)

        dynClient = get_api_client(api_key=api_key, host=host)

        mas_backup_dir = self._task.args.get('mas_backup_dir', None)
        db2_backup_version = self._task.args.get('db2_backup_version', None)

        if not mas_backup_dir or mas_backup_dir == '':
            raise AnsibleError("mas_backup_dir is a required parameter and cannot be empty")
        if not db2_backup_version or db2_backup_version == '':
            raise AnsibleError("db2_backup_version is a required parameter and cannot be empty")

        # Check if backup directory exists
        db2_backup_path = os.path.join(mas_backup_dir, f"backup-{db2_backup_version}-db2u")
        checkBackupDirectoryExists(db2_backup_path, db2_backup_version)
        display.v(f"Db2 backup path {db2_backup_path} exists. Proceeding with restore...")

        db2_backup_resource_path = os.path.join(db2_backup_path, "resources")
        # Get DB2 instance name from backed up CR
        cr_path = os.path.join(db2_backup_resource_path, "cr.yaml")
        
        # read cr.yaml
        with open(cr_path, 'r') as cr_file:
            backup_db2u_cr = yaml.safe_load(cr_file)
        display.v("Successfully read DB2 backup CR file")

        db2_instance_name = backup_db2u_cr['metadata']['name']
        db2_namespace = backup_db2u_cr['metadata']['namespace']

        # Check if Db2u instance is already present
        db2u_instance_cr = getDb2uInstance(dynClient, db2_instance_name, db2_namespace)
        if db2u_instance_cr is not None:
            display.v(f"Db2u instance {db2_instance_name} already exists in namespace {db2_namespace}. Checking if it is ready...")
            if isDb2uReady(db2u_instance_cr):
                display.v(f"Db2u instance {db2_instance_name} is already in Ready state. Checking version...")
                if getDb2VersionFromCR(db2u_instance_cr) == getDb2VersionFromCR(backup_db2u_cr):
                    display.v(f"Db2u instance {db2_instance_name} version matches the backup version. Skipping DB2 instance restore...")
                    return dict(
                        changed=False,
                        failed=False,
                        proceed=False,
                        success=True,
                        msg=f"Db2u instance {db2_instance_name} is already in Ready state. Skipping DB2 instance restore..."
                    )
                else:
                    display.v(f"Db2u instance {db2_instance_name} version does not match the backup version. Abandoning restore... Check the instance manually.")
                    return dict(
                        changed=False,
                        failed=True,
                        proceed=False,
                        success=False,
                        msg=f"Db2u instance {db2_instance_name} version does not match the backup version. Abandoning restore... Check the instance manually."
                    )
            else:
                display.v(f"Db2u instance {db2_instance_name} is not in Ready state. Abandoning restore... Check the instance status manually.")
                return dict(
                    changed=False,
                    failed=True,
                    proceed=False,
                    success=False,
                    msg=f"Db2u instance {db2_instance_name} is not in Ready state. Abandoning restore... Check the instance status manually."
                )
        else:
            display.v(f"Db2u instance {db2_instance_name} does not exist in namespace {db2_namespace}. Proceeding with B2 instance restore...")

        # =======================================================
        # 1. Create DB2 namespace if not exists
        # =======================================================
        display.v(f"Creating Db2 namespace '{db2_namespace}' if it does not already exist")
        createNamespace(dynClient, db2_namespace)

        # =======================================================
        # 2. Restore Db2 Secret resources from backup
        # =======================================================
        display.v(f"Restoring Db2 Secret resources from backup path '{db2_backup_resource_path}/secrets'")
        db2_secrets_path = os.path.join(db2_backup_resource_path, "secrets")
        secret_files = os.listdir(db2_secrets_path)
        for secret_file in secret_files:
            # Some info files will be kept in secrets folder with NOT_SECRET in the filename
            if "NOT_SECRET" in secret_file:
                continue
            display.v(f"Restoring Db2 Secret resource from backup file '{secret_file}'")
            with open(os.path.join(db2_secrets_path, secret_file), 'r') as f:
                secret_yaml = f.read()
                apply_resource(dynClient, secret_yaml, db2_namespace)
        
        # =======================================================
        # 3. Gather info from backup files to recreate new Db2u instance
        # =======================================================

        db2_info = {}
        db2_info['db2_instance_name'] = db2_instance_name
        db2_info['db2_namespace'] = db2_namespace
        db2_info['db2_type'] = backup_db2u_cr['spec'].get('environment', {}).get('dbType', 'db2wh')
        # Get DB name from backup CR
        db2_info['db2_database_name'] = backup_db2u_cr['spec'].get('environment', {}).get('database', {}).get('name', 'BLUDB')

        # Get Db2 configs from backup CR
        db2_info['db2_database_db_config'] = backup_db2u_cr['spec'].get('environment', {}).get('database', {}).get('dbConfig', {})
        db2_info['db2_instance_dbm_config'] = backup_db2u_cr['spec'].get('environment', {}).get('instance', {}).get('dbmConfig', {})
        db2_info['db2_instance_registry'] = backup_db2u_cr['spec'].get('environment', {}).get('instance', {}).get('registry', {})

        # Get dftTableOrg
        db2_info['db2_table_org'] = backup_db2u_cr['spec'].get('environment', {}).get('database', {}).get('settings', {}).get('dftTableOrg', 'ROW')

        # Get Pod config
        db2_pod_config = backup_db2u_cr['spec'].get('podConfig', {}).get('db2u', {}).get('resource', {}).get('db2u', {})
        db2_info['db2_cpu_requests'] = db2_pod_config.get('requests', {}).get('cpu', None)
        db2_info['db2_memory_requests'] = db2_pod_config.get('requests', {}).get('memory', None)
        db2_info['db2_cpu_limits'] = db2_pod_config.get('limits', {}).get('cpu', None)
        db2_info['db2_memory_limits'] = db2_pod_config.get('limits', {}).get('memory', None)

        # Get LDAP user info if present
        ldap_info_file_path = os.path.join(db2_backup_resource_path, "ldapuser-NOT_SECRET.yaml")
        if os.path.exists(ldap_info_file_path):
            with open(ldap_info_file_path, 'r') as ldap_info_file:
                ldap_info = yaml.safe_load(ldap_info_file)
                db2_info['db2_ldap_username'] = ldap_info['db2_ldap_username']
                db2_info['db2_ldap_password'] = ldap_info['db2_ldap_password']
            display.v(f"Successfully read LDAP user info from {ldap_info_file_path}")
        
        # Get DB2 backup info file
        db2_info_file_path = os.path.join(db2_backup_resource_path, "db2-backup-info.yaml")
        if os.path.exists(db2_info_file_path):
            with open(db2_info_file_path, 'r') as info_file:
                backup_db2_info = yaml.safe_load(info_file)
                db2_info['db2_version'] = backup_db2_info['db2_version']
                db2_info['db2_channel'] = backup_db2_info['db2_channel']
            display.v(f"Successfully read Db2 backup info from {db2_info_file_path}")
        else:
            db2_info['db2_version'] = getDb2VersionFromCR(backup_db2u_cr)
            if "s11.5.9.0" in db2_info['db2_version']:
                db2_info['db2_channel'] = "v110509.0"
            else:
                display.v("Warning: Could not find Db2 backup info file. Using default channel for the version from CR.")
        
        return dict(
            message=f"Successfully restored Db2 instance's Secrets from backup paths.",
            failed=False,
            changed=False,
            success=True,
            proceed=True,
            **db2_info
        )
