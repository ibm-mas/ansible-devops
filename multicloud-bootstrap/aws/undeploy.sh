#!/bin/bash
set -e

# This script will initiate the undeployment process of MAS.

# Variables
SCRIPT_RELATIVE_DIR=$(dirname "${BASH_SOURCE[0]}")
cd $SCRIPT_RELATIVE_DIR
LOG_FILE_DIR=$(pwd)
RANDOM_STR=$(cat ../mas-provisioning.log | grep "RANDOM_STR:" | cut -d ':' -f 2 | tr -d ' ')
REGION=$(cat ../mas-provisioning.log | grep "DEPLOY_REGION:" | cut -d ':' -f 2 | tr -d ' ')
ACCOUNT_ID=$(cat ../mas-provisioning.log | grep "ACCOUNT_ID:" | cut -d ':' -f 2 | tr -d ' ')
ACCESS_KEY_ID=$(cat ../mas-provisioning.log | grep "AWS_ACCESS_KEY_ID:" | cut -d ':' -f 2 | tr -d ' ')
IAM_POLICY_NAME="masocp-policy-${RANDOM_STR}"
IAM_USER_NAME="masocp-user-${RANDOM_STR}"

# Log variables
log " RANDOM_STR=$RANDOM_STR"
log " REGION=$REGION"
log " IAM_POLICY_NAME=$IAM_POLICY_NAME"
log " IAM_USER_NAME=$IAM_USER_NAME"

# Bastion host deletion
log "==== Bastion host deletion started ===="
# Undeploy OCP cluster
cd $GIT_REPO_HOME/aws/ocp-bastion-host
set +e
terraform destroy -input=false -auto-approve
set -e
log "==== Bastion host deletion completed ===="

# Call cloud specific script
log "==== OCP cluster deletion started ===="
# Undeploy OCP cluster
cd $GIT_REPO_HOME/aws/ocp-terraform
# Copy the OCP pull secret to correct place
mkdir -p /root/mas-on-aws
if [[ ! -f /root/mas-on-aws/pull-secret.json ]]; then
  cp $GIT_REPO_HOME/pull-secret.json /root/mas-on-aws/
  log "Copied OCP pull secret file to right place"
fi
terraform destroy -input=false -auto-approve
log "==== OCP cluster deletion completed ===="

# Delete PrivateHostedZone if it exist
hosted_zone_id="$(aws route53 list-hosted-zones --output text --query 'HostedZones[*].[Name,Id]' --output text | grep $CLUSTER_NAME | cut -f2)"
if [[ -n $hosted_zone_id ]]
then
	aws route53 delete-hosted-zone --id $hosted_zone_id 
	log "PrivateHostedZone deleted"
else
    log "PrivateHostedZone not exist"
fi

# Delete S3 buckets
log "==== S3 buckets deletion started ===="
log "Following S3 buckets will be deleted"
aws s3api list-buckets --query 'Buckets[?contains(Name, `masocp-'"$RANDOM_STR"'`) == `true`].[Name]' --output text
log "Deleting the buckets..."
aws s3api list-buckets --query 'Buckets[?contains(Name, `masocp-'"$RANDOM_STR"'`) == `true`].[Name]' --output text | xargs -I {} aws s3 rb s3://{} --force
log "==== S3 buckets deletion completed ===="

# Delete IAM resources
#aws iam detach-user-policy --user-name ${IAM_USER_NAME} --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/${IAM_POLICY_NAME}
#aws iam delete-access-key --user-name ${IAM_USER_NAME} --access-key-id ${ACCESS_KEY_ID}
#aws iam delete-user --user-name ${IAM_USER_NAME}
#aws iam delete-policy --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/${IAM_POLICY_NAME}
#log "Deleted policy ${IAM_POLICY_NAME}, user ${IAM_USER_NAME}"
log "Please delete the IAM user ${IAM_USER_NAME} and IAM policy ${IAM_POLICY_NAME} manually"