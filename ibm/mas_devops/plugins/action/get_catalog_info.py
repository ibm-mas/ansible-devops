#!/usr/bin/env python3

from ansible.plugins.action import ActionBase

from mas.devops.data import getCatalog

class ActionModule(ActionBase):
    """
    Usage Example
    -------------
    tasks:
      - name: "Load catalog metadata"
        ibm.mas_devops.get_catalog_info:
          mas_catalog_version: "{{ catalog_tag }}"
        register: mas_catalog_metadata
    """
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        catalogId = self._task.args['mas_catalog_version']
        catalogData = getCatalog(catalogId)

        if catalogData is None:
            return dict(
                message=f"Failed to load catalog information for {catalogId}",
                success=False,
                failed=True,
                changed=False,
                id=catalogId,
                result=None
            )

        return dict(
            message=f"Successfully loaded catalog information for {catalogId}",
            success=True,
            failed=False,
            changed=False,
            id=catalogId,
            result=catalogData
        )
