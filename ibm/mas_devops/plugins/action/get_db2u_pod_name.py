#!/usr/bin/env python3

import urllib3
from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.utils.display import Display
from kubernetes.dynamic import DynamicClient
from kubernetes.dynamic.exceptions import NotFoundError

from ansible_collections.ibm.mas_devops.plugins.module_utils.backuprestore import getDb2uInstance, getDb2VersionFromCR, isDb2uReady


# Disabling warnings will prevent InsecureRequestWarnings from dynClient
urllib3.disable_warnings()
display = Display()

class ActionModule(ActionBase):
    """
    Usage Example
    -------------
    tasks:
      - name: "Get Db2u pod name
        ibm.mas_devops.get_db2u_pod_name:
    """
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        # Initialize DynamicClient and grab the task args
        host = self._task.args.get('host', None)
        api_key = self._task.args.get('api_key', None)

        dynClient = get_api_client(api_key=api_key, host=host)

        db2_instance_name = self._task.args.get('db2_instance_name')
        db2_namespace = self._task.args.get('db2_namespace')
        
        if db2_instance_name is None:
            raise AnsibleError(f"Error: db2_instance_name argument was not provided")
        if db2_namespace is None:
            raise AnsibleError(f"Error: db2_namespace argument was not provided")

        # First, check if the Db2u Instance is present and healthy state.
        db2u_cr = getDb2uInstance(dynClient, db2_instance_name, db2_namespace)
        if not db2u_cr:
            raise AnsibleError(f"Error: Db2u instance '{db2_instance_name}' not found in namespace '{db2_namespace}'")
        if not isDb2uReady(db2u_cr):
            raise AnsibleError(f"Error: Db2u instance '{db2_instance_name}' is not in 'Ready' state")
        
        # Next, get the Pod name for the Db2u instance
        label_selector = f"app={db2_instance_name},type=engine"
        display.v(f"Looking up Db2u Pod in namespace '{db2_namespace}' with labels '{label_selector}'")
        try:
            podAPI = dynClient.resources.get(api_version="v1", kind="Pod")
            pods = podAPI.get(namespace=db2_namespace, label_selector=label_selector)
            if pods.items:
                pod_name = pods.items[0]["metadata"]["name"]
                display.v(f"Found Pod '{pod_name}' in namespace '{db2_namespace}' with labels '{label_selector}'")
                return dict(failed=False, success=True, pod_name=pod_name, msg="Db2u Pod found")
            else:
                display.v(f"No Pods found in namespace '{db2_namespace}' with labels '{label_selector}'")
        except NotFoundError:
            display.v(f"No Pods found in namespace '{db2_namespace}' with labels '{label_selector}'")
        return dict(failed=True, success=False, pod_name="", msg="Db2u Pod not found")

