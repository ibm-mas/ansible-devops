#!/usr/bin/env python3

from mas.devops.ocp import getSecret
from kubernetes.dynamic import DynamicClient
from kubernetes.dynamic.exceptions import NotFoundError

from mas.devops.ocp import getCR

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

def getDb2uInstance(dynClient: DynamicClient, db2_instance_name: str, db2_namespace: str):
    """
    Retrieve Db2uCluster CR instance
    """
    
    db2uCR = getCR(dynClient, cr_api_version="db2u.databases.ibm.com/v1", cr_kind="Db2uCluster", cr_name=db2_instance_name, namespace=db2_namespace)
    if db2uCR:
        return db2uCR.to_dict()
    else:
        # Db2uCluster CR not found, try Db2uInstance
        db2uCR = getCR(dynClient, cr_api_version="db2u.databases.ibm.com/v1", cr_kind="Db2uInstance", cr_name=db2_instance_name, namespace=db2_namespace)
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