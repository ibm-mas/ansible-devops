#!/usr/bin/env python3

# Helpers shared by the get_mongoce_info and get_mongomck_info action plugins

from ansible.utils.display import Display
from kubernetes.dynamic import DynamicClient
from kubernetes.dynamic.exceptions import NotFoundError

from mas.devops.ocp import getCR

display = Display()

def getMongoAdminSecretName(mongoDBCommunityCR):
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
    Check if MongoDB instance is running
    return True if running, else False
    """
    display.v(f"Checking if MongoDB instance is in 'Running' state")
    if 'status' in mongoCR:
        if 'phase' in mongoCR['status']:
            if mongoCR['status']['phase'] == 'Running':
                display.v(f"MongoDB instance is in 'Running' state")
                return True
    display.v(f"MongoDB instance is not in 'Running' state")
    return False

def getMongoCR(dynClient: DynamicClient, mongodb_instance_name: str, mongodb_namespace: str) -> dict:
    """
    Check if MongoDB instance exists
    return cr if exists, else return empty dict
    """
    display.v(f"Checking if MongoDB instance '{mongodb_instance_name}' exists in namespace '{mongodb_namespace}'")
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
    Get MongoDB version from MongoDBCommunity CR
    """
    if 'spec' in mongoCR:
        if 'version' in mongoCR['spec']:
            return mongoCR['spec']['version']
    return ""

def getMongoDBServiceName(mongoCR: dict) -> str:
    """
    Get MongoDB Service name from MongoDBCommunity CR
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
