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
        subscriptions = dynaClient.resources.get(api_version="operators.coreos.com/v1alpha1", kind='Subscription')

        allSubscriptionsAtLatest = False
        attempts = 0
        while attempts < retries and not allSubscriptionsAtLatest:
          subs = subscriptions.get()
          attempts += 1
          allSubscriptionsAtLatestThisLoop = True
          atLatest = []
          notAtLatest = []

          for subscription in subs.items:
            display.v(f"* {subscription.metadata.namespace}/{subscription.metadata.name} = {subscription.status.state}")
            if subscription.status.state != "AtLatestKnown":
              allSubscriptionsAtLatestThisLoop = False
              notAtLatest.append(f"{subscription.metadata.namespace}/{subscription.metadata.name} = {subscription.status.state}")
            else:
              atLatest.append(f"{subscription.metadata.namespace}/{subscription.metadata.name} = {subscription.status.state}")

          if allSubscriptionsAtLatestThisLoop:
            allSubscriptionsAtLatest = True
          else:
            display.v(f"Delaying {delay} seconds before next check")
            time.sleep(delay)

        if allSubscriptionsAtLatest:
          return dict(
            message="All Subscriptions are at the latest known operator version",
            failed=False,
            changed=False,
            atLatest=atLatest,
            notAtLatest=notAtLatest
          )
        else:
          raise AnsibleError(f"Error: One or more subscriptions did not update to the latest known operator version")
