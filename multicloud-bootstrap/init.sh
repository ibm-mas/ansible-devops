#!/bin/bash
#
# This is the init script that will call the individual Cloud specific script
#

## Inputs
export CLUSTER_TYPE=$1
export OFFERING_TYPE=$2
export DEPLOY_REGION=$3
export ACCOUNT_ID=$4
export CLUSTER_SIZE=$5
export RANDOM_STR=$6
export BASE_DOMAIN=$7
export BASE_DOMAIN_RG_NAME=$8
export SSH_KEY_NAME=$9
export DEPLOY_WAIT_HANDLE=${10}
export SLS_ENTITLEMENT_KEY=${11}
export OCP_PULL_SECRET=${12}
export MAS_LICENSE_URL=${13}
export SLS_ENDPOINT_URL=${14}
export SLS_REGISTRATION_KEY=${15}
export SLS_PUB_CERT_URL=${16}
export BAS_ENDPOINT_URL=${17}
export BAS_API_KEY=${18}
export BAS_PUB_CERT_URL=${19}
export MAS_JDBC_USER=${20}
export MAS_JDBC_PASSWORD=${21}
export MAS_JDBC_URL=${22}
export MAS_JDBC_CERT_URL=${23}
export MAS_DB_IMPORT_DEMO_DATA=${24}
export EXS_OCP_URL=${25}
export EXS_OCP_USER=${26}
export EXS_OCP_PWD=${27}
export RG_NAME=${28}
export RECEPIENT=${29}
export SENDGRID_API_KEY=${30}
export AZURE_SUBSC_ID=${31}
export AZURE_TENANT_ID=${32}
export AZURE_SP_CLIENT_ID=${33}
export AZURE_SP_CLIENT_PWD=${34}
export SELLER_SUBSCRIPTION_ID=${35}
export SELLER_RESOURCE_GROUP=${36}
export SELLER_COMPUTE_GALLERY=${37}
export SELLER_IMAGE_VERSION=${38}
export EMAIL_NOTIFICATION=${39}

# Load helper functions
. helper.sh
export -f log
export -f get_mas_creds
export -f retrieve_mas_ca_cert
export -f mark_provisioning_failed
export -f get_sls_endpoint_url
export -f get_sls_registration_key
export -f get_bas_endpoint_url
export -f get_bas_api_key

## Configure CloudWatch agent
if [[ $CLUSTER_TYPE == "aws" ]]; then
  log "Configuring CloudWatch logs agent"
  # TODO Temporary code to install CloudWatch agent. Later this will be done in AMI, and remove the code
  #-----------------------------------------
  cd /tmp
  wget https://s3.amazonaws.com/amazoncloudwatch-agent/redhat/amd64/latest/amazon-cloudwatch-agent.rpm
  rpm -U ./amazon-cloudwatch-agent.rpm
  #-----------------------------------------
  # Create CloudWatch agent config file
  mkdir -p /opt/aws/amazon-cloudwatch-agent/bin
  cat <<EOT >> /opt/aws/amazon-cloudwatch-agent/bin/config.json
{
  "agent": {
    "run_as_user": "root"
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [{
          "file_path": "/root/mas-on-aws/mas-provisioning.log",
          "log_group_name": "/ibm/mas/masocp-${RANDOM_STR}",
          "log_stream_name": "mas-provisioning-logs"
        }]
      }
    }
  }
}
EOT
  # Start CloudWatch agent service
  /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json -s
  sleep 60
  cd -
fi

# Check for input parameters
if [[ (-z $CLUSTER_TYPE) || (-z $DEPLOY_REGION) || (-z $ACCOUNT_ID) || (-z $CLUSTER_SIZE) \
   || (-z $RANDOM_STR) || (-z $BASE_DOMAIN) || (-z $SSH_KEY_NAME) || (-z $DEPLOY_WAIT_HANDLE) ]]; then
  log "ERROR: Required parameter not specified, please provide all the required inputs to the script."
  PRE_VALIDATION=fail
fi

if [[ $OFFERING_TYPE == "MAS Core + Cloud Pak for Data" ]]; then
  export DEPLOY_CP4D="true"
  export DEPLOY_MANAGE="false"
