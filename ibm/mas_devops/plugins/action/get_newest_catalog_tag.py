#!/usr/bin/env python3

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError

from mas.devops.data import getNewestCatalogTag, NoSuchCatalogError

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        # Initialize DynamicClient and grab the task args
        arch = self._task.args['arch']

        try:
            catalogTag = getNewestCatalogTag(arch)
        except NoSuchCatalogError as e:
            raise AnsibleError(f"Error: No catalogs available for {arch}") from e

        return dict(
            message=f"Successfully found newest catalog for {arch}",
            failed=False,
            changed=False,
            arch=arch,
            result=catalogTag
        )
