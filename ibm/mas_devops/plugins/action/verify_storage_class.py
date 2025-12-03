#!/usr/bin/env python3

import urllib3
from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client
from ansible.plugins.action import ActionBase

from mas.devops.ocp import getStorageClass


# Disabling warnings will prevent InsecureRequestWarnings from dynClient
urllib3.disable_warnings()


class ActionModule(ActionBase):
    """
    Usage Example
    -------------
    tasks:
      - name: "Verify if Storage class exist
        ibm.mas_devops.verify_storage_class:
    """
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        # Initialize DynamicClient and grab the task args
        host = self._task.args.get('host', None)
        api_key = self._task.args.get('api_key', None)

        dynClient = get_api_client(api_key=api_key, host=host)
        storageClass = self._task.args['storage_class']
        sc = getStorageClass(dynClient, storageClass)

        # We don't want to fail if we can't find the specific storage class, doing so will
        # result in roles/playbooks failing in environments where none of the default
        # storage classes are available.  We use the success=false to track when we couldn't
        # find a default storage class, which does not trigger Ansible treating the action as
        # failed.
        if sc is None:
            return dict(
                message=f"Failed to find {{ storageClass }} storage class in cluster",
                success=False,
                failed=False,
                name=storageClass
            )

        return dict(
            message=f"Successfully found {{ storageClass }} storage class in cluster",
            success=True,
            failed=False,
            name=storageClass
        )
