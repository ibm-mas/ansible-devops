#!/usr/bin/env python3

import os
import yaml
from mas.devops.ocp import getSecret
from kubernetes.dynamic import DynamicClient
from kubernetes.dynamic.exceptions import NotFoundError

from mas.devops.ocp import getCR, getSecret


def createBackupDirectories(paths: list) -> bool:
    """
    Create backup directories if they do not exist
    """
    try:
        for path in paths:
            os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        return False

def copyContentsToYamlFile(file_path: str, content: dict) -> bool:
    """
    Write dictionary content to a YAML file
    """
    try:
        with open(file_path, 'w') as yaml_file:
            yaml.dump(content, yaml_file, default_flow_style=False)
        return True
    except Exception as e:
        return False

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

def backupSecret(dynClient: DynamicClient, namespace: str, secret_name: str, backup_path: str) -> bool:
    """
    Backup a Secret to a YAML file
    """
    secret = getSecret(dynClient, namespace, secret_name)
    if secret:
        secret_file_path = f"{backup_path}/{secret_name}.yaml"
        filtered_secret = filterResourceData(secret)
        if copyContentsToYamlFile(secret_file_path, filtered_secret):
            return True
        else:
            return False
    else:
        return False

def getSubscription(dynClient: DynamicClient, namespace: str, package_name: str):
    """
    Retrieve Subscription resource by package name in the specified namespace
    """
    try:
        subscription_resource = dynClient.resources.get(api_version="operators.coreos.com/v1alpha1", kind="Subscription")
        subscription = subscription_resource.get(namespace=namespace, name=package_name)
        return subscription.to_dict()
    except NotFoundError:
        return None
    except Exception as e:
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
        return None

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

def isDb2uReady(db2uCR: dict) -> bool:
    """
    Check if Db2uCluster/Db2uInstance is in ready state
    """
    if 'status' in db2uCR:
        status = db2uCR['status']
        if 'state' in status and status['state'] == 'Ready':
            return True
    return False