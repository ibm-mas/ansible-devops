#!/bin/bash

if [ -e "/workspace/additional-configs" ]; then
  cp /workspace/additional-configs/* /workspace/configs/
fi

if [ -e "/workspace/entitlement/entitlement.lic" ]; then
  cp /workspace/entitlement/entitlement.lic /workspace/configs/entitlement.lic
fi

source /opt/app-root/src/env.sh

#-Temporary (Test Only)
echo "ibmcloud cli - installing container-service plugin"
ibmcloud plugin install container-service
echo "ibmcloud cli - list plugins"
ibmcloud plugin list
echo "ibmcloud cli - login"
echo ${IBMCLOUD_APIKEY}
ibmcloud login --apikey ${IBMCLOUD_APIKEY} --no-region --quiet
echo "ibmcloud cli - end"
#----------------------

ansible-playbook "$@"
rc=$?
python3 /opt/app-root/src/save-junit-to-mongo.py
exit $rc
