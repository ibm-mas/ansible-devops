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

urllib3.disable_warnings()  # Disabling warnings will prevent InsecureRequestWarnings from dynClient
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

display = Display()

def display_information(mongoDBCommunityCR : dict):
    display.v(f"MongoCE instance name .......................... {mongoDBCommunityCR['metadata']['name']}")
    display.v(f"MongoCE namespace .............................. {mongoDBCommunityCR['metadata']['namespace']}")
    display.v(f"MongoDB Version ................................ {mongoDBCommunityCR['spec']['version']}")

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

def get_prometheus_secretname_from_mongoce(mongoDBCommunityCR : dict) -> str:
  if 'prometheus' in mongoDBCommunityCR['spec']:
    if 'passwordSecretRef' in mongoDBCommunityCR['spec']['prometheus']:
      return mongoDBCommunityCR['spec']['prometheus']['passwordSecretRef']['name']
    else:
      return None

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
    crdAPI = dynClient.resources.get(api_version=crd_api_version, kind=crd_kind)

    try:
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
    secretAPI = dynClient.resources.get(api_version="v1", kind="Secret")
    try:
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
    issuerAPI = dynClient.resources.get(api_version="cert-manager.io/v1", kind="Issuer")
    try:
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
    certificateAPI = dynClient.resources.get(api_version="cert-manager.io/v1", kind="Certificate")
    try:
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

class ActionModule(ActionBase):
    """
    Usage Example
    -------------
    tasks:
      - name: "Backup MongoDB instance resources (CR, secrets, configmaps, issuers, certificates)"
        ibm.mas_devops.backup_mongo_cr:
    """
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        # Initialize DynamicClient and grab the task args
        host = self._task.args.get('host', None)
        api_key = self._task.args.get('api_key', None)

        dynClient = get_api_client(api_key=api_key, host=host)

        mongodb_instance_name = self._task.args.get('mongodb_instance_name')
        mongodb_namespace = self._task.args.get('mongodb_namespace')
        mongodb_backup_resource_path = self._task.args.get('mongodb_backup_resource_path')

        if mongodb_instance_name is None:
            raise AnsibleError(f"Error: mongodb_instance_name argument was not provided")
        if mongodb_namespace is None:
            raise AnsibleError(f"Error: mongodb_namespace argument was not provided")
        
        display.v(f"Backing up MongoDB Community instance '{mongodb_instance_name}' in namespace '{mongodb_namespace}'")

        # 1. Backup MongoDB Community CR
        mongodb_cr = isMongoExist(dynClient, mongodb_instance_name, mongodb_namespace)
        if not mongodb_cr:
            raise AnsibleError(f"Error: MongoDB Community instance '{mongodb_instance_name}' does not exist in namespace '{mongodb_namespace}'")
        else:
            display.v(f"MongoDB Community instance '{mongodb_instance_name}' exists in namespace '{mongodb_namespace}'")

        if not isMongoRunning(mongodb_cr):
            raise AnsibleError(f"Error: MongoDB Community instance '{mongodb_instance_name}' is not in 'Running' state")
        
        is_cr_backup = backupMongoCRContents(dynClient, mongodb_cr, mongodb_backup_resource_path)
        if not is_cr_backup:
            raise AnsibleError(f"Error: Failed to back up MongoDB Community CR for instance '{mongodb_instance_name}'")
        
        display.v(f"Successfully backed up MongoDB Community CR to '{mongodb_backup_resource_path}/cr.yaml'")

        # 2. Backup MongoDB namespace Secrets defined in the MongoDB CR

        # Get all relevant User Secret names from the MongoDB CR
        user_secret_names = get_usersecrets_from_mongoce(mongodb_cr)

        # Get Prometheus and TLS Secret names from the MongoDB CR
        prometheus_secret_names = get_prometheus_secretname_from_mongoce(mongodb_cr)
        tls_secret_names = get_tlscertkey_secretname_from_mongoce(mongodb_cr)
        
        secret_names = user_secret_names + [prometheus_secret_names] + [tls_secret_names]

        display.v(f"All Secrets to backup:  '{secret_names}'")

        # Backup each Secret
        for secret_name in secret_names:
            if not backupSecret(dynClient, mongodb_namespace, secret_name, f"{mongodb_backup_resource_path}/secrets"):
                raise AnsibleError(f"Error: Failed to back up Secret '{secret_name}'")
        
        display.v(f"Successfully backed up all Secrets in namespace '{mongodb_namespace}' to '{mongodb_backup_resource_path}/secrets'")


        # 3. Backup Issuers in the MongoDB namespace
        is_issuers_backup = backupIssuersInNamespace(dynClient, mongodb_namespace, f"{mongodb_backup_resource_path}/issuers")
        if not is_issuers_backup:
            raise AnsibleError(f"Error: Failed to back up Issuers in namespace '{mongodb_namespace}'")
        display.v(f"Successfully backed up Issuers in namespace '{mongodb_namespace}' to '{mongodb_backup_resource_path}/issuers'")

        # Backup Certificates in the MongoDB namespace
        is_certificates_backup = backupCertificatesInNamespace(dynClient, mongodb_namespace, f"{mongodb_backup_resource_path}/certificates")
        if not is_certificates_backup:
            raise AnsibleError(f"Error: Failed to back up Certificates in namespace '{mongodb_namespace}'")
        display.v(f"Successfully backed up Certificates in namespace '{mongodb_namespace}' to '{mongodb_backup_resource_path}/certificates'")

        return dict(
            message=f"Successfully backed up MongoDB Community instance '{mongodb_instance_name}' resources",
            failed=False,
            changed=False,
            success=True,
            ansible_facts={
                "mongodb_version": getMongoVersion(mongodb_cr) # this fact can be used in subsequent tasks
            }
        )


