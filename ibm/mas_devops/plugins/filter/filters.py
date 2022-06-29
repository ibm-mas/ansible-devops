# -----------------------------------------------------------
# Licensed Materials - Property of IBM
# 5737-M66, 5900-AAA
# (C) Copyright IBM Corp. 2021 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication, or disclosure
# restricted by GSA ADP Schedule Contract with IBM Corp.
# -----------------------------------------------------------
import yaml
import re

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

def getAnnotations(annotations = None):
  """
  filter: getAnnotations
    annotations
    author: Padmanabhan Kosalaram <pakosal1@in.ibm.com>
    version_added: 0.1
    short_description: This method creates annotation dict
    description:
        - This method creates annotation dict from the user passed annotation
    options:
      _annotations:
        description: user passed annotation, format to be passed x=y,foo=bar,hello=world
        required: True
    notes:
      - limited error handling, will not handle unexpected data currently
  """
  annotation_dict =	{}
  if annotations:
    try:
        annotation_list = annotations.strip().split(',')
        for annotation in annotation_list:
            annotation = annotation.split("=")
            annotation_dict[ annotation[0] ] = annotation[1]
    except:
        print("Annotation block processing failed, set the annotation_dict blank")
        annotation_dict =	{}
  return annotation_dict

def addAnnotationBlock(cr_definition,annotation_block = None):
  """
  filter: addAnnotationBlock
    cr_definition
    annotation_block
    author: Padmanabhan Kosalaram <pakosal1@in.ibm.com>
    version_added: 0.1
    short_description: Appened annotation block  to CR definition
    description:
        - This method Appened annotation block  to CR definition
    options:
      _cr_definition:
        description: CR definition
        required: True
      _annotation_block:
        description: annotation block to add to the CR User
        required: True
    notes:
      - limited error handling, will not handle unexpected data currently
  """
  print('#--------------------')
  print('cr_definition before adding annotation ::: \n' +cr_definition)

  if annotation_block:
    print('#--------------------')
    print('annotation_block ::: \n' +annotation_block)

    try:
        cr_definition = re.sub('(metadata:)', annotation_block, cr_definition, 1)
    except:
        print("Annotation block replace failed. cr_definition not updated with annotation block")

    print('#--------------------')
    print('cr_definition after adding annotation ::: \n' + cr_definition)

  return cr_definition

def getResourceNames(resourceList):
  """
    filter: getResourceNames
    author: David Parker <parkerda@uk.ibm.com>
    version_added: 10.0
    short_description: Return a list of resource names
    description:
        - This filter returns a list of resource names
    options:
      _resourceList:
        description: list of resources
        required: True
    notes:
      - limited error handling, will not handle unexpected data currently
  """
  resourceNames = []
  for resource in resourceList["resources"]:
    resourceNames.append(resource['metadata']['name'])
  return resourceNames

def defaultStorageClass(storageClassLookup, storageClassOptions):
  """
    filter: defaultStorageClass
    author: David Parker <parkerda@uk.ibm.com>
    version_added: 10.0
    short_description: Return a dict of known storage classes
    description:
        - This filter returns the name of an available storage class from the list of options provided
    options:
      _storageClassLookup:
        description: list of storageclass resources
        required: True
      _storageClassOptions:
        description: list of storageclasses that are supported, the first one found in the results will be used
        required: True
    notes:
      - limited error handling, will not handle unexpected data currently
  """
  for classOptionName in storageClassOptions:
    for storageClass in storageClassLookup["resources"]:
      if storageClass['metadata']['name'] == classOptionName:
        return classOptionName
  # We couldn't find a suitable storage class
  return ""

def getWSLProjectId(wslProjectLookup, wslProjectName):
  """
    filter: getWSLProjectId
    author: Alexandre Quinteiro <alefq@br.ibm.com>
    version_added: 11.0
    short_description: ---
    description:
        - This filter the id of the analytics project that has a name equals to wslProjectName
    options:
      _wslProjectLookup:
        description: list of analytics project objects
        required: True
      _wslProjectName:
        description: name of analytics project we are looking for
        required: True
    notes:
      - limited error handling, will not handle unexpected data currently
  """
  for wslProject in wslProjectLookup:
    if wslProject['entity']['name'] == wslProjectName:
      return wslProject['metadata']['guid']
  # Project not found
  return ""

class FilterModule(object):
  def filters(self):
    return {
      'private_vlan': private_vlan,
      'public_vlan': public_vlan,
      'appws_components': appws_components,
      'addAnnotationBlock': addAnnotationBlock,
      'getAnnotations': getAnnotations,
      'getResourceNames': getResourceNames,
      'defaultStorageClass': defaultStorageClass,
      'getWSLProjectId': getWSLProjectId,
    }
