#!/usr/bin/env python3

import urllib3
from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.utils.display import Display
from kubernetes.dynamic import DynamicClient
from kubernetes.dynamic.exceptions import NotFoundError

from mas.devops.ocp import getStorageClass, getCR
from mas.devops.mas import getDefaultStorageClasses


# Disabling warnings will prevent InsecureRequestWarnings from dynClient
urllib3.disable_warnings()
display = Display()

def getStorageClassFromCR(mongoCR: dict) -> str:
    """
    Get Storage Class from MongoDB Community CR
    spec.statefulSet.spec.volumeClaimTemplates[0].spec.storageClassName
    """
    if mongoCR and 'spec' in mongoCR:
        if 'statefulSet' in mongoCR['spec']:
            if 'spec' in mongoCR['spec']['statefulSet']:
                if 'volumeClaimTemplates' in mongoCR['spec']['statefulSet']['spec']:
                    if len(mongoCR['spec']['statefulSet']['spec']['volumeClaimTemplates']) > 0:
                        if 'spec' in mongoCR['spec']['statefulSet']['spec']['volumeClaimTemplates'][0]:
                            if 'storageClassName' in mongoCR['spec']['statefulSet']['spec']['volumeClaimTemplates'][0]['spec']:
                                return mongoCR['spec']['statefulSet']['spec']['volumeClaimTemplates'][0]['spec']['storageClassName']
    return ""

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

def determineBestStorageClass(dynClient: DynamicClient, existing_storageclass: str, backup_storageclass: str) -> str:
    """
    Determine best storage class,
    1. Picks existing storage class if exists, if not
    2. Picks storage class from backup if exists, if not
    3. Picks default rwo storage class.
    """

    best_sc = ""
    # 1) Try existing storage class if provided
    if existing_storageclass != "":
        display.v(f"Checking existing storage class '{existing_storageclass}'")
        sc = getStorageClass(dynClient, existing_storageclass)
        if sc is not None:
            best_sc = existing_storageclass
        else:
            display.v(f"Existing storage class '{existing_storageclass}' does not exist")

    # 2) Try backup storage class if existing not usable
    if best_sc == "" and backup_storageclass != "":
        display.v(f"Checking backup storage class '{backup_storageclass}'")
        backup_sc = getStorageClass(dynClient, backup_storageclass)
        if backup_sc is not None:
            best_sc = backup_storageclass
        else:
            display.v(f"Backup storage class '{backup_storageclass}' does not exist")

    # 3) Fallback to default RWO storage class
    if best_sc == "":
        display.v("Falling back to default RWO storage class")
        default_sc = getDefaultStorageClasses(dynClient)
        if default_sc.provider is None:
            raise AnsibleError("Error: Could not find default RWO storage class to use for MongoDB Community instance")
        best_sc = default_sc.rwo

    display.v(f"Using storage class '{best_sc}' for MongoDB Community instance")
    return best_sc


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
        backup_mongodb_storage_class = self._task.args.get('backup_mongodb_storage_class', None)

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

        # Determine best storage class to use
        # skip storage class check if backup storage class is not provided
        best_sc = ""
        if backup_mongodb_storage_class is not None:
            best_sc = determineBestStorageClass(
                dynClient=dynClient,
                existing_storageclass=getStorageClassFromCR(mongodbCR) if mongodbCR else "",
                backup_storageclass=backup_mongodb_storage_class
            )

        if not mongodbCR:
            display.v(f"MongoDB Community instance '{mongodb_instance_name}' does NOT exist in namespace '{mongodb_namespace}'")
            return dict(
                message=f"MongoDB Community instance '{mongodb_instance_name}' does NOT exist in namespace '{mongodb_namespace}'",
                success=True,
                failed=False,
                exist=False,
                running=False,
                storage_class=best_sc
            )
        elif isMongoRunning(mongodbCR):
            display.v(f"MongoDB Community instance '{mongodb_instance_name}' is running version '{mongodbCR['spec']['version']}' in namespace '{mongodb_namespace}'")
            return dict(
                message=f"MongoDB Community instance '{mongodb_instance_name}' is running version '{mongodbCR['spec']['version']}' in namespace '{mongodb_namespace}'",
                success=True,
                failed=False,
                exist=True,
                running=True,
                mongoce_version=mongodbCR['spec']['version'],
                storage_class=getStorageClassFromCR(mongodbCR)
            ) 
        else:
            display.v(f"MongoDB Community instance '{mongodb_instance_name}' is NOT in 'Running' state in namespace '{mongodb_namespace}'")
            return dict(
                message=f"MongoDB Community instance '{mongodb_instance_name}' is NOT in 'Running' state in namespace '{mongodb_namespace}'",
                success=True,
                failed=False,
                exist=True,
                running=False,
                storage_class=best_sc,
                mongoce_version=mongodbCR['spec']['version']
            )
