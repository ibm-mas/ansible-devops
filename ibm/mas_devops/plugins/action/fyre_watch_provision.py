#!/usr/bin/env python3

import requests
import urllib3
from time import sleep

from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display

display = Display()

def checkStatus(username: str, password: str, clusterName: str, site: str, retryCount: int=0, errorCount: int=0) -> bool:
    if retryCount >= 60:
        display.v(" - Reached retry limit (60)")
        return False
    elif errorCount >= 5:
        display.v(" - Reached error limit (5)")
        return False

    headers = {
        "content-type": "application/json"
    }
    auth = (username, password)
    url = f"https://ocpapi.svl.ibm.com/v1/ocp/{ clusterName }/status?site={ site }"
    response = requests.get(url=url, headers=headers, auth=auth, verify=False)

    # Example values for "details" field:
    # -------------------------------------------------------------------------
    # 400: user iotf NOT authorized to get cluster status for cluster id 932429
    # 400: Cluster/environment longhorn1 does not exist
    # 423: user parkerda (id 22020) blocked at 2025-10-20 05:50:30 until 2025-10-20 09:50:30 due to too many requests that resulted in an error

    if response.status_code == 400:
        clusterDetails = response.json().get("details", None)
        if "does not exist" in clusterDetails:
            display.v(" - Cluster does not exist")
            sleep(120)
            checkStatus(username, password, clusterName, site, errorCount+1, errorCount+1)
        else:
            display.v(f" - Fatal error: {clusterDetails}")
            return False
    if response.status_code == 423:
            display.v(f" - Fatal error: {clusterDetails}")
            return False
    elif response.status_code == 200:
        clusterStatus = response.json().get("deployed_status", "unknown")
        if clusterStatus == "deployed":
            display.v(" - Cluster is deployed")
            return True
        else:
            display.v(f" - Cluster is in status '{clusterStatus}' - waiting 2m before checking again")
        sleep(120)
        checkStatus(username, password, clusterName, site, retryCount+1, errorCount)
    else:
        display.v(f" - Unexpected return code ({response.status_code}): {response.json()}")
        return False


class ActionModule(ActionBase):
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

        display.v(f"Waiting for cluster '{clusterName}' to be provisioned")
        ready = checkStatus(FYRE_USERNAME, FYRE_APIKEY, clusterName, fyreSite)

        if ready:
            return dict(
                message=f"Cluster '{clusterName}' was successfully provisioned",
                success=True,
                failed=False,
                changed=False
            )
        else:
            return dict(
                message=f"Cluster '{clusterName}' was NOT successfully provisioned",
                success=False,
                failed=True,
                changed=False
            )
