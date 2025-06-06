#!/bin/bash

######
#
#  create DRO token in k8s secret
#
#######

echo "Usage ./create_dro_token.sh tenant_name_in_lower_case instance_id token"

NAMESPACE='aibroker'

TENANT=$1
instance_id=$2
token=$3

if [[ -z ${instance_id} ]]; then
  #echo "❌ Missing instance_id "
  #exit 1
  echo "using default namespace aibroker"
  NAMESPACE='aibroker'

else
  NAMESPACE=mas-${instance_id}-aibroker
fi

echo $NAMESPACE

echo $token

if [ -z ${TENANT} ]; then
  echo "using default tenant name=aibroker-user"
  TENANT='aibroker-user'
  #echo "Usage ./create_apikey.sh tenant_name_in_lower_case"
  #exit 1
fi

echo "Creating DRO token in k8s secret"
oc create secret generic ${TENANT}----dro-secret -n ${NAMESPACE} \
  --from-literal=DRO_TOKEN=${token}
