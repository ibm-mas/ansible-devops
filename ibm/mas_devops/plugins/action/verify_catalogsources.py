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
        retries = self._task.args['retries']
        delay = self._task.args['delay']

        display.v(f"Checking CatalogSources are ready ({retries} retries with a {delay} second delay)")
        catalogSources = dynaClient.resources.get(api_version="operators.coreos.com/v1alpha1", kind='CatalogSource')

        allReady = False
        attempts = 0
        while attempts < retries and not allReady:
          catalogs = catalogSources.get()
          attempts += 1
          allReadyThisLoop = True
          ready = []
          notReady = []

          for catalogSource in catalogs.items:
            message = f"{catalogSource.metadata.namespace}/{catalogSource.metadata.name} = {catalogSource.status.connectionState.lastObservedState}"
            display.v(f"* {message}")
            if catalogSource.status.connectionState.lastObservedState != "READY":
              allReadyThisLoop = False
              notReady.append(message)
            else:
              ready.append(message)

          if allReadyThisLoop:
            allReady = True
          else:
            display.v(f"Delaying {delay} seconds before next check")
            time.sleep(delay)

        if allReady:
          return dict(
            message="All CatalogSources are ready",
            failed=False,
            changed=False,
            ready=ready,
            notReady=notReady
          )
        else:
          raise AnsibleError(f"Error: One or more CatalogSources are not ready")
