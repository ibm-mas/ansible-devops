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

def db2_overwrite_config(components):
  """
      filter: db2_overwrite_config
      author: André Marcelino <andrercm@br.ibm.com>
      version_added: 0.1
      short_description: Returns db2 config in yaml form
      description:
          - This filter takes the key=value pairs, seperated by semicolon, for db2 custom config to be used in db2ucluster
          and returns them in yaml form.
      options:
        components:
          description: key=value pairs of components, seperated by semicolon, to install into an application workspace.
          required: True
  """
  if components is None or components == '' or components == '{}':
    return None
  else:
    # Take INSTANCE_MEMORY=AUTOMATIC and make {'dbmConfig': {'INSTANCE_MEMORY': 'AUTOMATIC'}}
    split_components = components.strip().split(';')
    components_yaml = {}

    for component in split_components:
      split_component = component.split('=')
      components_yaml[split_component[0]] = split_component[1]

    return components_yaml

def string2dict(_string = None):
  """
  filter: string2dict
    _string
    author: Richard Acree <acree@us.ibm.com>
    version_added: 0.1
    short_description: This method creates dict from a string
    description:
      - This method creates dict from the user passed string
    options:
      _string:
        description: user passed string, format to be passed x=y,foo=bar,hello=world
        required: True
    notes:
      - limited error handling, will not handle unexpected data
  """
  _dict = {}
  if _string and _string != 'None':
    try:
      _list = _string.strip().split(',')
      for _item in _list:
        _item = _item.split("=")
        _dict[ _item[0] ] = _item[1]
    except:
      print("Failed to parse parameter: "+_string)
      _dict = {}
  return _dict

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

def setManagePVC(data, mountPath, pvcName, pvcSize, storageClassName, accessMode, volumeName = None):
  """
    filter: setManagePVC
    author: André Marcelino <andrercm@br.ibm.com>
    version_added: 13.0
    short_description: ---
    description:
        - This builds the yaml structure to set Manage persistent volume
    options:
      data:
        description: list of existing Manage Persistent Volumes
        required: True
      mountPath:
        description: Persistent Volumes mount path
        required: True
      mountPath:
        description: Persistent Volumes Claim name
        required: True
      storageClassName:
        description: Persistent Volumes Claim Storage Class name
        required: True
      volumeName:
        description: Persistent Volume name associated to the PVC
        required: True
    notes:
      - limited error handling, will not handle unexpected data currently
  """
  pvc_list = []

  persistentVolumes = {  
    "accessModes": [accessMode],
    "mountPath": mountPath,
    "pvcName": pvcName,
    "size": pvcSize,
    "storageClassName": storageClassName,
    "volumeName": volumeName
  }
  if not volumeName:
    del persistentVolumes['volumeName']
  data.append(persistentVolumes)
  for pvc in data:
    pvc_list.append(pvc)
  return pvc_list

def setManageBirtProperties(data, rptRoute, rptServerBundleName):
  sb_list = []
  rpt_bundle = {
    "bundleType": "report",
    "isDefault": False,
    "isMobileTarget": False,
    "isUserSyncTarget": False,
    "name": rptServerBundleName,
    "replica": 1,
    "routeSubDomain": rptServerBundleName
  }

  hasRpt = [True for x in data if x['bundleType'] == 'report']
  if len(hasRpt) == 0:
    data.append(rpt_bundle)
  for sb in data:
    disablequeuemanager = 0 if sb['bundleType'] == 'report' else 1
    if 'bundleLevelProperties' in sb:
      if 'mxe.report.birt.viewerurl' not in sb['bundleLevelProperties'] and 'mxe.report.birt.disablequeuemanager' not in sb['bundleLevelProperties']:
        sb['bundleLevelProperties']+=f"mxe.report.birt.viewerurl={rptRoute}  mxe.report.birt.disablequeuemanager={disablequeuemanager}"
    else:
      sb['bundleLevelProperties']=f"mxe.report.birt.viewerurl={rptRoute}  mxe.report.birt.disablequeuemanager={disablequeuemanager}"
    sb_list.append(sb)
  return sb_list


