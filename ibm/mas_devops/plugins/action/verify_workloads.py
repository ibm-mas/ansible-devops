#!/usr/bin/env python3

from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.utils.display import Display

import time

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        # Initialize DynamicClient and grab the task args
        host = self._task.args.get('host', None)
        api_key = self._task.args.get('api_key', None)

        dynClient = get_api_client(api_key=api_key, host=host)
        retries = self._task.args['retries']
        delay = self._task.args['delay']

        deployments = dynClient.resources.get(api_version="v1", kind='Deployment')
        sts = dynClient.resources.get(api_version="v1", kind='StatefulSet')

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

        # We will ignore any issues with these deployments/statefulsets when assessing the health of the cluster
        # Consider carefully the impact of adding anything here - only add things that are utterly broken
        # AND out of our control to fix!
        ignoredResources = [
          # [NOTREADY] ibm-cpd/wd-discovery-ranker-rest = 1 replicas/None ready/1 updated/None available
          # [NOTREADY] ibm-cpd/ax-wdp-notebooks-api-deploy = 1 replicas/None ready/1 updated/None available
          "wd-discovery-ranker-rest",
          "ax-wdp-notebooks-api-deploy"
        ]

        allResourcesHealthy = False
        attempts = 0
        while attempts < retries and not allResourcesHealthy:
          resources = resourceAPI.get()
          attempts += 1
          allResourcesHealthyThisLoop = True
          ready = []
          notReady = []
          notReadyResources = []
          disabled = []
          ignored = []
          display.v(f"Checking {resourceName} are healthy ({attempts}/{retries} retries with a {delay} second delay)")

          for resource in resources.items:
            if resource.metadata.name in ignoredResources:
              msg = f"{resource.metadata.namespace}/{resource.metadata.name} = {resource.status.replicas} replicas/{resource.status.availableReplicas} available"
              display.v(f"[IGNORED] {msg}")
              ignored.append(msg)
            elif resource.status.replicas == 0:
              msg = f"{resource.metadata.namespace}/{resource.metadata.name} = {resource.status.replicas} replicas/{resource.status.availableReplicas} available"
              display.v(f"[DISABLED] {msg}")
              disabled.append(msg)
            else:
              msg = f"{resource.metadata.namespace}/{resource.metadata.name} = {resource.status.replicas} replicas/{resource.status.readyReplicas} ready/{resource.status.updatedReplicas} updated/{resource.status.availableReplicas} available"
              if resource.status.replicas != resource.status.readyReplicas or resource.status.replicas != resource.status.updatedReplicas or resource.status.replicas != resource.status.availableReplicas:
                display.v(f"[NOTREADY] {msg}")
                notReady.append(msg)
                notReadyResources.append(f"{resource.metadata.namespace}/{resource.metadata.name}")
                allResourcesHealthyThisLoop = False
              else:
                display.vvv(f"[READY]   {msg}")
                ready.append(msg)

          display.vvv(f"Finished check: allResourcesHealthyThisLoop={allResourcesHealthyThisLoop} delay: {delay}")
          if allResourcesHealthyThisLoop:
            display.v(f"Finished check: All workloads are healthy")
            allResourcesHealthy = True
          else:
            display.v(f"Finished check: Delaying {delay} seconds before next check")
            time.sleep(delay)

        if allResourcesHealthy:
          display.v(f"Success: allResourcesHealthy={allResourcesHealthy}")
          return dict(
            message=f"All {resourceName} are healthy",
            failed=False,
            changed=False,
            resources=dict(
              ready=ready,
              notReady=notReady,
              disabled=disabled,
              ignored=ignored
            )
          )
        else:
          display.v(f"Failure: allResourcesHealthy={allResourcesHealthy}")

          notReadyMsg = ', '.join(notReadyResources)
          raise AnsibleError(f"Error: These {resourceName} are not healthy: {notReadyMsg}")
