#!/bin/bash

if [ -e "/workspace/additional-configs" ]; then
  cp /workspace/additional-configs/* /workspace/configs/
fi

if [ -e "/workspace/entitlement/entitlement.lic" ]; then
  cp /workspace/entitlement/entitlement.lic /workspace/configs/entitlement.lic
fi

#-Temporary (Test Only)
ibmcloud plugin install container-service
ibmcloud plugin list
ibmcloud login --apikey $IBMCLOUD_APIKEY --no-region --quiet 
#----------------------

source /opt/app-root/src/env.sh
ansible-playbook "$@"
rc=$?
python3 /opt/app-root/src/save-junit-to-mongo.py
exit $rc