elif [[ $OFFERING_TYPE == "MAS Core + Manage (no Cloud Pak for Data)" ]]; then
  export DEPLOY_CP4D="false"
  export DEPLOY_MANAGE="true"
else
  log "ERROR: Incorrect value for OFFERING_TYPE - $OFFERING_TYPE"
  PRE_VALIDATION=fail
fi

## Variables
# OCP variables
export GIT_REPO_HOME=$(pwd)
export CLUSTER_NAME="masocp-${RANDOM_STR}"
export OPENSHIFT_USER="masocpuser"
export OPENSHIFT_PASSWORD=masocp${RANDOM_STR}pass
export OPENSHIFT_PULL_SECRET_FILE_PATH=${GIT_REPO_HOME}/pull-secret.json
export MASTER_NODE_COUNT="3"
export WORKER_NODE_COUNT="3"
export AZ_MODE="multi_zone"
export MAS_IMAGE_TEST_DOWNLOAD="cp.icr.io/cp/mas/admin-dashboard:5.1.27"
export BACKUP_FILE_NAME="terraform-backup-${CLUSTER_NAME}.zip"
if [[ $CLUSTER_TYPE == "aws" ]]; then
  export DEPLOYMENT_CONTEXT_UPLOAD_PATH="s3://masocp-${RANDOM_STR}-bucket-${DEPLOY_REGION}/ocp-cluster-provisioning-deployment-context/"
elif [[ $CLUSTER_TYPE == "azure" ]]; then
  export DEPLOYMENT_CONTEXT_UPLOAD_PATH="ocp-cluster-provisioning-deployment-context/${BACKUP_FILE_NAME}"
  export STORAGE_ACNT_NAME="masocp${RANDOM_STR}stgaccount"
fi
# Mongo variables
export MAS_INSTANCE_ID="mas-${RANDOM_STR}"
export MAS_CONFIG_DIR=/var/tmp/masconfigdir
export MONGODB_NAMESPACE="mongoce-${RANDOM_STR}"
# Amqstreams variables
export KAFKA_NAMESPACE=amq-streams
export KAFKA_CLUSTER_NAME=test
export KAFKA_CLUSTER_SIZE=small
export KAFKA_USER_NAME=masuser
# SLS variables
export SLS_NAMESPACE="ibm-sls-${RANDOM_STR}"
# BAS variables
export BAS_NAMESPACE="ibm-bas-${RANDOM_STR}"
export BAS_PERSISTENT_STORAGE=ocs-storagecluster-cephfs
export BAS_PASSWORD=basuser
export BAS_CONTACT_MAIL="bas.support@ibm.com"
export BAS_CONTACT_FIRSTNAME=Bas
export BAS_CONTACT_LASTNAME=Support
export GRAPHANA_PASSWORD=password
# MAS variables
#export MAS_ENTITLEMENT_KEY=$SLS_ENTITLEMENT_KEY
# CP4D variables
export CPD_ENTITLEMENT_KEY=$SLS_ENTITLEMENT_KEY
export CPD_VERSION=cpd40
export MAS_CHANNEL=8.7.x
export CPD_STORAGE_CLASS=ocs-storagecluster-cephfs
export CPD_NAMESPACE="ibm-common-services"
export CPD_SERVICES_NAMESPACE="cpd-services-${RANDOM_STR}"
# DB2WH variables
export DB2WH_META_STORAGE_CLASS=ocs-storagecluster-cephfs
export DB2WH_USER_STORAGE_CLASS=ocs-storagecluster-cephfs
export DB2WH_BACKUP_STORAGE_CLASS=ocs-storagecluster-cephfs
export DB2WH_LOGS_STORAGE_CLASS=ocs-storagecluster-cephfs
export DB2WH_TEMP_STORAGE_CLASS=ocs-storagecluster-cephfs
export DB2WH_INSTANCE_NAME=db2wh-db01
export DB2WH_VERSION=11.5.7.0-cn1
# Manage variables
export MAS_APP_ID=manage
export MAS_WORKSPACE_ID="wsmasocp"
export MAS_JDBC_CERT_LOCAL_FILE=$GIT_REPO_HOME/db.crt
export MAS_CLOUD_AUTOMATION_VERSION=1.0

RESP_CODE=0

# Export env variables which are not set by default during userdata execution
export HOME=/root

