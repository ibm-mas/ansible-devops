# -----------------------------------------------------------
# Licensed Materials - Property of IBM
# 5737-M66, 5900-AAA
# (C) Copyright IBM Corp. 2020 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication, or disclosure
# restricted by GSA ADP Schedule Contract with IBM Corp.
# -----------------------------------------------------------

import yaml
import re

def addAnnotation(cr_definition,annotations = None):
  """
  filter: addAnnotation
    cr_definition
    annotation
    author: Padmanabhan Kosalaram <pakosal1@in.ibm.com>
    version_added: 0.1
    short_description: Create annotation block and appened it to CR definition
    description:
        - This method construct annotation block from passed annontation and then appened the block to CR definition
    options:
      _cr_definition:
        description: CR definition
        required: True
      _annotations:
        description: User defined annotation to add, annotation format to be passed x=y:foo=bar:mas.ibm.com/hyperscalerProvider=aws:mas.ibm.com/hyperscalerFormat=saas:mas.ibm.com/hyperscalerChannel=ibm
        required: True

    notes:
      - limited error handling, will not handle unexpected data currently
  """
  print('#--------------------')
  print('cr_definition before adding annotation ::: \n' +cr_definition)

  if annotations:
    print('#--------------------')
    print('annotations ::: \n' +annotations)
    
    annotation_block = '''metadata:
  annotations: '''

    try:
        annotation_list = annotations.split(':')
        for annotation in annotation_list:
            annotation = annotation.split("=")
            annotation_block = annotation_block + '\n    ' + annotation[0] + ': "' + annotation[1] + '"' 
      
        cr_definition = re.sub('(metadata:)', annotation_block, cr_definition, 1)
    except:
        print("Annotation block processing failed. cr_definition not updated with annotation block")

    print('#--------------------')
    print('cr_definition after adding annotation ::: \n' + cr_definition)
  
  return cr_definition

class FilterModule(object):
  def filters(self):
    return {
      'addAnnotation': addAnnotation
    }