def setManageDoclinksProperties(data, doclinkPath01, bucketName, accessKey, secretAccesskey, bucketEndpoint):
  sb_list = []
  for sb in data:
    if 'bundleLevelProperties' in sb:
      if 'mxe.doclink.doctypes.topLevelPaths' not in sb['bundleLevelProperties'] and 'mxe.doclink.doctypes.defpath' not in sb['bundleLevelProperties'] and 'mxe.doclink.path01' not in sb['bundleLevelProperties'] and 'mxe.doclink.securedAttachment' not in sb['bundleLevelProperties']:
        sb['bundleLevelProperties']+=f"  mxe.doclink.doctypes.topLevelPaths=cos:doclinks  mxe.doclink.doctypes.defpath=cos:doclinks/default  mxe.doclink.path01=cos:doclinks={doclinkPath01}  mxe.doclink.securedAttachment=true  mxe.cosbucketname={bucketName}  mxe.cosaccesskey={accessKey}  mxe.cossecretkey={secretAccesskey}  mxe.cosendpointuri={bucketEndpoint}  mxe.attachmentstorage=com.ibm.tivoli.maximo.oslc.provider.COSAttachmentStorage"
    else:
      sb['bundleLevelProperties']=f"mxe.doclink.doctypes.topLevelPaths=cos:doclinks  mxe.doclink.doctypes.defpath=cos:doclinks/default  mxe.doclink.path01=cos:doclinks={doclinkPath01}  mxe.doclink.securedAttachment=true  mxe.cosbucketname={bucketName}  mxe.cosaccesskey={accessKey}  mxe.cossecretkey={secretAccesskey}  mxe.cosendpointuri={bucketEndpoint}  mxe.attachmentstorage=com.ibm.tivoli.maximo.oslc.provider.COSAttachmentStorage"
    sb_list.append(sb)
  return sb_list

def _setSystemProperties(data, meaweb_value, oslc_rest_value, webapp_value, rest_webapp_value):

  sb_list = []

  for sb in data:
    if 'bundleLevelProperties' in sb:
      if 'mxe.int.webappurl' not in sb['bundleLevelProperties'] and 'mxe.oslc.restwebappurl' not in sb['bundleLevelProperties'] and 'mxe.oslc.webappurl' not in sb['bundleLevelProperties'] and 'mxe.rest.webappurl' not in sb['bundleLevelProperties']:
        sb['bundleLevelProperties']+=f"  mxe.int.webappurl={meaweb_value}  mxe.oslc.restwebappurl={oslc_rest_value}  mxe.oslc.webappurl={webapp_value}  mxe.rest.webappurl={rest_webapp_value}"
    else:
      sb['bundleLevelProperties']=f"mxe.int.webappurl={meaweb_value}  mxe.oslc.restwebappurl={oslc_rest_value}  mxe.oslc.webappurl={webapp_value}  mxe.rest.webappurl={rest_webapp_value}"
    sb_list.append(sb)
  return sb_list


class FilterModule(object):
  def filters(self):
    return {
      'private_vlan': private_vlan,
      'public_vlan': public_vlan,
      'appws_components': appws_components,
      'addAnnotationBlock': addAnnotationBlock,
      'db2_overwrite_config': db2_overwrite_config,
      'string2dict': string2dict,
      'getAnnotations': getAnnotations,
      'getResourceNames': getResourceNames,
      'defaultStorageClass': defaultStorageClass,
      'getWSLProjectId': getWSLProjectId,
      'setManagePVC': setManagePVC,
      'setManageBirtProperties': setManageBirtProperties,
      'setManageDoclinksProperties': setManageDoclinksProperties,
      'setSystemProperties': _setSystemProperties,
    }
