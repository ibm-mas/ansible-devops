# coding: utf-8 -*-
# # (C) Copyright IBM Corp. 2020 All Rights Reserved.
# Eclipse Public License 2.0 (see https://spdx.org/licenses/EPL-2.0.html)

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: cis_dns_entries

short_description: Manage MAS DNS entries

version_added: "2.2.0"

description: Manage MAS DNS entries using IBM Cloud Internet Services.

author:
    - David Parker (@durera)
'''

import requests
import getpass
import os
from requests.exceptions import HTTPError
from ansible.module_utils.basic import AnsibleModule

def main():

    fields = dict(

        dns_entries = dict(
            type = "list",
            required = True,
        ),

        cis_crn = dict(
            type = "str",
            required = True,
        ),

        cis_apikey = dict(
            type = "str",
            required = True,
            no_log = True,
        ),

        ocp_ingress = dict(
            type = "str",
            required = True,
        ),

        cis_subdomain = dict(
            type = "str",
        ),

        update_dns = dict(
            type = "bool",
            default = False,
        ),

        dns_zone = dict(
            type = "str",
        ),

    )
    module = AnsibleModule(
        argument_spec=fields,
        supports_check_mode = True,
    )

    if any(v == "" for v in [module.params['dns_entries'], module.params['cis_crn'], module.params['cis_apikey'], module.params['ocp_ingress']]):
        module.fail_json(msg = f"Required parameters: [dns_entries, cis_crn, cis_apikey, ocp_ingress] cannot be empty")

    changed = False

    crn = module.params['cis_crn']
    cisApiKey = module.params['cis_apikey']
    openshiftIngress = module.params['ocp_ingress']
    domainPrefix = module.params['cis_subdomain']
    updateDNS = module.params['update_dns']

    # User may want to select an specific zone
    dnsZone = module.params['dns_zone']

    url = "https://iam.cloud.ibm.com/oidc/token"

    payload='apikey=' + cisApiKey + '&response_type=cloud_iam&grant_type=urn%3Aibm%3Aparams%3Aoauth%3Agrant-type%3Aapikey'
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

        response = requests.request("GET", url, headers=headers, data=payload)
        json_response = response.json()

        if response.status_code != 200:
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

        url = f"https://api.cis.cloud.ibm.com/v1/{crn}/zones/{zoneId}/dns_records?per_page=1000"

        payload={}
        headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Auth-User-Token': access_token
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        json_response = response.json()

        if response.status_code != 200:
            module.fail_json(msg = f"Could not get DNS entries using provided CRN and Zone: {response.content}")

        dnsRecords = json_response['result']

        existingDNSEntries = [ sub['name'] for sub in dnsRecords ]
        existingDNSIDs = [ sub['id'] for sub in dnsRecords ]

        count = 0
        dnsEntries = module.params['dns_entries']

        for line in dnsEntries:
            count += 1
            if line != "":
                if domainPrefix == "":
                    entryName = f'{line}.{zoneName}'
                else:
                    entryName = f'{line}.{domainPrefix}.{zoneName}'
            else:
                # Adding non-wildcard domain entry
                if domainPrefix == "":
                    entryName = f'{zoneName}'
                else:
                    entryName = f'{domainPrefix}.{zoneName}'

            if(entryName in existingDNSEntries):
                if(updateDNS):
                    dnsId = existingDNSIDs[existingDNSEntries.index(entryName)]
                    # Updating DNS entry
                    url = f"https://api.cis.cloud.ibm.com/v1/{crn}/zones/{zoneId}/dns_records/{dnsId}"

                    payload="{\n    \"name\": \"" + entryName + "\",\n    \"type\": \"CNAME\",\n    \"content\": \"" + openshiftIngress + "\"\n}"
                    headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-Auth-User-Token': access_token
                    }

                    response = requests.request("PUT", url, headers=headers, data=payload)
                    if(response.status_code == 200):
                        changed = True
                    #     DNS record updated successfully

            else:
                # Adding DNS entry
                url = f"https://api.cis.cloud.ibm.com/v1/{crn}/zones/{zoneId}/dns_records"

                payload="{\n    \"name\": \"" + entryName + "\",\n    \"type\": \"CNAME\",\n    \"content\": \"" + openshiftIngress + "\"\n}"
                headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'X-Auth-User-Token': access_token
                }

                response = requests.request("POST", url, headers=headers, data=payload)
                if(response.status_code == 200):
                    changed = True
                    # DNS record created successfully
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        module.fail_json(msg = f"Error calling : {url}")

    module.exit_json(
        changed = changed,
        msg = "CIS DNS Record(s) created/updated successfully"
    )

if __name__ == '__main__':
    main()