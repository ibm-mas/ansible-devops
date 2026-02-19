#!/usr/bin/env python3

from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.utils.display import Display

import urllib3
import logging

from mas.devops.mas import waitForAppReady

urllib3.disable_warnings()  # Disabling warnings will prevent InsecureRequestWarnings from dynClient
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        display = Display()

        # Initialize DynamicClient and grab the task args
        host = self._task.args.get('host', None)
        api_key = self._task.args.get('api_key', None)

        dynClient = get_api_client(api_key=api_key, host=host)

        # Get task arguments
        instanceId = self._task.args.get('instance_id', None)
        applicationId = self._task.args.get('application_id', None)
        workspaceId = self._task.args.get('workspace_id', None)
        retries = self._task.args.get('retries', 50)
        delay = self._task.args.get('delay', 60)

        if instanceId is None:
            raise AnsibleError(f"Error: instance_id argument was not provided")
        if applicationId is None:
            raise AnsibleError(f"Error: application_id argument was not provided")

        resourceName = f"{instanceId}/{applicationId}"
        if workspaceId is not None:
            resourceName = f"{instanceId}/{applicationId}-{workspaceId}"

        isReady = waitForAppReady(
          dynClient=dynClient,
          instanceId=instanceId,
          applicationId=applicationId,
          workspaceId=workspaceId,
          retries=retries,
          delay=delay,
          debugLogFunction=display.vv,
          infoLogFunction=display.v
        )

        if isReady:
            return dict(
                message=f"Application {resourceName} is ready",
                success=True,
                failed=False,
                changed=False
            )
        else:
            return dict(
                message=f"Application {resourceName} is not ready",
                success=False,
                failed=True,
                changed=False
            )
