#!/usr/bin/env python3

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError

from mas.devops.data import getNewestCatalogTag

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        # Initialize DynamicClient and grab the task args
        arch = self._task.args['arch']
        catalogTag = getNewestCatalogTag(arch)

        if catalogTag is None:
            raise AnsibleError(f"Error: No catalogs available for {arch}")

        return dict(
            message=f"Successfully found newest catalog for {arch}",
            failed=False,
            changed=False,
            arch=arch,
            result=catalogTag
        )
