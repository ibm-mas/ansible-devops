#!/bin/bash

# This script will send email notification using SendGrid service
cd $GIT_REPO_HOME
MSG_FILE_SRC_DETAILS="azure/notification/email/message-details.html"
MSG_FILE_SRC_CREDS="azure/notification/email/message-creds.html"
MSG_FILE_DETAILS="azure/notification/email/message-details-updated.html"
MSG_FILE_CREDS="azure/notification/email/message-creds-updated.html"

#if [[ $STATUS == "SUCCESS" ]]; then
  # Login to OCP cluster
#  oc login -u $OPENSHIFT_USER -p $OPENSHIFT_PASSWORD --server=https://api.${CLUSTER_NAME}.${BASE_DOMAIN}:6443
  # Collect email details
#  certfile="/tmp/${CLUSTER_NAME}-ca.crt"
#  retrieve_mas_ca_cert $RANDOM_STR $certfile
#  certcontents=$(cat $certfile | tr '\n' "," | sed "s/,/\\\\\\\n/g")
#  certcontents=$(echo $certcontents | sed 's/\//\\\//g')
#  log "$certcontents"
#    if [[ -z $SLS_ENDPOINT_URL ]]; then
#    get_sls_endpoint_url $RANDOM_STR
#    log " CALL_SLS_URL=$CALL_SLS_URL"
#  fi
#  if [[ -z $BAS_ENDPOINT_URL ]]; then
#    get_bas_endpoint_url $RANDOM_STR
#    log " CALL_BAS_URL=$CALL_BAS_URL"
#  fi
#  get_mas_creds $RANDOM_STR
#  log " MAS_USER=$MAS_USER"
#  log " MAS_PASSWORD=$MAS_PASSWORD"
#fi

# Temp code
certfilename="${CLUSTER_NAME}-ca.crt"
certfilepath="/tmp/${certfilename}"
echo "dummy data" >> $certfilepath

# Get the first verified sender
VERIFIED_SENDER=$(curl --request GET --url https://api.sendgrid.com/v3/verified_senders --header "Authorization: Bearer $SENDGRID_API_KEY" --header "Content-Type: application/json" | jq '.results[] | select(.verified == true) | .from_email+":"+.from_name' | head -1)
log " VERIFIED_SENDER=$VERIFIED_SENDER"
if [[ -n $VERIFIED_SENDER ]]; then
  # Send email for environment details
  /usr/bin/cp -f $MSG_FILE_SRC_DETAILS $MSG_FILE_DETAILS
  emailid=$(echo $VERIFIED_SENDER | cut -d ':' -f 1 | tr -d '"')
  name=$(echo $VERIFIED_SENDER | cut -d ':' -f 2 | tr -d '"')
  sed -i "s/\[MESSAGE-TEXT\]/$MESSAGE_TEXT/g" $MSG_FILE_DETAILS
  sed -i "s/\[STATUS\]/$STATUS/g" $MSG_FILE_DETAILS
  sed -i "s/\[REGION\]/$DEPLOY_REGION/g" $MSG_FILE_DETAILS
  sed -i "s/\[UNIQ-STR\]/$RANDOM_STR/g" $MSG_FILE_DETAILS
  sed -i "s/\[OPENSHIFT-CLUSTER-CONSOLE-URL\]/$OPENSHIFT_CLUSTER_CONSOLE_URL/g" $MSG_FILE_DETAILS
  sed -i "s/\[OPENSHIFT-CLUSTER-API-URL\]/$OPENSHIFT_CLUSTER_API_URL/g" $MSG_FILE_DETAILS
  sed -i "s/\[OCP-USER\]/$OPENSHIFT_USER/g" $MSG_FILE_DETAILS
  sed -i "s/\[MAS-URL-INIT-SETUP\]/$MAS_URL_INIT_SETUP/g" $MSG_FILE_DETAILS
  sed -i "s/\[MAS-URL-ADMIN\]/$MAS_URL_ADMIN/g" $MSG_FILE_DETAILS
  sed -i "s/\[MAS-URL-WORKSPACE\]/$MAS_URL_WORKSPACE/g" $MSG_FILE_DETAILS
  sed -i "s/\[MAS-USER\]/$MAS_USER/g" $MSG_FILE_DETAILS
  sed -i "s/\[SLS-ENDPOINT-URL\]/$CALL_SLS_URL/g" $MSG_FILE_DETAILS
  sed -i "s/\[BAS-ENDPOINT-URL\]/$CALL_BAS_URL/g" $MSG_FILE_DETAILS
  log "Sending email using below file ..."
  bodyHTML=$(cat $MSG_FILE_DETAILS)
  log ""
  log " EmailID=$emailid"
  log " Name=$name"
  log " BodyHTML=$bodyHTML"
  ENCODEDED_TEXT=$(eval cat $certfilepath | base64 -w 0)
  maildata="{\"personalizations\": [{\"to\": [{\"email\": \"${RECEPIENT}\"}]}],\"from\": {\"email\": \"${emailid}\", \"name\": \"$name\"},\"subject\": \"MAS Provisioning Notification (contains an attachment)\",\"content\": [{\"type\": \"text/html\",\"value\": \"${bodyHTML}\"}],\"attachments\": [{\"content\": \"${ENCODEDED_TEXT}\", \"type\": \"text/plain\", \"filename\": \"$certfilename\"}]}"
  log " maildata=\"$maildata\""
  curl --request POST --url https://api.sendgrid.com/v3/mail/send --header "Authorization: Bearer $SENDGRID_API_KEY" --header "Content-Type: application/json" --data "$maildata"
  # Send email for passwords
  /usr/bin/cp -f $MSG_FILE_SRC_CREDS $MSG_FILE_CREDS
  emailid=$(echo $VERIFIED_SENDER | cut -d ':' -f 1 | tr -d '"')
  name=$(echo $VERIFIED_SENDER | cut -d ':' -f 2 | tr -d '"')
  sed -i "s/\[MESSAGE-TEXT\]/$MESSAGE_TEXT/g" $MSG_FILE_CREDS
  sed -i "s/\[STATUS\]/$STATUS/g" $MSG_FILE_CREDS
  sed -i "s/\[REGION\]/$DEPLOY_REGION/g" $MSG_FILE_CREDS
  sed -i "s/\[UNIQ-STR\]/$RANDOM_STR/g" $MSG_FILE_CREDS
  sed -i "s/\[OCP-PASSWORD\]/$OPENSHIFT_PASSWORD/g" $MSG_FILE_CREDS
  sed -i "s/\[MAS-PASSWORD\]/$MAS_PASSWORD/g" $MSG_FILE_CREDS
  log "Sending email using below file ..."
  bodyHTML=$(cat $MSG_FILE_CREDS)
  log " EmailID=$emailid"
  log " Name=$name"
  log " BodyHTML=$bodyHTML"
  maildata="{\"personalizations\": [{\"to\": [{\"email\": \"${RECEPIENT}\"}]}],\"from\": {\"email\": \"${emailid}\", \"name\": \"$name\"},\"subject\": \"MAS Provisioning Notification (contains credentials)\",\"content\": [{\"type\": \"text/html\",\"value\": \"${bodyHTML}\"}],\"filename\": \"$certfilename\"}]}"
  log " maildata=\"$maildata\""
  curl --request POST --url https://api.sendgrid.com/v3/mail/send --header "Authorization: Bearer $SENDGRID_API_KEY" --header "Content-Type: application/json" --data "$maildata"
fi
