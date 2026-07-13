#!/usr/bin/env python3

import urllib3
from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.utils.display import Display
from kubernetes.dynamic import DynamicClient
from kubernetes.dynamic.exceptions import NotFoundError

from mas.devops.ocp import getCR

# Disabling warnings will prevent InsecureRequestWarnings from dynClient
urllib3.disable_warnings()
display = Display()

def isMongoRunning(mongoCR: dict) -> bool:
    """
    Check if MongoDB Community instance is running
    return True if running, else False
    """
    display.v(f"Checking if MongoDB Community instance is in 'Running' state")
    if 'status' in mongoCR:
        if 'phase' in mongoCR['status']:
            if mongoCR['status']['phase'] == 'Running':
                display.v(f"MongoDB Community instance is in 'Running' state")
                return True
    display.v(f"MongoDB Community instance is not in 'Running' state")
    return False

def getMongoceCR(dynClient: DynamicClient, mongodb_instance_name: str, mongodb_namespace: str) -> dict:
    """
    Check if MongoDB Community instance exists
    return cr if exists, else return empty dict
    """
    display.v(f"Checking if MongoDB Community instance '{mongodb_instance_name}' exists in namespace '{mongodb_namespace}'")
    mongodbCR = getCR(
        dynClient=dynClient,
        cr_api_version="mongodbcommunity.mongodb.com/v1",
        cr_kind="MongoDBCommunity",
        cr_name=mongodb_instance_name,
        namespace=mongodb_namespace
    )
    if mongodbCR:
        return mongodbCR.to_dict()
    else:
        return {}


class ActionModule(ActionBase):
    """
    Usage Example
    -------------
    tasks:
      - name: "Verify Existing MongoDB version
        ibm.mas_devops.verify_mongoce_version:
    """
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        # Initialize DynamicClient and grab the task args
        host = self._task.args.get('host', None)
        api_key = self._task.args.get('api_key', None)

        dynClient = get_api_client(api_key=api_key, host=host)

        mongodb_instance_name = self._task.args.get('mongodb_instance_name')
        mongodb_namespace = self._task.args.get('mongodb_namespace')

        if mongodb_instance_name is None:
            raise AnsibleError(f"Error: mongodb_instance_name argument was not provided")
        if mongodb_namespace is None:
            raise AnsibleError(f"Error: mongodb_namespace argument was not provided")

        # Check for existing MongoDb install
        mongodbCR = getMongoceCR(
            dynClient=dynClient,
            mongodb_instance_name=mongodb_instance_name,
            mongodb_namespace=mongodb_namespace
        )

        if not mongodbCR:
            display.v(f"MongoDB Community instance '{mongodb_instance_name}' does NOT exist in namespace '{mongodb_namespace}'")
            return dict(
                message=f"MongoDB Community instance '{mongodb_instance_name}' does NOT exist in namespace '{mongodb_namespace}'",
                success=True,
                failed=False,
                exist=False,
                running=False
            )
        elif isMongoRunning(mongodbCR):
            display.v(f"MongoDB Community instance '{mongodb_instance_name}' is running version '{mongodbCR['spec']['version']}' in namespace '{mongodb_namespace}'")
            return dict(
                message=f"MongoDB Community instance '{mongodb_instance_name}' is running version '{mongodbCR['spec']['version']}' in namespace '{mongodb_namespace}'",
                success=True,
                failed=False,
                exist=True,
                running=True,
                mongoce_version=mongodbCR['spec']['version']
            ) 
        else:
            display.v(f"MongoDB Community instance '{mongodb_instance_name}' is NOT in 'Running' state in namespace '{mongodb_namespace}'")
            return dict(
                message=f"MongoDB Community instance '{mongodb_instance_name}' is NOT in 'Running' state in namespace '{mongodb_namespace}'",
                success=True,
                failed=False,
                exist=True,
                running=False,
                mongoce_version=mongodbCR['spec']['version']
            )
