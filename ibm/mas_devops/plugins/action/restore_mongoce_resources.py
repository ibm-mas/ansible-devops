#!/usr/bin/env python3

import logging
import urllib3

from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.utils.display import Display
from kubernetes.dynamic import DynamicClient
from kubernetes.dynamic.exceptions import NotFoundError

import yaml
import os
from mas.devops.ocp import createNamespace, apply_resource

urllib3.disable_warnings()  # Disabling warnings will prevent InsecureRequestWarnings from dynClient
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

display = Display()

def display_information(mongoDBCommunityCR : dict):
    display.v(f"MongoCE instance name .......................... {mongoDBCommunityCR['metadata']['name']}")
    display.v(f"MongoCE namespace .............................. {mongoDBCommunityCR['metadata']['namespace']}")
    display.v(f"MongoDB Version ................................ {mongoDBCommunityCR['spec']['version']}")

class ActionModule(ActionBase):
    """
    Usage Example
    -------------
    tasks:
      - name: "Restore MongoDB instance resources (secrets, issuers, certificates)"
        ibm.mas_devops.restore_mongoce_resources:
    """
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        # Initialize DynamicClient and grab the task args
        host = self._task.args.get('host', None)
        api_key = self._task.args.get('api_key', None)

        dynClient = get_api_client(api_key=api_key, host=host)

        mongodb_namespace = self._task.args.get('mongodb_namespace')
        mongodb_backup_secrets_path = self._task.args.get('backup_secrets_path')
        mongodb_backup_issuers_path = self._task.args.get('backup_issuers_path')
        mongodb_backup_certs_path = self._task.args.get('backup_certificates_path')

        if mongodb_namespace is None:
            raise AnsibleError(f"Error: mongodb_namespace argument was not provided")
        if mongodb_backup_secrets_path is None:
            raise AnsibleError(f"Error: mongodb_backup_secrets_path argument was not provided")
        if mongodb_backup_issuers_path is None:
            raise AnsibleError(f"Error: mongodb_backup_issuers_path argument was not provided")
        if mongodb_backup_certs_path is None:
            raise AnsibleError(f"Error: mongodb_backup_certs_path argument was not provided")
        
        # =======================================================
        # 1. Create MongoDB namespace if not exists
        # =======================================================
        display.v(f"Creating MongoDB namespace '{mongodb_namespace}' if it does not already exist")
        createNamespace(dynClient, mongodb_namespace)
        
        # =======================================================
        # 2. Restore MongoDB Secret resources from backup
        # =======================================================
        display.v(f"Restoring MongoDB Secret resources from backup path '{mongodb_backup_secrets_path}'")
        secret_files = os.listdir(mongodb_backup_secrets_path)
        for secret_file in secret_files:
            with open(os.path.join(mongodb_backup_secrets_path, secret_file), 'r') as f:
                secret_yaml = f.read()
                apply_resource(dynClient, secret_yaml, mongodb_namespace)
        
        # =======================================================
        # 3. Restore MongoDB Issuer resources from backup
        # =======================================================
        display.v(f"Restoring MongoDB Issuer resources from backup path '{mongodb_backup_issuers_path}'")
        issuer_files = os.listdir(mongodb_backup_issuers_path)
        for issuer_file in issuer_files:
            with open(os.path.join(mongodb_backup_issuers_path, issuer_file), 'r') as f:
                issuer_yaml = f.read()
                apply_resource(dynClient, issuer_yaml, mongodb_namespace)
        
        # =======================================================
        # 4. Restore MongoDB Certificate resources from backup
        # =======================================================
        display.v(f"Restoring MongoDB Certificate resources from backup path '{mongodb_backup_certs_path}'")
        cert_files = os.listdir(mongodb_backup_certs_path)
        for cert_file in cert_files:
            with open(os.path.join(mongodb_backup_certs_path, cert_file), 'r') as f:
                cert_yaml = f.read()
                apply_resource(dynClient, cert_yaml, mongodb_namespace)
        
        
        return dict(
            message=f"Successfully restored MongoDB instance's Secrets, Issuers and Certificates from backup paths.",
            failed=False,
            changed=False,
            success=True,
            restored=True
        )


