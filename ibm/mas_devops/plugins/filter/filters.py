# -----------------------------------------------------------
# Licensed Materials - Property of IBM
# 5737-M66, 5900-AAA
# (C) Copyright IBM Corp. 2021 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication, or disclosure
# restricted by GSA ADP Schedule Contract with IBM Corp.
# -----------------------------------------------------------
import yaml

def private_vlan(vlans):
  """
    filter: private_vlan
    author: Caio Pereira <caiofcp@br.ibm.com>
    version_added: 0.1
    short_description: Provides private vlan id
    description:
        - This lookup returns a private vlan id to be used to create roks cluster
    options:
      _terms:
        description: list of Vlans
        required: True
    notes:
      - limited error handling, will not handle unexpected data currently
  """
  private_vlan = None
  public_vlan_router = [x['properties']['primary_router'] for x in vlans if x['type'] == 'public'][0][3:6]
  for vlan in vlans:
      if vlan['type'] == 'private' and vlan['properties']['primary_router'][3:6] == public_vlan_router:
        private_vlan = vlan['id']
  return private_vlan


def public_vlan(vlans):
  """
      filter: public_vlan
      author: Caio Pereira <caiofcp@br.ibm.com>
      version_added: 0.1
      short_description: Provides public vlan id
      description:
          - This lookup returns a public vlan id to be used to create roks cluster
      options:
        _terms:
          description: list of Vlans
          required: True
      notes:
        - limited error handling, will not handle unexpected data currently
  """
  public_vlan = [x['id'] for x in vlans if x['type'] == 'public'][0]  
  return public_vlan

def appws_components(components):
  """
      filter: appws_components
      author: Andrew Whitfield <whitfiea@uk.ibm.com>
      version_added: 0.1
      short_description: Returns components in yaml form
      description:
          - This filter takes the key=value pairs, seperated by commas, for components to be installed into an app workspace
          and returns them in yaml form.
      options:
        components:
          description: key=value pairs of components, seperated by commas, to install into an application workspace.
          required: True
  """
  if components is None or components == '' or components == '{}':
    return None
  else:
    # Take base=latest,health=latest and make {'base': {'version': 'latest'},'health': {'version': 'latest'}}
    split_components = components.strip().split(',')
    components_yaml = {}
    for component in split_components:
      split_component = component.split('=')
      components_yaml[split_component[0]] = {'version': split_component[1]}

    return components_yaml

class FilterModule(object):
  def filters(self):
    return {
      'private_vlan': private_vlan,
      'public_vlan': public_vlan,
      'appws_components': appws_components
    }
