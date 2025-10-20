#!/usr/bin/env python3

import argparse
import requests
import os
import sys
import urllib3
from time import sleep

parser = argparse.ArgumentParser()
parser.add_argument("--site", required=True)
parser.add_argument("--name", required=True)

args, unknown = parser.parse_known_args()

FYRE_USERNAME = os.getenv("FYRE_USERNAME", None)
FYRE_APIKEY = os.getenv("FYRE_APIKEY", None)

assert FYRE_USERNAME is not None
assert FYRE_APIKEY is not None

urllib3.disable_warnings()

def checkStatus(retryCount: int=0, errorCount: int=0) -> bool:
    if retryCount >= 60:
        print(" - Reached retry limit (60)")
        return False
    elif errorCount >= 5:
        print(" - Reached error limit (5)")
        return False

    headers = {
        "content-type": "application/json"
    }
    auth = (FYRE_USERNAME, FYRE_APIKEY)
    url = f"https://ocpapi.svl.ibm.com/v1/ocp/{ args.name }/status?site={ args.site }"
    response = requests.get(url=url, headers=headers, auth=auth, verify=False)

    # Example values for "details" field:
    # -------------------------------------------------------------------------
    # 400: user iotf NOT authorized to get cluster status for cluster id 932429
    # 400: Cluster/environment longhorn1 does not exist
    # 423: user parkerda (id 22020) blocked at 2025-10-20 05:50:30 until 2025-10-20 09:50:30 due to too many requests that resulted in an error

    if response.status_code == 400:
        clusterDetails = response.json().get("details", None)
        if "does not exist" in clusterDetails:
            print(" - Cluster does not exist")
            sleep(120)
            checkStatus(errorCount+1, errorCount+1)
        else:
            print(f" - Fatal error: {clusterDetails}")
            return False
    if response.status_code == 423:
            print(f" - Fatal error: {clusterDetails}")
            return False
    elif response.status_code == 200:
        clusterStatus = response.json().get("deployed_status", "unknown")
        if clusterStatus == "deployed":
            print(" - Cluster is deployed")
            return True
        else:
            print(f" - Cluster is in status '{clusterStatus}' - waiting 2m before checking again")
        sleep(120)
        checkStatus(retryCount+1, errorCount)
    else:
        print(f" - Unexpected return code ({response.status_code}): {response.json()}")
        return False

print(f"Waiting for cluster '{args.name}' to be provisioned")
ready = checkStatus()

if ready:
    print(f"Cluster '{args.name}' was successfully provisioned")
    sys.exit(0)
else:
    print(f"Cluster '{args.name}' was NOT successfully provisioned")
    sys.exit(1)
