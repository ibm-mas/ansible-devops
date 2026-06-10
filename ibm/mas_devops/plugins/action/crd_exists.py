#!/usr/bin/env python3

import logging
import urllib3
from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client
from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase

from mas.devops.ocp import crdExists

urllib3.disable_warnings()  # Disabling warnings will prevent InsecureRequestWarnings from dynClient
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class ActionModule(ActionBase):
    """
    Usage Example
    -------------
    tasks:
      - name: "Check CRD exists"
        ibm.mas_devops.crd_exists:
            crdName: GrafanaDashboard
        register: crd_exists
    """
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        # Target subscription
        crdName = self._task.args.get('crdName', None)

        if crdName is None:
            raise AnsibleError("Error: CRD Name argument was not provided")

        # Initialize DynamicClient and apply the Subscription
        host = self._task.args.get('host', None)
        api_key = self._task.args.get('api_key', None)

        dynClient = get_api_client(api_key=api_key, host=host)
        isCRDPresent = crdExists(dynClient, crdName)

        return dict(
            success=True,
            exists=isCRDPresent
        )
