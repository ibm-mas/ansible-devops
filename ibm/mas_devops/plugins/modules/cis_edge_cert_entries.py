# coding: utf-8 -*-
# (C) Copyright IBM Corp. 2025 All Rights Reserved.
# Eclipse Public License 2.0 (see https://spdx.org/licenses/EPL-2.0.html)

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: cis_edge_cert_entries

short_description: Manage MAS CIS Edge Cert entries

version_added: "1.0.0"

description: Manage MAS Edge Certs using IBM Cloud Internet Services.

author:
    - Andrew Whitfield (@whitfiea)
'''

import time

import requests
from ansible.module_utils.basic import AnsibleModule


def _request_with_retry(method, url, headers, payload, max_retries=5, backoff_base=30):
    """Execute an HTTP request with exponential backoff retry on 429 responses.

    Retries up to max_retries times when a 429 rate-limit response is received.
    The wait time is the greater of backoff_base * 2^attempt and the retry_after
    value returned in the 429 response body, ensuring we always respect the
    server's requested back-off.

    Args:
        method (str): HTTP method (GET, POST, PUT, PATCH, DELETE).
        url (str): Request URL.
        headers (dict): HTTP headers.
        payload: Request body.
        max_retries (int, optional): Maximum number of attempts. Defaults to 5.
        backoff_base (int, optional): Base wait seconds for exponential backoff. Defaults to 30.

    Returns:
        requests.Response: The last response received.
    """
    for attempt in range(max_retries):
        response = requests.request(method, url, headers=headers, data=payload)
        if response.status_code != 429:
            return response
        retry_after = backoff_base * (2 ** attempt)
        try:
            retry_after = max(retry_after, response.json().get("retry_after", 0))
        except Exception:
            pass
        time.sleep(retry_after)
    return response


def main():

    fields = dict(

        edge_cert_entries = dict(
            type = "list",
            required = True,
        ),
        cis_crn = dict(
            type = "str",
            required = True,
        ),
        ibmcloud_apikey = dict(
            type = "str",
            required = True,
            no_log = True,
        ),
        instance_id = dict(
            type = "str",
            required = True,
        ),
        mas_domain = dict(
            type = "str",
            required = False,
            default = "",
        ),
        cis_subdomain = dict(
            type = "str",
            required = False,
            default = "",
        ),
        dns_zone = dict(
            type = "str",
        ),
    )
    module = AnsibleModule(
        argument_spec=fields,
        supports_check_mode = True,
    )

    if any(v == "" for v in [module.params['edge_cert_entries'], module.params['cis_crn'], module.params['ibmcloud_apikey'], module.params['instance_id']]):
        module.fail_json(msg = f"Required parameters: [edge_cert_entries, cis_crn, ibmcloud_apikey, instance_id] cannot be empty")

    crn = module.params['cis_crn']
    ibmCloudApiKey = module.params['ibmcloud_apikey']
    instanceId = module.params['instance_id']
    edgeCertEntries = module.params['edge_cert_entries']

    # User may want to select an specific zone
    dnsZone = module.params['dns_zone']

    url = "https://iam.cloud.ibm.com/oidc/token"

    payload='apikey=' + ibmCloudApiKey + '&response_type=cloud_iam&grant_type=urn%3Aibm%3Aparams%3Aoauth%3Agrant-type%3Aapikey'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)

        # If the response was successful, no Exception will be raised

        if response.status_code != 200:
            module.fail_json(msg = f"Could not get IBM Cloud Token based on the provided API: {response.content}")

        json_response = response.json()
        access_token = json_response['access_token']

        # Getting zones

        url = f"https://api.cis.cloud.ibm.com/v1/{crn}/zones"

        payload={}
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Auth-User-Token': access_token
        }

        response = _request_with_retry("GET", url, headers=headers, payload=payload)
        json_response = response.json()

        if response.status_code == 429:
            module.fail_json(msg = f"Could not get Zones using provided CRN (rate limited after retries): {response.content}")
        elif response.status_code != 200:
            module.fail_json(msg = f"Could not get Zones using provided CRN: {response.content}")

        zones = json_response['result']

        # Looking for available zones

        for zone in zones:
            if(dnsZone and dnsZone == zone['id']):
                currentZone = zone
            elif(not dnsZone):
                currentZone = zone

        zoneName = currentZone['name']
        zoneId = currentZone['id']

        if len(zones) > 1 and not dnsZone:
            module.fail_json(msg = f"More than one zone found please choose one and export DNS_ZONE_ID env var.")
        elif len(zones) == 0:
            module.fail_json(msg = f"No DNS zones found, aborting...")

        url = f"https://api.cis.cloud.ibm.com/v1/{crn}/zones/{zoneId}/ssl/certificate_packs?per_page=500"

        payload={}
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Auth-User-Token': access_token
        }

        response = _request_with_retry("GET", url, headers=headers, payload=payload)
        json_response = response.json()

        if response.status_code == 429:
            module.fail_json(msg = f"Could not get SSL Certificates using provided CRN and Zone (rate limited after retries): {response.content}")
        elif response.status_code != 200:
            module.fail_json(msg = f"Could not get SSL Certificates using provided CRN and Zone: {response.content}")

        results = json_response['result']

        msg = ""
        existingCertHosts = []

        # Primary filter: collect hosts from advanced certs that contain mas_instance_id
        for certs in results:
            if certs['type'] == "advanced":
                for host in certs['hosts']:
                    if instanceId in host:
                        existingCertHosts.append(host)

        # Fallback filter: when no hosts matched by instance ID, use cis_subdomain
        if len(existingCertHosts) == 0 and cisSubdomain:
            for certs in results:
                if certs['type'] == "advanced":
                    for host in certs['hosts']:
                        if cisSubdomain in host:
                            existingCertHosts.append(host)

        # Fallback filter: when no hosts matched by instance ID or subdomain, use mas_domain
        if len(existingCertHosts) == 0 and masDomain:
            for certs in results:
                if certs['type'] == "advanced":
                    for host in certs['hosts']:
                        if masDomain in host:
                            existingCertHosts.append(host)

        exitingCertHostsFound = len(existingCertHosts)

        entryMissing = False
        for entryName in edgeCertEntries:
            if not any(entryName == host for host in existingCertHosts):
                entryMissing = True
                msg = msg + f"{entryName} not in exisitng hosts. \n "
        
        if not entryMissing:
            msg = "All expected edge cert hosts present in existing edge certificates"

    except requests.exceptions.RequestException as e:  # This is the correct syntax
        module.fail_json(msg = f"Error {e} calling : {url}")

    result = {"changed": False, "reorder": entryMissing, "msg": msg, "exitingCertHostsFound": exitingCertHostsFound}
    module.exit_json(**result)

if __name__ == '__main__':
    main()
