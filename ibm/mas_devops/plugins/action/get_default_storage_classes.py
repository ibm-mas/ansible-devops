#!/usr/bin/env python3

import urllib3
from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client
from ansible.plugins.action import ActionBase

from mas.devops.mas import getDefaultStorageClasses


# Disabling warnings will prevent InsecureRequestWarnings from dynClient
urllib3.disable_warnings()


class ActionModule(ActionBase):
    """
    Usage Example
    -------------
    tasks:
      - name: "Lookup default storage classes"
        ibm.mas_devops.get_default_storage_classes:
        register: defaultStorageClasses
    """
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        # Initialize DynamicClient and grab the task args
        host = self._task.args.get('host', None)
        api_key = self._task.args.get('api_key', None)

        dynClient = get_api_client(api_key=api_key, host=host)
        storageClasses = getDefaultStorageClasses(dynClient)

        # We don't want to fail if we can't find any default storage classes, doing so will
        # result in roles/playbooks failing in environments where none of the default
        # storage classes are available.  We use the success=false to track when we couldn't
        # find a default storage class, which does not trigger Ansible treating the action as
        # failed.
        if storageClasses.provider is None:
            return dict(
                message=f"Failed to find any default supported storage classes",
                success=False,
                failed=False,
                changed=False,
                **vars(storageClasses)
            )

        return dict(
            message=f"Successfully found default storage classes ({storageClasses.provider})",
            success=True,
            failed=False,
            changed=False,
            **vars(storageClasses)
        )