# Decide clutser size
case $CLUSTER_SIZE in
  small)
    log "Using small size cluster"
    export MASTER_NODE_COUNT="3"
    export WORKER_NODE_COUNT="3"
    ;;
  medium)
    log "Using medium size cluster"
    export MASTER_NODE_COUNT="3"
    export WORKER_NODE_COUNT="5"
    ;;
  large)
    log "Using large size cluster"
    export MASTER_NODE_COUNT="5"
    export WORKER_NODE_COUNT="7"
    ;;
  *)
    log "Using default small size cluster"
    export MASTER_NODE_COUNT="3"
    export WORKER_NODE_COUNT="3"
    ;;
esac

# Log the variable values
log "Below are common deployment parameters,"
echo " CLUSTER_TYPE: $CLUSTER_TYPE"
echo " OFFERING_TYPE: $OFFERING_TYPE"
echo " DEPLOY_REGION: $DEPLOY_REGION"
echo " ACCOUNT_ID: $ACCOUNT_ID"
echo " CLUSTER_SIZE: $CLUSTER_SIZE"
echo " RANDOM_STR: $RANDOM_STR"
echo " BASE_DOMAIN: $BASE_DOMAIN"
echo " BASE_DOMAIN_RG_NAME: $BASE_DOMAIN_RG_NAME"
echo " SSH_KEY_NAME: $SSH_KEY_NAME"
echo " DEPLOY_CP4D: $DEPLOY_CP4D"
echo " DEPLOY_MANAGE: $DEPLOY_MANAGE"
echo " MAS_LICENSE_URL: $MAS_LICENSE_URL"
echo " SLS_ENDPOINT_URL: $SLS_ENDPOINT_URL"
echo " SLS_REGISTRATION_KEY: $SLS_REGISTRATION_KEY"
echo " SLS_PUB_CERT_URL: $SLS_PUB_CERT_URL"
echo " BAS_ENDPOINT_URL: $BAS_ENDPOINT_URL"
echo " BAS_API_KEY: $BAS_API_KEY"
echo " BAS_PUB_CERT_URL: $BAS_PUB_CERT_URL"
echo " MAS_JDBC_USER: $MAS_JDBC_USER"
echo " MAS_JDBC_URL: $MAS_JDBC_URL"
echo " MAS_JDBC_CERT_URL: $MAS_JDBC_CERT_URL"
echo " MAS_DB_IMPORT_DEMO_DATA: $MAS_DB_IMPORT_DEMO_DATA"
echo " EXS_OCP_URL: $EXS_OCP_URL"
echo " EXS_OCP_USER: $EXS_OCP_USER"
echo " RG_NAME=$RG_NAME"
echo " RECEPIENT=$RECEPIENT"
echo " AZURE_SUBSC_ID=$AZURE_SUBSC_ID"
echo " AZURE_TENANT_ID=$AZURE_TENANT_ID"
echo " AZURE_SP_CLIENT_ID=$AZURE_SP_CLIENT_ID"
echo " SELLER_SUBSCRIPTION_ID=$SELLER_SUBSCRIPTION_ID"
echo " SELLER_RESOURCE_GROUP=$SELLER_RESOURCE_GROUP"
echo " SELLER_COMPUTE_GALLERY=$SELLER_COMPUTE_GALLERY"
echo " SELLER_IMAGE_VERSION=$SELLER_IMAGE_VERSION"
echo " EMAIL_NOTIFICATION: $EMAIL_NOTIFICATION"

