#!/usr/bin/env python3

from ansible_collections.kubernetes.core.plugins.module_utils.common import get_api_client

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.utils.display import Display

import time

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)
        display = Display()

        # Initialize DynamicClient and grab the task args
        dynaClient = get_api_client()
        mas_instance = self._task.args['mas_instance_id']
        mas_app_id = self._task.args['mas_app_id']
        mas_app_version = self._task.args['mas_app_version']
        retries = self._task.args['retries']
        delay = self._task.args['delay']

        display.v(f"Checking {mas_app_id} version is matching ({retries} retries with a {delay} second delay)")

        masAppInstances = None
        if mas_app_id == "manage":
          masAppInstances = dynaClient.resources.get(api_version="apps.mas.ibm.com/v1", kind='ManageApp')

        if masAppInstances is not None:
          versionMatching = False
          version = ""
          attempts = 0

          while attempts < retries and not versionMatching:

            appInstances = masAppInstances.get()
            attempts += 1

            for appInstance in appInstances.items:
              message = f"{appInstance.metadata.namespace}/{appInstance.metadata.name} = {appInstance.status.versions.reconciled}"
              display.v(f"* {message}")
              if appInstance.metadata.name == mas_instance and appInstance.status.versions.reconciled == mas_app_version:
                versionMatching = True
                break

            if not versionMatching and attempts < retries:
              display.v(f"Delaying {delay} seconds before next check")
              time.sleep(delay)

          if versionMatching:
            return dict(
              message=f"MAS {mas_app_id} version is matched",
              failed=False,
              changed=False,
              version=mas_app_version
            )
          else:
            raise AnsibleError(f"Error: MAS {mas_app_id} version is not matched")
        else:
            raise AnsibleError(f"Error: MAS ({mas_app_id}) instance doesn't exist")
