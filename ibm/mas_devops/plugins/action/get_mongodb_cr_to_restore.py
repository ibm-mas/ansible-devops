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
import base64
import os

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
      - name: "Retrieve and Set facts from MongoDB instance CR and resources"
        ibm.mas_devops.get_mongodb_cr_to_restore:
    """
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        mas_backup_dir = self._task.args.get('mas_backup_dir')
        mongodb_backup_version = self._task.args.get('mongodb_backup_version')

        if mas_backup_dir is None or mas_backup_dir == "":
            raise AnsibleError(f"Error: mongodb_instance_name argument was not provided")
        
        if mongodb_backup_version is None or mongodb_backup_version == "":
            raise AnsibleError(f"Error: mongodb_backup_version argument was not provided")

        mongodb_backup_path = f"{mas_backup_dir}/backup-{mongodb_backup_version}-mongoce"

        # check if backup directory exists
        display.v(f"Checking if MongoDB backup directory exists at path: {mongodb_backup_path}")
        if not os.path.isdir(mongodb_backup_path):
            raise AnsibleError(f"Directory {mongodb_backup_path} does NOT exist!")
        display.v(f"MongoDB backup directory exists at path: {mongodb_backup_path}")

        # check if cr.yaml exsits
        mongodb_cr_file = f"{mongodb_backup_path}/cr.yaml"
        display.v(f"Checking if MongoDB backup CR file exists at path: {mongodb_cr_file}")
        if not os.path.isfile(mongodb_cr_file):
            raise AnsibleError(f"MongoDB backup CR file does NOT exist at path: {mongodb_cr_file}")
        display.v(f"MongoDB backup CR file exists at path: {mongodb_cr_file}")

        # read cr.yaml
        with open(mongodb_cr_file, 'r') as cr_file:
            mongodb_cr = yaml.safe_load(cr_file)
        display.v("Successfully read MongoDB backup CR file")


        return dict(
            message=f"Successfully set mongodb CR as facts from backup at '{mongodb_backup_path}'",
            failed=False,
            changed=False,
            success=True,
            mongodb_cr= mongodb_cr
        )


