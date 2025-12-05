#!/usr/bin/env python3

import urllib3
from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.utils.display import Display
from kubernetes.dynamic import DynamicClient
from kubernetes.dynamic.exceptions import NotFoundError

from mas.devops.ocp import getStorageClass
from mas.devops.mas import getDefaultStorageClasses


# Disabling warnings will prevent InsecureRequestWarnings from dynClient
urllib3.disable_warnings()
display = Display()

def getStorageClassFromCR(mongoCR: dict) -> str:
    """
    Get Storage Class from MongoDB Community CR
    spec.statefulSet.spec.volumeClaimTemplates[0].spec.storageClassName
    """
    if 'spec' in mongoCR:
        if 'statefulSet' in mongoCR['spec']:
            if 'spec' in mongoCR['spec']['statefulSet']:
                if 'volumeClaimTemplates' in mongoCR['spec']['statefulSet']['spec']:
                    if len(mongoCR['spec']['statefulSet']['spec']['volumeClaimTemplates']) > 0:
                        if 'spec' in mongoCR['spec']['statefulSet']['spec']['volumeClaimTemplates'][0]:
                            if 'storageClassName' in mongoCR['spec']['statefulSet']['spec']['volumeClaimTemplates'][0]['spec']:
                                return mongoCR['spec']['statefulSet']['spec']['volumeClaimTemplates'][0]['spec']['storageClassName']
    return ""

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
        mongodbCR = isMongoExist(
            dynClient=dynClient,
            mongodb_instance_name=mongodb_instance_name,
            mongodb_namespace=mongodb_namespace
        )

        if not mongodbCR:
            return dict(
                message=f"MongoDB Community instance '{mongodb_instance_name}' does NOT exist in namespace '{mongodb_namespace}'",
                success=True,
                failed=False,
                exist=False
            )
        
        # Check if storage class from existing CR exists
        # Storage class name from existing CR
        sc_name_from_cr=getStorageClassFromCR(mongodbCR)
        sc = getStorageClass(dynClient, sc_name_from_cr)

        best_sc = ""

        if sc is None:
            # check if storage class from backup CR exists
            backup_sc = getStorageClass(dynClient, backup_mongodb_storage_class)
            if backup_sc is None:
                # both storage classes do not exist, go for default storage class
                default_sc = getDefaultStorageClasses(dynClient)
                if default_sc.provider is None:
                    raise AnsibleError(f"Error: Could not find default storage class to use for existing MongoDB Community instance '{mongodb_instance_name}' in namespace '{mongodb_namespace}'")
                else:
                    best_sc = default_sc.rwo
            else:
                best_sc = backup_mongodb_storage_class
        else:
            best_sc = sc_name_from_cr


        # check if mongo is running
        if not isMongoRunning(mongodbCR):
            return dict(
                message=f"MongoDB Community instance '{mongodb_instance_name}' is NOT in 'Running' state in namespace '{mongodb_namespace}'",
                success=True,
                failed=False,
                exist=True,
                running=False,
                storage_class=best_sc,
                mongoce_version=mongoce_version
            )

        mongoce_version = mongodbCR['spec']['version']

        return dict(
            message=f"MongoDB Community instance '{mongodb_instance_name}' is running version '{mongoce_version}' in namespace '{mongodb_namespace}'",
            success=True,
            failed=False,
            exist=True,
            running=True,
            mongoce_version=mongoce_version,
            storage_class=best_sc
        )

