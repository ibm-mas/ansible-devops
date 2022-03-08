#!/bin/bash

# This script is used to copy the AMI to all supported regions.
# The source region will be us-east-1.

## Variables
SOURCE_IMAGE_ID=$1
DATE_STR=$(date +%Y%M%d-%H%M)
SUPPORTED_REGIONS=( us-east-2 us-west-2 ca-central-1 eu-north-1 eu-south-1 eu-west-1 eu-west-2 eu-west-3 \
                    eu-central-1 ap-northeast-1 ap-northeast-2 ap-northeast-3 ap-south-1 ap-southeast-1 \
                    ap-southeast-2 sa-east-1 )

if [[ -z $SOURCE_IMAGE_ID ]]; then
  echo "ERROR: Provide source AMI Id as input parameter"
  exit 1
fi

for region in "${SUPPORTED_REGIONS[@]}"; do
  echo "Copying image to region $region"
  aws ec2 copy-image --source-region us-east-1 --region $region --source-image-id $SOURCE_IMAGE_ID --name "masocp-bootnode-$DATE_STR" --description "masocp-bootnode-$DATE_STR"
done 

echo "Copied AMI to all supported regions"
