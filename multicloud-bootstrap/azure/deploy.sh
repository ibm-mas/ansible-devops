#!/bin/bash
set -e

# This script will initiate the provisioning process of MAS. It will perform following steps,

## Variables
#export AWS_DEFAULT_REGION=$DEPLOY_REGION
#MASTER_INSTANCE_TYPE="m5.2xlarge"
#WORKER_INSTANCE_TYPE="m5.4xlarge"
# Mongo variables
export MONGODB_STORAGE_CLASS=gp2
# Amqstreams variables
export KAFKA_STORAGE_CLASS=gp2
# Service principle variables
SP_NAME="http://${CLUSTER_NAME}-sp"
#IAM_USER_NAME="masocp-user-${RANDOM_STR}"
# SLS variables 
export SLS_STORAGE_CLASS=gp2
# BAS variables 
export BAS_META_STORAGE=gp2

# Retrieve SSH public key
#TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
#SSH_PUB_KEY=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" –v http://169.254.169.254/latest/meta-data/public-keys/0/openssh-key)

log "Below are Cloud specific deployment parameters,"
#log " AWS_DEFAULT_REGION: $AWS_DEFAULT_REGION"
#log " MASTER_INSTANCE_TYPE: $MASTER_INSTANCE_TYPE"
#log " WORKER_INSTANCE_TYPE: $WORKER_INSTANCE_TYPE"
log " MONGODB_STORAGE_CLASS: $MONGODB_STORAGE_CLASS"
log " KAFKA_STORAGE_CLASS: $KAFKA_STORAGE_CLASS"
log " SP_NAME: $SP_NAME"
#log " IAM_USER_NAME: $IAM_USER_NAME"
log " SLS_STORAGE_CLASS: $SLS_STORAGE_CLASS"
log " BAS_META_STORAGE: $BAS_META_STORAGE"
log " SSH_PUB_KEY: $SSH_PUB_KEY"

## Download files from S3 bucket
# Download MAS license
log "==== Downloading MAS license ===="
cd $GIT_REPO_HOME
if [[ ! -z ${MAS_LICENSE_URL} ]]; then
  azcopy copy "${MAS_LICENSE_URL}" "entitlement.lic"
fi

# Download SLS certificate
cd $GIT_REPO_HOME
if [[ ! -z ${SLS_PUB_CERT_URL} ]]; then
  azcopy copy "${SLS_PUB_CERT_URL}" "sls.crt"
fi
# Download BAS certificate
cd $GIT_REPO_HOME
if [[ ! -z ${UDS_PUB_CERT_URL} ]]; then
  azcopy copy "${UDS_PUB_CERT_URL}" "bas.crt"
fi

### Read License File & Retrive SLS hostname and host id
line=$(head -n 1 entitlement.lic)
set -- $line
hostname=$2
hostid=$3
log " SLS_HOSTNAME: $hostname"
log " SLS_HOST_ID: $hostid"
#SLS Instance name
export SLS_INSTANCE_NAME="$hostname"
export SLS_LICENSE_ID="$hostid"

# Add unique id as a tag to the resource group
#az tag create --resource-id /subscriptions/$AZURE_SUBSC_ID/resourcegroups/$RG_NAME --tags clusterUniqueString=$RANDOM_STR
#log "Tag clusterUniqueString=$RANDOM_STR added to the resource group $RG_NAME"

# Deploy OCP cluster and bastion host
if [[ $OPENSHIFT_USER_PROVIDE == "false" ]]; then
  cd $GIT_REPO_HOME

  ## Create OCP cluster
  cd $GIT_REPO_HOME/azure
  set +e
  ./create-ocp-cluster.sh
  retcode=$?
  if [[ $retcode -ne 0 ]]; then
    log "OCP cluster creation failed in Terraform step"
    exit 21
  fi
  set -e

  # # Get the new resource group name created by the OCP installer, bastion host will be created in the same resource group
  # OCP_CLUSTER_RG_NAME=$(az group list | jq ".[] | select(.location == \"$DEPLOY_REGION\") | select(.name | contains(\"masocp-$RANDOM_STR\")).name" | tr -d '"')
  # log "New resource group created by OpenShift installer: $OCP_CLUSTER_RG_NAME"
  # export OCP_CLUSTER_RG_NAME

  # ## Create bastion host
  # cd $GIT_REPO_HOME/azure
  # set +e
  # ./create-bastion-host.sh
  # retcode=$?
  # if [[ $retcode -ne 0 ]]; then
  #   log "Bastion host creation failed in Terraform step"
  #   exit 22
  # fi
  # set -e
 
  # Backup Terraform configuration
  rm -rf /tmp/ansible-devops
  mkdir /tmp/ansible-devops
  cp -r * /tmp/ansible-devops
  cd /tmp
  zip -r $BACKUP_FILE_NAME ansible-devops/*
  rm -rf /tmp/ansible-devops
  set +e
  az storage blob upload --account-name ${STORAGE_ACNT_NAME} --container-name masocpcontainer --name ${DEPLOYMENT_CONTEXT_UPLOAD_PATH} --file ${BACKUP_FILE_NAME} --auth-mode login
  retcode=$?
  if [[ $retcode -ne 0 ]]; then
    log "Failed while uploading deployment context to blob storage3"
    exit 23
  fi
  set -e
  log "OCP cluster Terraform configuration backed up at $DEPLOYMENT_CONTEXT_UPLOAD_PATH in file $CLUSTER_NAME.zip"

else
  log "==== Existing OCP cluster provided, skipping the cluster creation, Bastion host creation and S3 upload of deployment context ===="
fi

#Run ansible playbook to create azurefiles storage class 
log "=== Creating azurefiles-standard Storage class on OCP cluster ==="
cd $GIT_REPO_HOME/azure
ansible-playbook configure-azurefiles.yml
retcode=$?
if [[ $retcode -ne 0 ]]; then
  log "Failed to create azurefiles-standard storageclass"
  exit 27
fi
