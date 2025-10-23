#!/usr/bin/env python3

from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.utils.display import Display
from kubernetes.dynamic import DynamicClient
import time
import urllib3
import logging

urllib3.disable_warnings()  # Disabling warnings will prevent InsecureRequestWarnings from dynClient
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

display = Display()
logger = logging.getLogger("wait_for_conditions")

def waitForConditionsToReady(dynClient: DynamicClient, apiVersion: str, kind: str, namespace: str, name: str, conditionsToWaitFor: str, retryLimit: int=50):
    # waitForConditionsToReady(
    #   dynClient=dynClient,
    #   apiVersion="core.mas.ibm.com/v1",
    #   kind="Suite",
    #   namespace="mas-djp-core",
    #   name="djp",
    #   conditionsToWaitFor=["a","b","c"],
    #   retryLimit=50
    # )

    conditionsReady = 0
    attempts = 0
    while conditionsReady < len(conditionsToWaitFor):
        attempts += 1
        conditionsReady = 0

        logger.info(f"Checking required conditions:")
        resourceAPI = dynClient.resources.get(api_version=apiVersion, kind=kind)
        resource = resourceAPI = resourceAPI.get(namespace=namespace, name=name)

        if hasattr(resource, "status") and hasattr(resource.status, "conditions"):
            for condition in resource.status.conditions:
                # - lastTransitionTime: "2025-10-22T02:54:18Z"
                #   message: MAS is ready to use
                #   reason: Ready
                #   status: "True"
                #   type: Ready
                if condition.type in conditionsToWaitFor:
                    logger.info(f" - {condition.type}={condition.status}: [{condition.reason}] {condition.message}")
                    if condition.status == "True":
                        conditionsReady += 1

        # Decide what to do at the end of each loop
        if conditionsReady < len(conditionsToWaitFor):
            if attempts >= retryLimit:
                logger.info(f"One or more required conditions failed to transition to 'True' after {retryLimit} checks")
                return dict(
                    message=f"{kind} '{name}' is NOT ready ({', '.join(conditionsToWaitFor)})",
                    success=False,
                    failed=True,
                    changed=False,
                    resource=resource.to_dict()
                )
            else:
                # Sleep before another attempt
                time.sleep(120)
        else:
          logger.info(f"The required conditions have all transitioned to 'True'")
          return dict(
            message=f"{kind} '{name}' is ready ({', '.join(conditionsToWaitFor)})",
            success=True,
            failed=False,
            changed=False,
            resource=resource.to_dict()
          )


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        # Initialize DynamicClient and grab the task args
        host = self._task.args.get('host', None)
        api_key = self._task.args.get('api_key', None)

        dynClient = get_api_client(api_key=api_key, host=host)

        # Get task arguments
        api_version = self._task.args.get('api_version', None)
        kind = self._task.args.get('kind', None)
        namespace = self._task.args.get('namespace', None)
        name = self._task.args.get('name', None)
        conditions = self._task.args.get('conditions', [])
        retries = self._task.args.get('retries', 50)

        if api_version is None:
            raise AnsibleError(f"Error: api_version argument was not provided")
        if kind is None:
            raise AnsibleError(f"Error: kind argument was not provided")
        if namespace is None:
            raise AnsibleError(f"Error: namespace argument was not provided")
        if name is None:
            raise AnsibleError(f"Error: name argument was not provided")

        response = waitForConditionsToReady(
          dynClient=dynClient,
          apiVersion=api_version,
          kind=kind,
          namespace=namespace,
          name=name,
          conditionsToWaitFor=conditions,
          retryLimit=retries
        )
        return response
