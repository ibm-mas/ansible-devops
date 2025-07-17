#!/bin/bash

######
#
#  Assume python3 is installed
#
#######

echo "Usage ./create_apikey.sh tenant_name_in_lower_case"
TENANT=$1
AISERVICE=$2

echo "TENANT = ${TENANT}"

if [ -z ${TENANT} ]; then
    echo "using default tenant name=aiserviceuser"
    TENANT='aiserviceuser'
    #echo "Usage ./create_apikey.sh tenant_name_in_lower_case"
    #exit 1
fi

aiserviceapikey=$(python3 ../roles/aiservice/files/generate_api_key.py)
echo "aiserviceapikey=$aiserviceapikey"

echo "Creating apikey secret"
oc create secret generic ${TENANT}----apikey-secret -n ${AISERVICE} \
    --from-literal=aiservice_APIKEY=${aiserviceapikey}
