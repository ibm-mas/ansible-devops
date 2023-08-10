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
        core_version = self._task.args['core_version']
        retries = self._task.args['retries']
        delay = self._task.args['delay']

        display.v(f"Checking core version is matching ({retries} retries with a {delay} second delay)")
        
        masSuites = dynaClient.resources.get(api_version="core.mas.ibm.com/v1", kind='Suite')
        versionMatching = False
        version = ""
        attempts = 0
        while attempts < retries and not versionMatching:

          suites = masSuites.get()
          attempts += 1

          for suite in suites.items:
            message = f"{suite.metadata.namespace}/{suite.metadata.name} = {suite.status.versions.reconciled}"
            display.v(f"* {message}")
            if suite.metadata.name == mas_instance and suite.status.versions.reconciled == core_version:
              versionMatching = True
              break

          if not versionMatching and attempts < retries:
            display.v(f"Delaying {delay} seconds before next check")
            time.sleep(delay)

        if versionMatching:
          return dict(
            message="MAS core version is matched",
            failed=False,
            changed=False,
            version=core_version
          )
        else:
          raise AnsibleError(f"Error: MAS core version is not matched")
