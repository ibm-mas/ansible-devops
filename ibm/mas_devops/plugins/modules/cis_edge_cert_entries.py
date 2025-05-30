# coding: utf-8 -*-
# # (C) Copyright IBM Corp. 2025 All Rights Reserved.
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

import requests
from requests.exceptions import HTTPError
from ansible.module_utils.basic import AnsibleModule

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
        mas_instance_id = dict(
            type = "str",
            required = True,
        ),
        dns_zone = dict(
            type = "str",
        ),
    )
    module = AnsibleModule(
        argument_spec=fields,
        supports_check_mode = True,
    )

    if any(v == "" for v in [module.params['edge_cert_entries'], module.params['cis_crn'], module.params['ibmcloud_apikey'], module.params['mas_instance_id']]):
        module.fail_json(msg = f"Required parameters: [edge_cert_entries, cis_crn, ibmcloud_apikey, mas_instance_id] cannot be empty")

    crn = module.params['cis_crn']
    ibmCloudApiKey = module.params['ibmcloud_apikey']
    masInstanceId = module.params['mas_instance_id']
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

        url = f"https://api.cis.cloud.ibm.com/v1/{crn}/zones/{zoneId}/ssl/certificate_packs?per_page=500"

        payload={}
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Auth-User-Token': access_token
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        json_response = response.json()

        if response.status_code != 200:
            module.fail_json(msg = f"Could not get SSL Certificates using provided CRN and Zone: {response.content}")

        results = json_response['result']

        msg = ""
        existingCertHosts = []
        for certs in results:
            if certs['type'] == "advanced":
                for host in certs['hosts']:
                    if masInstanceId in host:
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