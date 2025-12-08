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

def get_tlscertkey_secretname_from_mongoce(mongoDBCommunityCR : dict) -> str:
  if 'security' in mongoDBCommunityCR['spec']:
    if 'tls' in mongoDBCommunityCR['spec']['security']:
      if 'certificateKeySecretRef' in mongoDBCommunityCR['spec']['security']['tls']:
        return mongoDBCommunityCR['spec']['security']['tls']['certificateKeySecretRef']['name']
    else:
      return None

def get_usersecrets_from_mongoce(mongoDBCommunityCR : dict) -> list:
  user_secrets = []
  for user in mongoDBCommunityCR['spec'].get('users', []):
    if 'passwordSecretRef' in user:
      user_secrets.append(user['passwordSecretRef']['name'])
    if 'scramCredentialsSecretName' in user:
      user_secrets.append(f"{user['scramCredentialsSecretName']}-scram-credentials")
  return user_secrets


def getMongoVersionFromCR(mongoCR: dict) -> str:
    """
    Get MongoDB version from MongoDB Community CR
    """
    if 'spec' in mongoCR:
        if 'version' in mongoCR['spec']:
            return mongoCR['spec']['version']
    return ""

def copyContentsToYamlFile(file_path: str, content: dict) -> bool:
    """
    Write dictionary content to a YAML file
    """
    try:
        with open(file_path, 'w') as yaml_file:
            yaml.dump(content, yaml_file, default_flow_style=False)
        return True
    except Exception as e:
        display.v(f"Error writing to YAML file {file_path}: {e}")
        return False

def filterMongoCR(crData: dict) -> dict:
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
    
    # remove replicaSetHorizons field from spec if exists
    if 'spec' in filteredCR:
        if 'replicaSetHorizons' in filteredCR['spec']:
            del filteredCR['spec']['replicaSetHorizons']

    return filteredCR

def getCR(dynClient: DynamicClient, crd_api_version: str, crd_kind: str, cr_name: str, namespace: str = None) -> dict:
    """
    Get a Custom Resource
    """
    try:
        crdAPI = dynClient.resources.get(api_version=crd_api_version, kind=crd_kind)
        if namespace:
            cr = crdAPI.get(name=cr_name, namespace=namespace)
        else:
            cr = crdAPI.get(name=cr_name)
        return cr
    except NotFoundError:
        display.v(f"CR {cr_name} of kind {crd_kind} does not exist in namespace {namespace}")

    return {}

