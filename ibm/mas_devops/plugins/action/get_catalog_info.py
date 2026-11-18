#!/usr/bin/env python3

from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase
from mas.devops.data import NoSuchCatalogError, getCatalog


class ActionModule(ActionBase):
    """
    Usage Example
    -------------
    tasks:
      - name: "Load catalog metadata"
        ibm.mas_devops.get_catalog_info:
          mas_catalog_version: "{{ catalog_tag }}"
          fail_if_catalog_does_not_exist: true
        register: mas_catalog_metadata
    """
    def run(self, tmp=None, task_vars=None):
        super().run(tmp, task_vars)

        catalogId = self._task.args.get('mas_catalog_version', None)
        failIfCatalogDoesNotExist = self._task.args.get('fail_if_catalog_does_not_exist', False)

        if catalogId is None:
            raise AnsibleError("Error: mas_catalog_version argument was not provided")
        if not isinstance(catalogId, str):
            raise AnsibleError("Error: mas_catalog_version argument is not a string")
        if not isinstance(failIfCatalogDoesNotExist, bool):
            raise AnsibleError("Error: fail_if_catalog_does_not_exist argument is not a boolean")

        try:
            catalogData = getCatalog(catalogId)
            return dict(
                message=f"Successfully loaded catalog information for {catalogId}",
                success=True,
                failed=False,
                changed=False,
                id=catalogId,
                **catalogData
            )
        except NoSuchCatalogError:
            return dict(
                message=f"Failed to load catalog information for {catalogId}",
                success=False,
                failed=failIfCatalogDoesNotExist,
                changed=False,
                id=catalogId
            )

