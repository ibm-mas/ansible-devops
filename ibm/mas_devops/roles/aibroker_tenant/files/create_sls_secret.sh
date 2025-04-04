#!/bin/bash

set -e

ROLE_PATH="${1}"
TENANT=$2
instance_id=$3

if [ -z ${TENANT} ]; then
  #echo "❌ Missing tenant name"
  #exit 1
  echo "Usage ./create_sls_secret.sh tenant-name aibroker-instance-id-from-CustomResourceDefinitions sls-url-from-sls-routes slsRegistrationKey-from-sls-api-pod-Environment path_to_the_ca_crt"
  echo "for example"
  echo "./create_sls_secret.sh aibroker-user aibdev https://sls.ibm-sls.xxx.ibm.com xxxx-xxxx-xxxx-xxx"
  exit 1
fi

cwd=$(pwd)
echo "location pwd in script create secret "

mkdir -p certs

echo "creating SLS registration, please wait....."
# instanceIdentifier=`python3 {{ role_path }}/files/alm_sample_sls_use.py $3 $4`
instanceIdentifier=$(python3 "${ROLE_PATH}/files/alm_sample_sls_use.py" $4 $5 $6)
# echo "SLS registration is created successfully."

registrationKey=$5

# echo "----------"
# echo $instanceIdentifier
# echo "----------"
# Set variables
# Need to change
NAMESPACE=mas-${instance_id}-aibroker
slsClientId="aibroker"-$instanceIdentifier
# echo $slsClientId

SECRET_NAME=${TENANT}----sls-secret
CA_FILE_PATH=$cwd/certs/aibroker-${instanceIdentifier}-ca.crt
TLS_FILE_PATH=$cwd/certs/aibroker-${instanceIdentifier}-tls.crt
KEY_FILE_PATH=$cwd/certs/aibroker-${instanceIdentifier}-tls.key

# Create the secret
oc create secret generic $SECRET_NAME -n $NAMESPACE \
  --from-file=$CA_FILE_PATH \
  --from-file=$TLS_FILE_PATH \
  --from-file=$KEY_FILE_PATH \
  --from-literal=SLS_CLIENT_ID=${slsClientId} \
  --from-literal=SLS_REGISTRATION_KEY=${registrationKey}
