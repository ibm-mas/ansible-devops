#!/usr/bin/env python3

from ansible_collections.kubernetes.core.plugins.module_utils.common import get_api_client

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.utils.display import Display

import time

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        # Initialize DynamicClient and grab the task args
        dynaClient = get_api_client()
        retries = self._task.args['retries']
        delay = self._task.args['delay']

        deployments = dynaClient.resources.get(api_version="v1", kind='Deployment')
        sts = dynaClient.resources.get(api_version="v1", kind='StatefulSet')

        depResult = self._checkResources(deployments, "Deployments", retries, delay)
        stsResult = self._checkResources(sts, "StatefulSets", retries, delay)

        return dict(
          failed = (depResult["failed"] and stsResult["failed"]),
          changed = (depResult["changed"] and stsResult["changed"]),
          message = f"{depResult['message']} / {stsResult['message']}",
          deployments = depResult,
          statefulSets = stsResult
        )

    def _checkResources(self, resourceAPI, resourceName, retries, delay):
        display = Display()

        display.v(f"Checking {resourceName} are healthy ({retries} retries with a {delay} second delay)")
        resources = resourceAPI.get()

        allResourcesHealthy = False
        attempts = 0
        while attempts < retries and not allResourcesHealthy:
          attempts += 1
          allResourcesHealthyThisLoop = True
          ready = []
          notReady = []
          disabled = []

          for resource in resources.items:
            if resource.status.replicas == 0:
              display.v(f"* {resource.metadata.namespace}/{resource.metadata.name} = {resource.status.replicas}/{resource.status.availableReplicas}")
              disabled.append(f"{resource.metadata.namespace}/{resource.metadata.name} = {resource.status.replicas} replicas/{resource.status.availableReplicas} available")
            else:
              display.v(f"* {resource.metadata.namespace}/{resource.metadata.name} = {resource.status.replicas}/{resource.status.readyReplicas}/{resource.status.updatedReplicas}/{resource.status.availableReplicas}")
              if resource.status.replicas != resource.status.readyReplicas or resource.status.replicas != resource.status.updatedReplicas or resource.status.replicas != resource.status.availableReplicas:
                notReady.append(f"{resource.metadata.namespace}/{resource.metadata.name} = {resource.status.replicas} replicas/{resource.status.readyReplicas} ready/{resource.status.updatedReplicas} updated/{resource.status.availableReplicas} available")
                allResourcesHealthyThisLoop = False
              else:
                ready.append(f"{resource.metadata.namespace}/{resource.metadata.name} = {resource.status.replicas} replicas/{resource.status.readyReplicas} ready/{resource.status.updatedReplicas} updated/{resource.status.availableReplicas} available")

          display.vvv(f"Finished loop: allResourcesHealthyThisLoop={allResourcesHealthyThisLoop} delay: {delay}")
          if allResourcesHealthyThisLoop:
            allResourcesHealthy = True
          else:
            display.vvv(f"Delaying {delay} seconds before next check")
            time.sleep(delay)

        if allResourcesHealthy:
          display.vvv(f"Success: allResourcesHealthy={allResourcesHealthy}")
          return dict(
            message=f"All {resourceName} are healthy",
            failed=False,
            changed=False,
            resources=dict(
              ready=ready,
              notReady=notReady,
              disabled=disabled
            )
          )
        else:
          display.vvv(f"Failure: allResourcesHealthy={allResourcesHealthy}")
          raise AnsibleError(f"Error: One or more {resourceName} are not healthy")