echo " HOME: $HOME"
echo " GIT_REPO_HOME: $GIT_REPO_HOME"
echo " CLUSTER_NAME: $CLUSTER_NAME"
echo " OPENSHIFT_USER: $OPENSHIFT_USER"
echo " OPENSHIFT_PULL_SECRET_FILE_PATH: $OPENSHIFT_PULL_SECRET_FILE_PATH"
echo " MASTER_NODE_COUNT: $MASTER_NODE_COUNT"
echo " WORKER_NODE_COUNT: $WORKER_NODE_COUNT"
echo " AZ_MODE: $AZ_MODE"
echo " MAS_IMAGE_TEST_DOWNLOAD: $MAS_IMAGE_TEST_DOWNLOAD"
echo " BACKUP_FILE_NAME: $BACKUP_FILE_NAME"
echo " DEPLOYMENT_CONTEXT_UPLOAD_PATH: $DEPLOYMENT_CONTEXT_UPLOAD_PATH"
echo " STORAGE_ACNT_NAME: $STORAGE_ACNT_NAME"
echo " MAS_INSTANCE_ID: $MAS_INSTANCE_ID"
echo " MAS_CONFIG_DIR: $MAS_CONFIG_DIR"
echo " KAFKA_NAMESPACE: $KAFKA_NAMESPACE"
echo " KAFKA_CLUSTER_NAME: $KAFKA_CLUSTER_NAME"
echo " KAFKA_CLUSTER_SIZE: $KAFKA_CLUSTER_SIZE"
echo " KAFKA_USER_NAME: $KAFKA_USER_NAME"
echo " BAS_PERSISTENT_STORAGE: $BAS_PERSISTENT_STORAGE"
echo " BAS_CONTACT_MAIL: $BAS_CONTACT_MAIL"
echo " BAS_CONTACT_FIRSTNAME: $BAS_CONTACT_FIRSTNAME"
echo " BAS_CONTACT_LASTNAME: $BAS_CONTACT_LASTNAME"
echo " CPD_STORAGE_CLASS: $CPD_STORAGE_CLASS"
echo " MAS_APP_ID: $MAS_APP_ID"
echo " MAS_WORKSPACE_ID: $MAS_WORKSPACE_ID"
echo " MAS_JDBC_CERT_LOCAL_FILE: $MAS_JDBC_CERT_LOCAL_FILE"

# Get deployment options
export DEPLOY_CP4D=$(echo $DEPLOY_CP4D | cut -d '=' -f 2)
export DEPLOY_MANAGE=$(echo $DEPLOY_MANAGE | cut -d '=' -f 2)

if [[ $CLUSTER_TYPE == "azure" ]]; then
  # Perform az login for accessing blob storage
  az login --identity
  az resource list -n masocp-${RANDOM_STR}-bootnode-vm
fi

# Perform prevalidation checks
log "===== PRE-VALIDATION STARTED ====="
./pre-validate.sh
retcode=$?
log "Pre validation return code is $retcode"
if [[ $retcode -ne 0 ]]; then
  log "Prevalidation checks failed"
  PRE_VALIDATION=fail
  mark_provisioning_failed $retcode
else
  log "Prevalidation checks successful"
  PRE_VALIDATION=pass
