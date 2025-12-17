#!/usr/bin/env python3

import os
import yaml
from mas.devops.ocp import getSecret
from kubernetes.dynamic import DynamicClient


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