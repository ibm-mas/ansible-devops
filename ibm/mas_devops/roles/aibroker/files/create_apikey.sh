#!/bin/bash

######
#
#  Assume python3 is installed
#
#######

echo "Usage ./create_apikey.sh tenant_name_in_lower_case"
TENANT=$1
AIBROKER=$2

echo "TENANT = ${TENANT}"

if [ -z ${TENANT} ]; then
    echo "using default tenant name=aibrokeruser"
    TENANT='aibrokeruser'
    #echo "Usage ./create_apikey.sh tenant_name_in_lower_case"
    #exit 1
fi

aibrokerapikey=$(python3 ../roles/aibroker/files/generate_api_key.py)
echo "aibrokerapikey=$aibrokerapikey"

echo "Creating apikey secret"
oc create secret generic ${TENANT}----apikey-secret -n ${AIBROKER} \
    --from-literal=AIBROKER_APIKEY=${aibrokerapikey}
