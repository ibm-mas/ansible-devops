#!/bin/bash

TENANT=$1
AIBROKER=$2
STORAGE_HOST=$3
STORAGE_ACCESSKEY=$4
STORAGE_SECRETKEY=$5
STORAGE_PROVIDER=$6


if [[ "$STORAGE_PROVIDER" == "minio" ]]; then
  STORAGE_PORT=$7
  STORAGE_REGION=$8
fi

if [[ "$STORAGE_PROVIDER" == "aws" ]]; then
  STORAGE_PORT=$7
  STORAGE_REGION=$8
fi

MODEL_ID_PREFIX=$9


if [ -z ${TENANT} ]; then
  echo "using default tenant name=aibrokeruser"
  TENANT='aibrokeruser'
  #echo "Usage ./create_s3.sh tenant_name_in_lower_case"
  #exit 1
fi

# echo -n "Enter S3 access-key > "
# read accesskey
# echo "You entered: $accesskey"

# echo -n "Enter S3 secret-key > "
# read secretkey
# echo "You entered: $secretkey"

# echo -n "Enter S3 region > "
# read region
# echo "You entered: $region"

# echo -n "Enter S3 provider url(for example: https://s3.amazonaws.com ) > "
# read s3_url
# echo "You entered: $s3_url"

# echo "TENANT = ${TENANT}"
# echo "access-key =${accesskey}"
# echo "secret-key =${secretkey}"
# echo "region =${region}"

# if [ -z ${TENANT} ]; then
#   echo "❌ Missing tenant name"
#   exit 1
# fi

# if [ -z ${access-key} ]; then
#   echo "❌ Missing S3 accesskey"
#   exit 1
# fi

# if [ -z ${secret-key} ]; then
#   echo "❌ Missing S3 secretkey"
#   exit 1
# fi

# if [ -z ${s3_url} ]; then
#   echo "❌ Missing S3 provider url"
#   exit 1
# fi

# if [ -z ${region} ]; then
#   echo "❌ Missing S3 region"
#   exit 1
# fi

bucketpostfix='-training-bucket'
if [[ $STORAGE_HOST == *"amazonaws"* ]]; then
  echo 'it is Amazon AWS'
  bucketname=$(python3 ../roles/aibroker/files/create_bucket.py ${TENANT} ${STORAGE_ACCESSKEY} ${STORAGE_SECRETKEY} ${STORAGE_REGION} ${MODEL_ID_PREFIX})
else
  echo 'it is Non Amazon AWS'
  bucketname="${TENANT}${bucketpostfix}"
fi

echo "bucketname=$bucketname"

if [[ "$bucketname" == "Error"* ]]; then
  echo "The variable $bucketname starts with the word 'Error'. Can not create bucket. Please check your S3 credential."
  exit 1
else
  echo "The credentail of S3 is valid. The bucketname $bucketname is created successfully."
  # Add storage secrets
  echo "Creating S3 secret in k8s"
  echo ${STORAGE_PROVIDER}
  if [ "$STORAGE_PROVIDER" == "aws" ]; then
    # Create a Kubernetes secret with the AWS S3 credentials
    oc create secret generic ${TENANT}----s3-secret -n ${AIBROKER} \
      --from-literal=ACCESS-KEY=${STORAGE_ACCESSKEY} \
      --from-literal=SECRET-KEY=${STORAGE_SECRETKEY} \
      --from-literal=URL=${STORAGE_HOST} \
      --from-literal=REGION=${STORAGE_REGION} \
      --from-literal=BUCKET-NAME=${bucketname}
  # Check if the storage provider is Minio
  elif [ "$STORAGE_PROVIDER" == "minio" ]; then
    # Create a Kubernetes secret with the Minio credentials
    oc create secret generic ${TENANT}----s3-secret -n ${AIBROKER} \
      --from-literal=ACCESS-KEY=${STORAGE_ACCESSKEY} \
      --from-literal=SECRET-KEY=${STORAGE_SECRETKEY} \
      --from-literal=URL=http://${STORAGE_HOST}:${STORAGE_PORT} \
      --from-literal=REGION=${STORAGE_REGION} \
      --from-literal=BUCKET-NAME=${bucketname}
  else
    echo "Invalid storage provider specified."
    exit 1
  fi
fi
