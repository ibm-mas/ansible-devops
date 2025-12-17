#!/usr/bin/env python3
import logging
import urllib3

from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.utils.display import Display
from kubernetes.dynamic import DynamicClient
from kubernetes.dynamic.exceptions import NotFoundError

from ansible_collections.ibm.mas_devops.plugins.module_utils.backuprestore import createBackupDirectories, backupSecret, getSubscription

import yaml
import os
import base64

from mas.devops.ocp import getCR, getSecret

urllib3.disable_warnings()  # Disabling warnings will prevent InsecureRequestWarnings from dynClient
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

display = Display()


def filterDb2CR(crData: dict) -> dict:
    """
    Filter out unnecessary fields from a Custom Resource
    """
    metadata_fields_to_remove = [
        'annotations',
        'creationTimestamp',
        'generation',
        'resourceVersion',
        'selfLink',
        'uid',
        'managedFields'
    ]
    filteredCR = crData.copy()
    if 'metadata' in filteredCR:
        for field in metadata_fields_to_remove:
            if field in filteredCR['metadata']:
                del filteredCR['metadata'][field]
    # remove status field
    if 'status' in filteredCR:
        del filteredCR['status']
    
    return filteredCR

def isDb2uReady(db2uCR: dict) -> bool:
    """
    Check if Db2uCluster/Db2uInstance is in ready state
    """
    if 'status' in db2uCR:
        status = db2uCR['status']
        if 'state' in status and status['state'] == 'Ready':
            return True
    return False

def getDb2uInstance(DynamicClient, db2_instance_name: str, db2_namespace: str):
    """
    Retrieve Db2uCluster CR instance
    """
    
    db2uCR = getCR(DynamicClient, cr_api_version="db2u.databases.ibm.com/v1", cr_kind="Db2uCluster", cr_name=db2_instance_name, namespace=db2_namespace)
    if db2uCR:
        return db2uCR.to_dict()
    else:
        # Db2uCluster CR not found, try Db2uInstance
        db2uCR = getCR(DynamicClient, cr_api_version="db2u.databases.ibm.com/v1", cr_kind="Db2uInstance", cr_name=db2_instance_name, namespace=db2_namespace)
        if db2uCR:
            return db2uCR.to_dict()
    return None

def backupDB2uCR(db2u_cr: dict, backup_path: str) -> bool:
    """
    Backup Db2uCluster/Db2uInstance CR to specified backup path
    """
    try:
        filteredCR = filterDb2CR(db2u_cr)
        backup_file_path = os.path.join(backup_path, "cr.yaml")
        with open(backup_file_path, 'w') as backup_file:
            yaml.dump(filteredCR, backup_file)
        display.v(f"Backed up Db2u CR to {backup_file_path}")
        return True
    except Exception as e:
        display.v(f"Error backing up Db2u CR: {e}")
        return False

def getImagePullSecretFromCR(db2uCR: dict) -> list:
    """
    Extract image pull secret name from Db2uCluster/Db2uInstance CR
    """
    try:
        if 'spec' in db2uCR and 'account' in db2uCR['spec'] and 'imagePullSecrets' in db2uCR['spec']['account']:
            image_pull_secrets = db2uCR['spec']['account']['imagePullSecrets']
            if isinstance(image_pull_secrets, list) and len(image_pull_secrets) > 0:
                return image_pull_secrets
        return None
    except Exception as e:
        display.v(f"Error extracting image pull secret from CR: {e}")
        return None

def getDb2VersionFromCR(db2uCR: dict) -> str:
    """
    Extract Db2 version from Db2uCluster/Db2uInstance CR
    """
    try:
        if 'spec' in db2uCR and 'version' in db2uCR['spec']:
            return db2uCR['spec']['version']
        return None
    except Exception as e:
        display.v(f"Error extracting Db2 version from CR: {e}")
        return None

def processUserCredentialsSecret(dynClient: DynamicClient, mas_instance_id: str, db2_instance_name: str, backup_path: str) -> bool:
    """
    Process user credentials secret for Db2u instance
    Check user credentials from jdbc credentials secret in Core namespace
    If the user is not the default db2inst1 user, backup the jdbc credentials secret as well
    this will be used during restore to set the correct user
    """
    jdbc_core_secret_name = f"jdbc-{db2_instance_name}-credentials".lower()
    jdbc_core_secret = getSecret(dynClient, namespace=f"mas-{mas_instance_id}-core".lower(), secret_name=jdbc_core_secret_name)
    if jdbc_core_secret:
        if 'data' in jdbc_core_secret and 'username' in jdbc_core_secret['data']:
            username_encoded = jdbc_core_secret['data']['username']
            username = base64.b64decode(username_encoded).decode('utf-8')
            if username.lower() != 'db2inst1':
                # Backup the jdbc credentials secret
                backup_status = backupSecret(dynClient=dynClient, namespace=f"mas-{mas_instance_id}-core".lower(), secret_name=jdbc_core_secret_name, backup_path=backup_path)
                if backup_status:
                    display.v(f"Backed up JDBC credentials secret '{jdbc_core_secret_name}' for Db2u instance '{db2_instance_name}'")
                    return True
                else:
                    display.v(f"Warning: Failed to backup JDBC credentials secret '{jdbc_core_secret_name}' for Db2u instance '{db2_instance_name}'")
                    return False
            else:
                display.v(f"JDBC credentials secret '{jdbc_core_secret_name}' uses default admin user. No additional user backup needed.")
        return False

