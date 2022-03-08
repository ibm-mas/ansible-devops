#!/bin/bash

# This script will send email notification using AWS SES service
cd $GIT_REPO_HOME
MSG_FILE_SRC="aws/notification/email/message.json"
MSG_FILE="aws/notification/email/message-updated.json"

## Raw email using SES
if [[ $STATUS == "SUCCESS" ]]; then
  # Login to OCP cluster
  oc login -u $OPENSHIFT_USER -p $OPENSHIFT_PASSWORD --server=https://api.${CLUSTER_NAME}.${BASE_DOMAIN}:6443
  # Collect email details
  certfile="/tmp/${CLUSTER_NAME}-ca.crt"
  retrieve_mas_ca_cert $RANDOM_STR $certfile
  certcontents=$(cat $certfile | tr '\n' "," | sed "s/,/\\\\\\\n/g")
  certcontents=$(echo $certcontents | sed 's/\//\\\//g')
  log "$certcontents"
    if [[ -z $SLS_ENDPOINT_URL ]]; then
    get_sls_endpoint_url $RANDOM_STR
    log " CALL_SLS_URL=$CALL_SLS_URL"
  fi
  if [[ -z $BAS_ENDPOINT_URL ]]; then
    get_bas_endpoint_url $RANDOM_STR
    log " CALL_BAS_URL=$CALL_BAS_URL"
  fi
  get_mas_creds $RANDOM_STR
  log " MAS_USER=$MAS_USER"
  log " MAS_PASSWORD=$MAS_PASSWORD"
fi
# Get list of senders from SES configuration
for item in `aws ses list-identities --region $DEPLOY_REGION | jq '.Identities' | grep -v '\[\|\]' | tr -d ' ' | tr -d '"' | tr -d ','`; do
  aws ses get-identity-verification-attributes --identities $item --region $DEPLOY_REGION | jq ".VerificationAttributes" | grep "Success"
  if [[ $? -eq 0 ]]; then
    if [[ -z $RECEPIENT ]]; then
      RECEPIENT=$item
      FROM_EMAIL=$item
    else
      RECEPIENT=$RECEPIENT,$item
    fi
  fi
done
if [[ -z $RECEPIENT ]]; then
    log "No verified email addresses found in the SES service in $DEPLOY_REGION region, no email will be sent"
else
    log "Found verified email addresses $RECEPIENT"
    /usr/bin/cp -f $MSG_FILE_SRC $MSG_FILE
    sed -i "s/\[SENDER\]/$FROM_EMAIL/g" $MSG_FILE
    sed -i "s/\[RECEIVER\]/$RECEPIENT/g" $MSG_FILE
    sed -i "s/\[IMPORT-CERT-MSG\]/$IMPORT_CERT_MSG/g" $MSG_FILE
    sed -i "s/\[STATUS\]/$STATUS/g" $MSG_FILE
    sed -i "s/\[REGION\]/$DEPLOY_REGION/g" $MSG_FILE
    sed -i "s/\[UNIQ-STR\]/$RANDOM_STR/g" $MSG_FILE
    sed -i "s/\[OPENSHIFT-CLUSTER-CONSOLE-URL\]/$OPENSHIFT_CLUSTER_CONSOLE_URL/g" $MSG_FILE
    sed -i "s/\[OPENSHIFT-CLUSTER-API-URL\]/$OPENSHIFT_CLUSTER_API_URL/g" $MSG_FILE
    sed -i "s/\[OCP-USER\]/$OPENSHIFT_USER/g" $MSG_FILE
    sed -i "s/\[OCP-PASSWORD\]/$OPENSHIFT_PASSWORD/g" $MSG_FILE
    sed -i "s/\[MAS-URL-INIT-SETUP\]/$MAS_URL_INIT_SETUP/g" $MSG_FILE
    sed -i "s/\[MAS-URL-ADMIN\]/$MAS_URL_ADMIN/g" $MSG_FILE
    sed -i "s/\[MAS-URL-WORKSPACE\]/$MAS_URL_WORKSPACE/g" $MSG_FILE
    sed -i "s/\[MAS-USER\]/$MAS_USER/g" $MSG_FILE
    sed -i "s/\[MAS-PASSWORD\]/$MAS_PASSWORD/g" $MSG_FILE
    sed -i "s/\[SLS-ENDPOINT-URL\]/$CALL_SLS_URL/g" $MSG_FILE
    sed -i "s/\[BAS-ENDPOINT-URL\]/$CALL_BAS_URL/g" $MSG_FILE
    sed -i "s/\[CA-CERT\]/$certcontents/g" $MSG_FILE
    log "Sending email using below file ..."
    cat $MSG_FILE
    aws ses send-raw-email --cli-binary-format raw-in-base64-out --raw-message file://${MSG_FILE} --region $DEPLOY_REGION
fi
