#!/usr/bin/env python3

import urllib3
from ansible_collections.kubernetes.core.plugins.module_utils.common import get_api_client
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
        dynClient = get_api_client()
        storageClasses = getDefaultStorageClasses(dynClient)

        if storageClasses.provider is None:
            return dict(
                message=f"Failed to find default storage classes",
                success=False,
                failed=True,
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
