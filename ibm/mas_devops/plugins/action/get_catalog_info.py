#!/usr/bin/env python3

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError

from mas.devops.data import getCatalog

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        # Initialize DynamicClient and grab the task args
        catalogId = self._task.args['mas_catalog_version']
        catalogData = getCatalog(catalogId)

        if catalogData is None:
            return dict(
                message=f"Failed to load catalog information for {catalogId}",
                failed=True,
                changed=False,
                id=catalogId,
                result=None
            )

        return dict(
            message=f"Successfully loaded catalog information for {catalogId}",
            failed=False,
            changed=False,
            id=catalogId,
            result=catalogData
        )
