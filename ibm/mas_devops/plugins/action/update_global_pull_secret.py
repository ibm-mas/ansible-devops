#!/usr/bin/env python3

import logging
import urllib3
from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client
from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase

from mas.devops.ocp import updateGlobalPullSecret

urllib3.disable_warnings()  # Disabling warnings will prevent InsecureRequestWarnings from dynClient
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class ActionModule(ActionBase):
    """
    Update the global pull secret in openshift-config namespace with registry credentials.
    
    Usage Example
    -------------
    tasks:
      - name: "Update Global Pull Secret"
        ibm.mas_devops.update_global_pull_secret:
          registry_url: "{{ registry_private_url }}"
          username: "{{ registry_username }}"
          password: "{{ registry_password }}"
        register: result
    """
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        registryUrl = self._task.args.get('registry_url', None)
        username = self._task.args.get('username', None)
        password = self._task.args.get('password', None)

        if registryUrl is None:
            raise AnsibleError(f"Error: registry_url argument was not provided")
        if username is None:
            raise AnsibleError(f"Error: username argument was not provided")
        if password is None:
            raise AnsibleError(f"Error: password argument was not provided")

        # Initialize DynamicClient and update the global pull secret
        host = self._task.args.get('host', None)
        api_key = self._task.args.get('api_key', None)

        dynClient = get_api_client(api_key=api_key, host=host)
        result = updateGlobalPullSecret(dynClient, registryUrl, username, password)

        return dict(
            message=f"Successfully updated global pull secret with credentials for {registryUrl}",
            success=True,
            failed=False,
            changed=result.get('changed', True),
            name=result.get('name'),
            namespace=result.get('namespace'),
            registry=result.get('registry')
        )