class ActionModule(ActionBase):
    
    """
    Usage Example
    -------------
    tasks:
      - name: "Backup Db2u instance resources (CR, secrets, configmaps, issuers, certificates)"
        ibm.mas_devops.backup_db2_instance:
    """
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        # Initialize DynamicClient and grab the task args
        host = self._task.args.get('host', None)
        api_key = self._task.args.get('api_key', None)

        dynClient = get_api_client(api_key=api_key, host=host)

        db2_instance_name = self._task.args.get('db2_instance_name', None)
        db2_namespace = self._task.args.get('db2_namespace', None)
        db2_backup_path = self._task.args.get('db2_backup_path', None)
        mas_instance_id = self._task.args.get('mas_instance_id', None)
        db2_dbname = self._task.args.get('db2_dbname', None)

        if not db2_instance_name or db2_instance_name == '':
            raise AnsibleError("db2_instance_name is a required parameter and cannot be empty")
        if not db2_namespace or db2_namespace == '':
            raise AnsibleError("db2_namespace is a required parameter and cannot be empty")
        if not db2_backup_path or db2_backup_path == '':
            raise AnsibleError("db2_backup_path is a required parameter and cannot be empty")
        if not mas_instance_id or mas_instance_id == '':
            raise AnsibleError("mas_instance_id is a required parameter and cannot be empty")
        if not db2_dbname or db2_dbname == '':
            raise AnsibleError("db2_dbname is a required parameter and cannot be empty")

        # Prepare backup resource path
        db2_backup_resource_path = f"{db2_backup_path}/resources"
        db2_backup_secrets_path = f"{db2_backup_resource_path}/secrets"
        #db2_backup_issuers_path = f"{db2_backup_resource_path}/issuers"

        # Create backup directory if it does not exist
        createBackupDirectories([db2_backup_path, db2_backup_resource_path, db2_backup_secrets_path])

        # Get Db2uCluster or Db2uInstance CR
        db2u_cr = getDb2uInstance(DynamicClient=dynClient, db2_instance_name=db2_instance_name, db2_namespace=db2_namespace)
        if not db2u_cr:
            raise AnsibleError(f"Db2uCluster or Db2uInstance CR '{db2_instance_name}' not found in namespace '{db2_namespace}'")
        
        # Check if db2u instance is in a ready state
        if not isDb2uReady(db2u_cr):
            raise AnsibleError(f"Db2u instance '{db2_instance_name}' is not in a ready state. Cannot proceed with backup.")
        
        # Backup Db2uCluster/Db2uInstance CR
        backup_cr_status = backupDB2uCR(db2u_cr=db2u_cr, backup_path=db2_backup_resource_path)
        if not backup_cr_status:
            raise AnsibleError(f"Failed to backup Db2u CR for instance '{db2_instance_name}'")
        
        # Backup Db2u Secrets
        # Backup image pull secret if specified in CR
        image_pull_secrets = getImagePullSecretFromCR(db2u_cr)
        if image_pull_secrets:
            for secret in image_pull_secrets:
                backupSecretStatus = backupSecret(dynClient=dynClient, namespace=db2_namespace, secret_name=secret, backup_path=db2_backup_secrets_path)
                if not backupSecretStatus:
                    display.v(f"Warning: Failed to backup image pull secret '{secret}' for Db2u instance '{db2_instance_name}'")
                else:
                    display.v(f"Backed up image pull secret '{secret}' for Db2u instance '{db2_instance_name}'")
        
        # Backup Db2u instance secret
        db2_instance_secret_name = f"c-{db2_instance_name}-instancepassword"
        backupSecretStatus = backupSecret(dynClient=dynClient, namespace=db2_namespace, secret_name=db2_instance_secret_name, backup_path=db2_backup_secrets_path)
        if not backupSecretStatus:
            display.v(f"Warning: Failed to backup Db2u instance secret '{db2_instance_secret_name}' for Db2u instance '{db2_instance_name}'")
        else:
            display.v(f"Backed up Db2u instance secret '{db2_instance_secret_name}' for Db2u instance '{db2_instance_name}'")

        # Check user credentials from jdbc credentials secret in Core namespace
        # If the user is not the default admin user, backup the jdbc credentials secret as well
        # this will be used during restore to set the correct user
        # If secret does not exist or uses default user, no action is taken.
        # Restore process will use default instance user in that case
        processUserCredentialsSecret(dynClient=dynClient, mas_instance_id=mas_instance_id, db2_instance_name=db2_instance_name, backup_path=db2_backup_secrets_path)

        # Get Channel details from Subscription
        # Package name hardcoded to db2u-operator
        subscription = getSubscription(dynClient=dynClient, namespace=db2_namespace, package_name="db2u-operator")
        channel_name = None
        if subscription:
            if 'spec' in subscription and 'channel' in subscription['spec']:
                channel_name = subscription['spec']['channel']
        else:
            display.v(f"Warning: Subscription 'db2u-operator' not found in namespace '{db2_namespace}'. Cannot retrieve channel information.")
            raise AnsibleError(f"Failed to retrieve Subscription for Db2u operator in namespace '{db2_namespace}'")

        # write db2-info.yaml file
        # using str() to ensure no yaml serialization issues with non-string types
        # Ansible wraps variables with metadata
        db2_info = {
            'db2_instance_name': str(db2_instance_name),
            'db2_namespace': str(db2_namespace),
            'db2_dbname': str(db2_dbname),
            'mas_instance_id': str(mas_instance_id),
            'db2_version': getDb2VersionFromCR(db2uCR=db2u_cr),
            'db2_channel': channel_name
        }

        db2_info_file_path = os.path.join(db2_backup_resource_path, "db2-info.yaml")
        with open(db2_info_file_path, 'w') as info_file:
            yaml.dump(db2_info, info_file)
        display.v(f"Wrote Db2 instance info to {db2_info_file_path}")

        return dict(
            message=f"Successfully backed up Standalone Db2 Universal Operator instance '{db2_instance_name}' resources",
            failed=False,
            changed=False,
            success=True,
        )