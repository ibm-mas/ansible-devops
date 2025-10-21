#!/usr/bin/env python3

import requests
import urllib3

from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display

display = Display()


def checkHostname(username, password, name, site) -> bool:
    headers = {
        "content-type": "application/json"
    }
    auth = (username, password)
    url = f"https://ocpapi.svl.ibm.com/v1/check_hostname/{name}?site={site}"
    response = requests.get(url=url, headers=headers, auth=auth, verify=False)

    # Example values for "details" field:
    # -------------------------------------------------------------------------
    # 400: user iotf NOT authorized to get cluster status for cluster id 932429
    # 400: Cluster/environment longhorn1 does not exist
    # 423: user parkerda (id 22020) blocked at 2025-10-20 05:50:30 until 2025-10-20 09:50:30 due to too many requests that resulted in an error

    if response.status_code == 200:
        responseJson = response.json()
        display.v(f" - {responseJson['status']}: {responseJson['details']}")
    else:
        raise AnsibleError(f"Error: Unexpected response code from Fyre APIs: [{response.status_code}] {response.json()}")

    if responseJson['status'] == "success":
        return True
    else:
        return False


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
        super(ActionModule, self).run(tmp, task_vars)

        FYRE_USERNAME = self._task.args.get('username', None)
        FYRE_APIKEY = self._task.args.get('apikey', None)
        clusterName = self._task.args.get('cluster_name', None)
        fyreSite = self._task.args.get('fyre_site', None)

        if FYRE_USERNAME is None:
            raise AnsibleError(f"Error: fyre_username argument was not provided")
        if FYRE_APIKEY is None:
            raise AnsibleError(f"Error: fyre_password argument was not provided")
        if clusterName is None:
            raise AnsibleError(f"Error: cluster_name argument was not provided")
        if fyreSite is None:
            raise AnsibleError(f"Error: fyre_site argument was not provided")

        urllib3.disable_warnings()

        display.v(f"Checking hostname availability for '{clusterName}'")
        available = checkHostname(FYRE_USERNAME, FYRE_APIKEY, clusterName, fyreSite)

        if available:
            return dict(
                message=f"Hostname '{clusterName}' is available",
                success=True,
                failed=False,
                changed=False,
                available=True
            )
        else:
            return dict(
                message=f"Hostname '{clusterName}' is NOT available",
                success=True,
                failed=False,
                changed=False,
                available=False
            )