def filterResourceData(data: dict) -> dict:
    """
    filter metadata from Resource data and create minimal dict
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
    filteredCopy = data.copy()
    if 'metadata' in filteredCopy:
        for field in metadata_fields_to_remove:
            if field in filteredCopy['metadata']:
                del filteredCopy['metadata'][field]

    if 'status' in filteredCopy:
        del filteredCopy['status']
    
    return filteredCopy

def getSecret(dynClient: DynamicClient, namespace: str, secret_name: str) -> dict:
    """
    Get a Secret
    """
    try:
        secretAPI = dynClient.resources.get(api_version="v1", kind="Secret")
        secret = secretAPI.get(name=secret_name, namespace=namespace)
        display.v(f"Secret {secret_name} exists in namespace {namespace}")
        return secret.to_dict()
    except NotFoundError:
        display.v(f"Secret {secret_name} does not exist in namespace {namespace}")
    return {}

def backupSecret(dynClient: DynamicClient, namespace: str, secret_name: str, backup_path: str) -> bool:
    """
    Backup a Secret to a YAML file
    """
    secret = getSecret(dynClient, namespace, secret_name)
    if secret:
        secret_file_path = f"{backup_path}/{secret_name}.yaml"
        filtered_secret = filterResourceData(secret)
        if copyContentsToYamlFile(secret_file_path, filtered_secret):
            display.v(f"Successfully backed up Secret '{secret_name}' to '{secret_file_path}'")
            return True
        else:
            display.v(f"Failed to back up Secret '{secret_name}' to '{secret_file_path}'")
            return False
    else:
        display.v(f"Secret '{secret_name}' not found in namespace '{namespace}', skipping backup")
        return False

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

def isMongoExist(dynClient: DynamicClient, mongodb_instance_name: str, mongodb_namespace: str) -> dict:
    """
    Check if MongoDB Community instance exists
    return cr if exists, else return empty dict
    """
    display.v(f"Checking if MongoDB Community instance '{mongodb_instance_name}' exists in namespace '{mongodb_namespace}'")
    mongodbCR = getCR(
        dynClient=dynClient,
        crd_api_version="mongodbcommunity.mongodb.com/v1",
        crd_kind="MongoDBCommunity",
        cr_name=mongodb_instance_name,
        namespace=mongodb_namespace
    )
    if mongodbCR:
        return mongodbCR.to_dict()
    else:
        return {}

def backupIssuersInNamespace(dynClient: DynamicClient, namespace: str, backup_path: str) -> bool:
    """
    Backup all Issuers in a namespace
    """
    display.v(f"Backing up Issuers in namespace '{namespace}' to '{backup_path}'")
    try:
        issuerAPI = dynClient.resources.get(api_version="cert-manager.io/v1", kind="Issuer")
        issuers = issuerAPI.get(namespace=namespace)
        
        for issuer in issuers.items:
            issuer_name = issuer["metadata"]["name"]
            issuer_file_path = f"{backup_path}/{issuer_name}.yaml"
            filtered_issuer = filterResourceData(issuer.to_dict())
            if copyContentsToYamlFile(issuer_file_path, filtered_issuer):
                display.v(f"Successfully backed up Issuer '{issuer_name}' to '{issuer_file_path}'")
            else:
                display.v(f"Failed to back up Issuer '{issuer_name}' to '{issuer_file_path}'")
                return False
        return True

    except NotFoundError:
        display.v(f"No Issuers found in namespace {namespace}")

    return False

def backupCertificatesInNamespace(dynClient: DynamicClient, namespace: str, backup_path: str) -> bool:
    """
    Backup all Certificates in a namespace
    """
    display.v(f"Backing up Certificates in namespace '{namespace}' to '{backup_path}'")
    try:
        certificateAPI = dynClient.resources.get(api_version="cert-manager.io/v1", kind="Certificate")
        certificates = certificateAPI.get(namespace=namespace)
        
        for certificate in certificates.items:
            certificate_name = certificate["metadata"]["name"]
            certificate_file_path = f"{backup_path}/{certificate_name}.yaml"
            filtered_certificate = filterResourceData(certificate.to_dict())
            if copyContentsToYamlFile(certificate_file_path, filtered_certificate):
                display.v(f"Successfully backed up Certificate '{certificate_name}' to '{certificate_file_path}'")
            else:
                display.v(f"Failed to back up Certificate '{certificate_name}' to '{certificate_file_path}'")
                return False
        return True

    except NotFoundError:
        display.v(f"No Certificates found in namespace {namespace}")

    return False

def backupMongoCRContents(dynClient: DynamicClient, cr_data: dict, backup_path: str) -> bool:
    """
    Backup MongoDB Community CR contents to a YAML file
    """
    display.v(f"Backing up MongoDB Community CR contents to '{backup_path}/cr.yaml'")
    cr_file_path = f"{backup_path}/cr.yaml"
    filtered_cr = filterMongoCR(cr_data)
    if copyContentsToYamlFile(cr_file_path, filtered_cr):
        display.v(f"Successfully backed up MongoDB Community CR to '{cr_file_path}'")
        return True
    else:
        display.v(f"Failed to back up MongoDB Community CR to '{cr_file_path}'")
        return False

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
      - name: "Retrieve and Set facts from MongoDB instance CR and resources"
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
        mongodb_cr = isMongoExist(dynClient, mongodb_instance_name, mongodb_namespace)
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

        return dict(
            message=f"Successfully set facts from MongoDB Community instance '{mongodb_instance_name}' resources",
            failed=False,
            changed=False,
            success=True,
            ansible_facts={
                "mongoce_pod_name": mongoce_pod_name, # this fact can be used in subsequent tasks
                "mongodb_admin_user": "admin",
                "mongodb_admin_password" : base64.b64decode(mongodb_admin_secret['data']['password']),
                "mongodb_service_name": mongodb_service_name,
                "mongodb_host": mongodb_host,
                "mongodb_version": getMongoVersion(mongodb_cr)
            }
        )


