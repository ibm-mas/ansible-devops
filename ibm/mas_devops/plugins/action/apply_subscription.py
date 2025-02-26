#!/usr/bin/env python3

import logging
import urllib3
from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client
from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase

from mas.devops.olm import applySubscription, OLMException

urllib3.disable_warnings()  # Disabling warnings will prevent InsecureRequestWarnings from dynClient
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class ActionModule(ActionBase):
    """
    Usage Example
    -------------
    tasks:
      - name: "Apply Subscription"
        ibm.mas_devops.apply_subscription:
          namespace: test-namespace
          package_name: ibm-sls
          package_channel: 3.x
        register: subscription
    """
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        # Target subscription
        namespace = self._task.args.get('namespace', None)
        config = self._task.args.get('config', None)

        # From which package?
        packageName = self._task.args.get('package_name', None)
        packageChannel = self._task.args.get('package_channel', None)

        # From which catalog?
        catalogSource = self._task.args.get('catalog_source', None)
        catalogSourceNamespace = self._task.args.get('catalog_source_namespace', None)

        if namespace is None:
            raise AnsibleError(f"Error: namespace argument was not provided")
        if not isinstance(packageName, str):
            raise AnsibleError(f"Error: packageName argument is not a string")

        # Initialize DynamicClient and apply the Subscription
        host = self._task.args.get('host', None)
        api_key = self._task.args.get('api_key', None)

        dynClient = get_api_client(api_key=api_key, host=host)
        try:
            subscription = applySubscription(dynClient, namespace, packageName, packageChannel, catalogSource, catalogSourceNamespace, config)
        except OLMException as e:
            raise AnsibleError(f"Error applying subscription: {e}")

        if subscription is None:
            return dict(
                message=f"Failed to apply subscription for {packageName} in {namespace}",
                success=False,
                failed=True,
                changed=False
            )

        return dict(
            message=f"Successfully applied subscription for {packageName} in {namespace}: {subscription.metadata.name}",
            success=True,
            failed=False,
            changed=False,
            **subscription.to_dict()
        )
