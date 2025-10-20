#!/usr/bin/env python3

import argparse
import requests
import os
import sys
import urllib3

parser = argparse.ArgumentParser()
parser.add_argument("--site", required=True)
parser.add_argument("--name", required=True)

args, unknown = parser.parse_known_args()

FYRE_USERNAME = os.getenv("FYRE_USERNAME", None)
FYRE_APIKEY = os.getenv("FYRE_APIKEY", None)

assert FYRE_USERNAME is not None
assert FYRE_APIKEY is not None

urllib3.disable_warnings()

def checkHostname() -> bool:
    headers = {
        "content-type": "application/json"
    }
    auth = (FYRE_USERNAME, FYRE_APIKEY)
    url = f"https://ocpapi.svl.ibm.com/v1/check_hostname/{args.name}?site={args.site}"
    response = requests.get(url=url, headers=headers, auth=auth, verify=False)

    # Example values for "details" field:
    # -------------------------------------------------------------------------
    # 400: user iotf NOT authorized to get cluster status for cluster id 932429
    # 400: Cluster/environment longhorn1 does not exist
    # 423: user parkerda (id 22020) blocked at 2025-10-20 05:50:30 until 2025-10-20 09:50:30 due to too many requests that resulted in an error

    if response.status_code == 200:
        responseJson = response.json()
        print(f" - {responseJson['status']}: {responseJson['details']}")

    if responseJson['status'] == "success":
        return True
    else:
        return False

print(f"Checking hostname availability for '{args.name}'")
available = checkHostname()

if available:
    print(f"Hostname '{args.name}' is available")
    sys.exit(0)
else:
    print(f"Hostname '{args.name}' is NOT available")
    sys.exit(1)
