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

from mas.devops.ocp import getCR, getSecret

urllib3.disable_warnings()  # Disabling warnings will prevent InsecureRequestWarnings from dynClient
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

display = Display()

def display_information(mongoDBCommunityCR : dict):
    display.v(f"MongoCE instance name .......................... {mongoDBCommunityCR['metadata']['name']}")
    display.v(f"MongoCE namespace .............................. {mongoDBCommunityCR['metadata']['namespace']}")
    display.v(f"MongoDB Version ................................ {mongoDBCommunityCR['spec']['version']}")

def get_mongoce_admin_secretname(mongoDBCommunityCR):
  """
    short_description: Get admin secret name from MongoDBCommunity CR
  """
  for user in mongoDBCommunityCR['spec']['users']:
    if 'db' in user:
      if user['db'] == 'admin' and 'passwordSecretRef' in user:
          return user['passwordSecretRef']['name']
  return None

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

def getMongoVersion(mongoCR: dict) -> str:
    """
    Get MongoDB version from MongoDB Community CR
    """
    if 'spec' in mongoCR:
        if 'version' in mongoCR['spec']:
            return mongoCR['spec']['version']
    return ""

def getMongoDBServiceName(mongoCR: dict) -> str:
    """
    Get MongoDB Service name from MongoDB Community CR
    """
    if 'spec' in mongoCR:
        if 'statefulSet' in mongoCR['spec']:
            if 'spec' in mongoCR['spec']['statefulSet']:
                if 'serviceName' in mongoCR['spec']['statefulSet']['spec']:
                    return mongoCR['spec']['statefulSet']['spec']['serviceName']
    return ""

def getPodNameFromLabels(dynClient: DynamicClient, namespace: str, label_selector: str) -> str:
    """
    Get Pod name from labels
    """
    display.v(f"Looking up Mongo Pod in namespace '{namespace}' with labels '{label_selector}'")
    try:
        podAPI = dynClient.resources.get(api_version="v1", kind="Pod")
        pods = podAPI.get(namespace=namespace, label_selector=label_selector)
        if pods.items:
            pod_name = pods.items[0]["metadata"]["name"]
            display.v(f"Found Pod '{pod_name}' in namespace '{namespace}' with labels '{label_selector}'")
            return pod_name
        else:
            display.v(f"No Pods found in namespace '{namespace}' with labels '{label_selector}'")
    except NotFoundError:
        display.v(f"No Pods found in namespace '{namespace}' with labels '{label_selector}'")
    return ""

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
        mongodb_cr = getMongoceCR(dynClient, mongodb_instance_name, mongodb_namespace)
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
        mongodb_admin_secretname = get_mongoce_admin_secretname(mongodb_cr)
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


