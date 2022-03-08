#!/bin/bash
set -e

# This script will initiate the provisioning process of MAS. It will perform following steps,

## Variables
export AWS_DEFAULT_REGION=$DEPLOY_REGION
MASTER_INSTANCE_TYPE="m5.2xlarge"
WORKER_INSTANCE_TYPE="m5.4xlarge"
# Mongo variables
export MONGODB_STORAGE_CLASS=gp2
# Amqstreams variables
export KAFKA_STORAGE_CLASS=gp2
# IAM variables
IAM_POLICY_NAME="masocp-policy-${RANDOM_STR}"
IAM_USER_NAME="masocp-user-${RANDOM_STR}"
# SLS variables 
export SLS_STORAGE_CLASS=gp2
# BAS variables 
export BAS_META_STORAGE=gp2
# CP4D variables
export CPD_BLOCK_STORAGE_CLASS=gp2

# Retrieve SSH public key
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
SSH_PUB_KEY=$(curl -H "X-aws-ec2-metadata-token: $TOKEN" –v http://169.254.169.254/latest/meta-data/public-keys/0/openssh-key)

log "Below are Cloud specific deployment parameters,"
echo " AWS_DEFAULT_REGION: $AWS_DEFAULT_REGION"
echo " MASTER_INSTANCE_TYPE: $MASTER_INSTANCE_TYPE"
echo " WORKER_INSTANCE_TYPE: $WORKER_INSTANCE_TYPE"
echo " MONGODB_STORAGE_CLASS: $MONGODB_STORAGE_CLASS"
echo " KAFKA_STORAGE_CLASS: $KAFKA_STORAGE_CLASS"
echo " IAM_POLICY_NAME: $IAM_POLICY_NAME"
echo " IAM_USER_NAME: $IAM_USER_NAME"
echo " SLS_STORAGE_CLASS: $SLS_STORAGE_CLASS"
echo " BAS_META_STORAGE: $BAS_META_STORAGE"
echo " SSH_PUB_KEY: $SSH_PUB_KEY"

## Download files from S3 bucket
# Download MAS license
log "==== Downloading MAS license ===="
cd $GIT_REPO_HOME
if [[ ${MAS_LICENSE_URL,,} =~ ^https? ]]; then
  wget "$MAS_LICENSE_URL" -O entitlement.lic
elif [[ ${MAS_LICENSE_URL,,} =~ ^s3 ]]; then
  aws s3 cp "$MAS_LICENSE_URL" entitlement.lic
fi
if [[ -f entitlement.lic ]]; then
  chmod 600 entitlement.lic
fi
# Download SLS certificate
cd $GIT_REPO_HOME
if [[ ${SLS_PUB_CERT_URL,,} =~ ^https? ]]; then
  log "Downloading SLS certificate from HTTP URL"
  wget "$SLS_PUB_CERT_URL" -O sls.crt
elif [[ ${SLS_PUB_CERT_URL,,} =~ ^s3 ]]; then
  log "Downloading SLS certificate from S3 URL"
  aws s3 cp "$SLS_PUB_CERT_URL" sls.crt
fi
if [[ -f sls.crt ]]; then
  chmod 600 sls.crt
fi
# Download BAS certificate
cd $GIT_REPO_HOME
if [[ ${BAS_PUB_CERT_URL,,} =~ ^https? ]]; then
  log "Downloading BAS certificate from HTTP URL"
  wget "$BAS_PUB_CERT_URL" -O bas.crt
elif [[ ${BAS_PUB_CERT_URL,,} =~ ^s3 ]]; then
  log "Downloading BAS certificate from S3 URL"
  aws s3 cp "$BAS_PUB_CERT_URL" bas.crt
fi
if [[ -f bas.crt ]]; then
  chmod 600 bas.crt
fi

### Read License File & Retrive SLS hostname and host id
line=$(head -n 1 entitlement.lic)
set -- $line
hostname=$2
hostid=$3
echo " SLS_HOSTNAME: $hostname"
echo " SLS_HOST_ID: $hostid"
#SLS Instance name
export SLS_INSTANCE_NAME="$hostname"
export SLS_LICENSE_ID="$hostid"

## IAM
# Create IAM policy
cd $GIT_REPO_HOME/aws
policyarn=$(aws iam create-policy --policy-name ${IAM_POLICY_NAME} --policy-document file://${GIT_REPO_HOME}/aws/iam/policy.json | jq '.Policy.Arn' | tr -d "\"")
# Create IAM user
aws iam create-user --user-name ${IAM_USER_NAME}
aws iam attach-user-policy --user-name ${IAM_USER_NAME} --policy-arn $policyarn
accessdetails=$(aws iam create-access-key --user-name ${IAM_USER_NAME})
export AWS_ACCESS_KEY_ID=$(echo $accessdetails | jq '.AccessKey.AccessKeyId' | tr -d "\"")
export AWS_SECRET_ACCESS_KEY=$(echo $accessdetails | jq '.AccessKey.SecretAccessKey' | tr -d "\"")
echo " AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID"
# Put some delay for IAM permissions to be applied in the backend
sleep 60

if [[ $OPENSHIFT_USER_PROVIDE == "false" ]]; then
  ## Provisiong OCP cluster
  # Create tfvars file
  cd $GIT_REPO_HOME/aws/ocp-terraform
  rm -rf terraform.tfvars

  if [[ $DEPLOY_REGION == "ap-northeast-1" ]]
  then
    AVAILABILITY_ZONE_1="${DEPLOY_REGION}a"
    AVAILABILITY_ZONE_2="${DEPLOY_REGION}c"
    AVAILABILITY_ZONE_3="${DEPLOY_REGION}d"
  elif [[ $DEPLOY_REGION == "ca-central-1" ]]
  then
    AVAILABILITY_ZONE_1="${DEPLOY_REGION}a"
    AVAILABILITY_ZONE_2="${DEPLOY_REGION}b"
    AVAILABILITY_ZONE_3="${DEPLOY_REGION}d"
  else
    AVAILABILITY_ZONE_1="${DEPLOY_REGION}a"
    AVAILABILITY_ZONE_2="${DEPLOY_REGION}b"
    AVAILABILITY_ZONE_3="${DEPLOY_REGION}c"
  fi

  cat <<EOT >> terraform.tfvars
cluster_name                    = "$CLUSTER_NAME"
region                          = "$DEPLOY_REGION"
az                              = "$AZ_MODE"
availability_zone1              = "${AVAILABILITY_ZONE_1}"
availability_zone2              = "${AVAILABILITY_ZONE_2}"
availability_zone3              = "${AVAILABILITY_ZONE_3}"
access_key_id                   = "$AWS_ACCESS_KEY_ID"
secret_access_key               = "$AWS_SECRET_ACCESS_KEY"
base_domain                     = "$BASE_DOMAIN"
openshift_pull_secret_file_path = "$OPENSHIFT_PULL_SECRET_FILE_PATH"
public_ssh_key                  = "$SSH_PUB_KEY"
openshift_username              = "$OPENSHIFT_USER"
openshift_password              = "$OPENSHIFT_PASSWORD"
cpd_api_key                     = "$CPD_API_KEY"
master_instance_type            = "$MASTER_INSTANCE_TYPE"
worker_instance_type            = "$WORKER_INSTANCE_TYPE"
master_replica_count            = "$MASTER_NODE_COUNT"
worker_replica_count            = "$WORKER_NODE_COUNT"
accept_cpd_license              = "accept"
EOT
  log "==== OCP cluster creation started ===="
  # Deploy OCP cluster
  sed -i "s/<REGION>/$DEPLOY_REGION/g" variables.tf
  terraform init -input=false
  terraform plan -input=false -out=tfplan
  set +e
  terraform apply -input=false -auto-approve
  retcode=$?
  if [[ $retcode -ne 0 ]]; then
    log "OCP cluster creation failed in Terraform step"
    exit 21
  fi
  set -e
  log "==== OCP cluster creation completed ===="

## Add ER Key to global pull secret
  cd /tmp
  oc extract secret/pull-secret -n openshift-config --keys=.dockerconfigjson --to=. --confirm
  export encodedEntitlementKey=$(echo cp:$SLS_ENTITLEMENT_KEY | tr -d '\n' | base64 -w0)
  ##export encodedEntitlementKey=$(echo cp:$SLS_ENTITLEMENT_KEY | base64 -w0)
  export emailAddress=$(cat .dockerconfigjson | jq -r '.auths["cloud.openshift.com"].email')
  jq '.auths |= . + {"cp.icr.io": { "auth" : "$encodedEntitlementKey", "email" : "$emailAddress"}}' .dockerconfigjson > /tmp/dockerconfig.json
  envsubst < /tmp/dockerconfig.json > /tmp/.dockerconfigjson
  oc set data secret/pull-secret -n openshift-config --from-file=/tmp/.dockerconfigjson

  ## Create bastion host
  cd $GIT_REPO_HOME/aws
  set +e
  ./create-bastion-host.sh
  retcode=$?
  if [[ $retcode -ne 0 ]]; then
    log "Bastion host creation failed in Terraform step"
    exit 22
  fi
  set -e
 
  # Backup Terraform configuration
  BACKUP_FILE_NAME=terraform-backup-${CLUSTER_NAME}.zip
  cd $GIT_REPO_HOME
  rm -rf /tmp/mas-multicloud
  mkdir /tmp/mas-multicloud
  cp -r * /tmp/mas-multicloud
  cd /tmp
  zip -r $BACKUP_FILE_NAME mas-multicloud/*
  set +e
  aws s3 cp $BACKUP_FILE_NAME $OCP_TERRAFORM_CONFIG_UPLOAD_S3_PATH
  retcode=$?
  if [[ $retcode -ne 0 ]]; then
    log "Failed while uploading deployment context to S3"
    exit 23
  fi
  set -e
  log "OCP cluster Terraform configuration backed up at $OCP_TERRAFORM_CONFIG_UPLOAD_S3_PATH in file $CLUSTER_NAME.zip"
else
  log "==== Existing OCP cluster provided, skipping the cluster creation, Bastion host creation and S3 upload of deployment context ===="
fi

## Configure OCP cluster
log "==== OCP cluster configuration (Cert Manager and SBO) started ===="
cd $GIT_REPO_HOME/ansible/playbooks
set +e
ansible-playbook configure-ocp.yml 
if [[ $? -ne 0 ]]; then
  # One reason for this failure is catalog sources not having required state information, so recreate the catalog-operator pod
  # https://bugzilla.redhat.com/show_bug.cgi?id=1807128
  echo "Deleting catalog-operator pod"
  podname=$(oc get pods -n openshift-operator-lifecycle-manager | grep catalog-operator | awk {'print $1'})
  oc logs $podname -n openshift-operator-lifecycle-manager
  oc delete pod $podname -n openshift-operator-lifecycle-manager
  sleep 10
  # Retry the step
  ansible-playbook configure-ocp.yml
  retcode=$?
  if [[ $retcode -ne 0 ]]; then
    log "Failed while configuring OCP cluster"
    exit 24
  fi
fi
set -e
log "==== OCP cluster configuration (Cert Manager and SBO) completed ===="

## Deploy MongoDB
log "==== MongoDB deployment started ===="
ansible-playbook install-mongodb.yml 
log "==== MongoDB deployment completed ===="

## Copying the entitlement.lic to MAS_CONFIG_DIR
cp $GIT_REPO_HOME/entitlement.lic $MAS_CONFIG_DIR

## Deploy Amqstreams
# log "==== Amq streams deployment started ===="
# ansible-playbook install-amqstream.yml  
# log "==== Amq streams deployment completed ===="

# SLS Deployment
if [[ (-z $SLS_ENDPOINT_URL) || (-z $SLS_REGISTRATION_KEY) || (-z $SLS_PUB_CERT_URL) ]]
then
    log "=== Deploying SLS Deployment ==="
    ## Deploy SLS
    log "==== SLS deployment started ===="
    ansible-playbook install-sls.yml
    log "==== SLS deployment completed ===="

else
    log "=== Using Existing SLS Deployment ==="
    ansible-playbook cfg-sls.yml
    log "=== Generated SLS Config YAML ==="
fi

#BAS Deployment
if [[ (-z $BAS_API_KEY) || (-z $BAS_ENDPOINT_URL) || (-z $BAS_PUB_CERT_URL) ]]
then
    log "=== Deploying BAS Deployment ==="
    ## Deploy BAS
    log "==== BAS deployment started ===="
    ansible-playbook install-bas.yml
    log "==== BAS deployment completed ===="

else
    log "=== Using Existing BAS Deployment ==="
    ansible-playbook cfg-bas.yml
    log "=== Generated BAS Config YAML ==="
fi

# Deploy CP4D
if [[ $DEPLOY_CP4D == "true" ]]; then
  log "==== CP4D deployment started ===="
  ansible-playbook install-cp4d.yml
  log "==== CP4D deployment completed ===="
fi

## Deploy MAS
log "==== MAS deployment started ===="
ansible-playbook install-suite.yml
log "==== MAS deployment completed ===="

## Deploy Manage
if [[ $DEPLOY_MANAGE == "true" ]]; then
  # Deploy Manage
  log "==== MAS Manage deployment started ===="
  ansible-playbook install-app.yml
  log "==== MAS Manage deployment completed ===="
  if [[ (-z $MAS_JDBC_USER) || (-z $MAS_JDBC_PASSWORD) || (-z $MAS_JDBC_URL) || (-z $MAS_JDBC_CERT_URL) ]]; then
    log "Skipping the Manage app JDBC configuration"
  else
    # Configure suite DB
    log "==== MAS Manage configure suite DB started ===="
    ansible-playbook configure-suite-db.yml -vv
    log "==== MAS Manage configure suite DB completed ===="
    # Configure app to use the DB
    log "==== MAS Manage configure app started ===="
    ansible-playbook configure-app.yml -vv
    log "==== MAS Manage configure app completed ===="
  fi
fi
