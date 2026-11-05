#!/usr/bin/env python3

import logging
import urllib3

from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.utils.display import Display

import yaml
import base64

from mas.devops.ocp import getSecret
from ansible_collections.ibm.mas_devops.plugins.module_utils.mongo import (
    getMongoAdminSecretName, isMongoRunning, getMongoCR, getMongoVersion,
    getMongoDBServiceName, getPodNameFromLabels
)

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
      - name: "Retrieve info from MongoDB instance CR and resources"
        ibm.mas_devops.get_mongoce_info:
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
        
        display.v(f"Retrieving MongoDB Community instance '{mongodb_instance_name}' in namespace '{mongodb_namespace}'")

        # 1. Check if MongoDB Community instance exists
        mongodb_cr = getMongoCR(dynClient, mongodb_instance_name, mongodb_namespace)
        if not mongodb_cr:
            raise AnsibleError(f"Error: MongoDB Community instance '{mongodb_instance_name}' does not exist in namespace '{mongodb_namespace}'")
        else:
            display.v(f"MongoDB Community instance '{mongodb_instance_name}' exists in namespace '{mongodb_namespace}'")

        # 2. Check if MongoDB Community instance is in 'Running' state
        if not isMongoRunning(mongodb_cr):
            raise AnsibleError(f"Error: MongoDB Community instance '{mongodb_instance_name}' is not in 'Running' state")
        
        display_information(mongodb_cr)
        
        # 3. Lookup mongoce Pod to retrieve mongo pod name
        mongoce_pod_name = getPodNameFromLabels(
            dynClient=dynClient,
            namespace=mongodb_namespace,
            label_selector="apps.kubernetes.io/pod-index=0"
        )
        if not mongoce_pod_name:
            raise AnsibleError(f"Error: Could not find Pod for MongoDB Community instance '{mongodb_instance_name}' in namespace '{mongodb_namespace}'")

        # 4. Retrieve MongoDB admin Secret data
        mongodb_admin_secretname = getMongoAdminSecretName(mongodb_cr)
        mongodb_admin_secret = getSecret(
            dynClient=dynClient,
            namespace=mongodb_namespace,
            secret_name=mongodb_admin_secretname
        )
        if not mongodb_admin_secret:
            raise AnsibleError(f"Error: Could not find admin Secret '{mongodb_admin_secretname}' for MongoDB Community instance '{mongodb_instance_name}' in namespace '{mongodb_namespace}'")

        # 5. Retrieve mongodb service name
        mongodb_service_name = getMongoDBServiceName(mongodb_cr)
        if not mongodb_service_name:
            raise AnsibleError(f"Error: Could not find MongoDB Service name for MongoDB Community instance '{mongodb_instance_name}' in namespace '{mongodb_namespace}'")
        
        # 6. Construct mongodb_host
        mongodb_host = f"{mongoce_pod_name}.{mongodb_service_name}.{mongodb_namespace}.svc.cluster.local:27017"

        mongo_info = dict(
            mongoce_pod_name=mongoce_pod_name,
            mongodb_admin_user="admin",
            mongodb_admin_password = base64.b64decode(mongodb_admin_secret['data']['password']),
            mongodb_service_name=mongodb_service_name,
            mongodb_host=mongodb_host,
            mongodb_version=getMongoVersion(mongodb_cr)
        )

        return dict(
            message=f"Successfully set facts from MongoDB Community instance '{mongodb_instance_name}' resources",
            failed=False,
            changed=False,
            success=True,
            **mongo_info
        )