fi
log "===== PRE-VALIDATION COMPLETED ($PRE_VALIDATION) ====="
exit 0
# Prrform the MAS deployment only if pre-validation checks are passed
if [[ $PRE_VALIDATION == "pass" ]]; then
  ## If user provided input of Openshift API url along with creds, then use the provided details for deployment of other components like CP4D, MAS etc.
  ## Otherwise, proceed with new cluster creation.
  if [[ -n $EXS_OCP_URL && -n $EXS_OCP_USER && -n $EXS_OCP_PWD ]]; then
    log "Openshift cluster details provided"
    # https://api.masocp-cluster.mas4aws.com/
    # https://api.ftmpsl-ocp-dev3.cp.fyre.ibm.com:6443/

    log "Debug: before: CLUSTER_NAME: $CLUSTER_NAME  BASE_DOMAIN: $BASE_DOMAIN"
    split_ocp_api_url $EXS_OCP_URL
    log "Debug: after: CLUSTER_NAME: $CLUSTER_NAME  BASE_DOMAIN: $BASE_DOMAIN"
    # echo $BASE_DOMAIN
    export OPENSHIFT_USER=$EXS_OCP_USER
    export OPENSHIFT_PASSWORD=$EXS_OCP_PWD
    export OPENSHIFT_USER_PROVIDE="true"
  else
    ## No input from user. Generate Cluster Name, Username, and Password.
    echo "Debug: No cluster details or insufficient data provided. Proceed to create new OCP cluster later"
    export CLUSTER_NAME="masocp-${RANDOM_STR}"
    export OPENSHIFT_USER="masocpuser"
    export OPENSHIFT_PASSWORD=masocp${RANDOM_STR}pass
    export OPENSHIFT_USER_PROVIDE="false"
  fi
  log " OPENSHIFT_USER_PROVIDE=$OPENSHIFT_USER_PROVIDE"

  # Create Red Hat pull secret
  echo "$OCP_PULL_SECRET" > $OPENSHIFT_PULL_SECRET_FILE_PATH
  chmod 600 $OPENSHIFT_PULL_SECRET_FILE_PATH

  # Call cloud specific script
  chmod +x $CLUSTER_TYPE/*.sh
  log "===== PROVISIONING STARTED ====="
  log "Calling cloud specific automation ..."
  cd $CLUSTER_TYPE
  ./deploy.sh
  retcode=$?
  log "Deployment return code is $retcode"
  if [[ $retcode -eq 0 ]]; then
    log "Deployment successful"
    log "===== PROVISIONING COMPLETED ====="
    export STATUS=SUCCESS
    export STATUS_MSG="MAS deployment completed successfully."
    export MESSAGE_TEXT="Please import the attached certificate into the browser to access MAS UI."
    export OPENSHIFT_CLUSTER_CONSOLE_URL="https:\/\/console-openshift-console.apps.${CLUSTER_NAME}.${BASE_DOMAIN}"
    export OPENSHIFT_CLUSTER_API_URL="https:\/\/api.${CLUSTER_NAME}.${BASE_DOMAIN}:6443"
    export OPENSHIFT_CLUSTER_API_URL="https:\/\/api.${CLUSTER_NAME}.${BASE_DOMAIN}:6443"
    export MAS_URL_INIT_SETUP="https:\/\/admin.mas-${RANDOM_STR}.apps.${CLUSTER_NAME}.${BASE_DOMAIN}\/initialsetup"
    export MAS_URL_ADMIN="https:\/\/admin.mas-${RANDOM_STR}.apps.${CLUSTER_NAME}.${BASE_DOMAIN}"
    export MAS_URL_WORKSPACE="https:\/\/$MAS_WORKSPACE_ID.home.mas-${RANDOM_STR}.apps.${CLUSTER_NAME}.${BASE_DOMAIN}"
    RESP_CODE=0
  else
    mark_provisioning_failed $retcode
  fi
  if [[ $CLUSTER_TYPE == "azure" ]]; then
    az tag update --operation merge --resource-id /subscriptions/${AZURE_SUBSC_ID}/resourceGroups/${RG_NAME} --tags DeploymentStatus="${STATUS}#${STATUS_MSG}" > /dev/null
  fi
fi

cd $GIT_REPO_HOME/$CLUSTER_TYPE
if [[ $CLUSTER_TYPE == "aws" ]]; then
  # Complete the template deployment
  cd $GIT_REPO_HOME/$CLUSTER_TYPE
  # Complete the CFT stack creation successfully
  log "Sending completion signal to CloudFormation stack."
  log " STATUS=$STATUS"
  log " STATUS_MSG=$STATUS_MSG"
  curl -k -X PUT -H 'Content-Type:' --data-binary "{\"Status\":\"SUCCESS\",\"Reason\":\"MAS deployment complete\",\"UniqueId\":\"ID-$CLUSTER_TYPE-$CLUSTER_SIZE-$CLUSTER_NAME\",\"Data\":\"${STATUS}#${STATUS_MSG}\"}" "$DEPLOY_WAIT_HANDLE"
fi

# Send email notification
if [[ $EMAIL_NOTIFICATION == "true" ]]; then
  sleep 30
  log "Buyer has explicitly opted for email notification, sending notification"
  ./notify.sh
else
  log "Buyer chose to not send email notification"
fi

# Upload log file to object store
if [[ $CLUSTER_TYPE == "aws" ]]; then
  # Upload the log file to s3
  aws s3 cp $GIT_REPO_HOME/mas-provisioning.log $DEPLOYMENT_CONTEXT_UPLOAD_PATH
elif [[ $CLUSTER_TYPE == "azure" ]]; then
  # Upload the log file to blob storage
  az storage blob upload --account-name ${STORAGE_ACNT_NAME} --container-name masocpcontainer --name ocp-cluster-provisioning-deployment-context/mas-provisioning.log --file $GIT_REPO_HOME/mas-provisioning.log --auth-mode login
fi
exit $RESP_CODE
