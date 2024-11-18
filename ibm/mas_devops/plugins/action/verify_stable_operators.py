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

        display.v(f"Checking Subscriptions are up to date ({retries} retries with a {delay} second delay)")
        crds = dynaClient.resources.get(kind='CustomResourceDefinition')

        allCRsStable = False
        attempts = 0
        while attempts < retries and not allCRsStable:
          crds = crds.get()
          attempts += 1
          allCRsStableThisLoop = True
          stable = []
          notStable = []

          for crd in crds.items:
            display.v(f"* {crd.metadata.name}")
            crs = dynaClient.resources.get(kind=crd["spec"]["names"]["kind"])
            for cr in crs.items:
              display.v(f"* {crd.metadata.name}/{cr.metadata.name}")
              skipped = True
              for condition in cr["status"]["conditions"]:
                  if "ansibleResult" in condition:
                      skipped = False
                      if condition["message"] == "Awaiting next reconciliation":
                          age = datetime.now() - datetime.datetime(condition["ansibleResult"]["completion"])
                          if age > timedelta(minutes=10):
                              stable.push(f"{cr.metadata.namespace}/{cr.metadata.name} = Stable")
                          else:
                              notStable.push(f"{cr.metadata.namespace}/{cr.metadata.name} = Waiting")
                              allCRsStableThisLoop = False
                      else:
                          notStable.push(f"{cr.metadata.namespace}/{cr.metadata.name} = Running")
                          allCRsStableThisLoop = False
              if skipped:
                  stable.push(f"{cr.metadata.namespace}/{cr.metadata.name} = Skipped")

          if allCRsStableThisLoop:
            allCRsStable = True
          else:
            display.v(stable)
            display.v(notStable)
            display.v(f"Delaying {delay} seconds before next check")
            time.sleep(delay)

        if allCRsStable:
          return dict(
            message="All CRs are stable",
            failed=False,
            changed=False,
            stable=stable,
            notStable=notStable
          )
        else:
          raise AnsibleError(f"Error: One or more CRs are not stable")
