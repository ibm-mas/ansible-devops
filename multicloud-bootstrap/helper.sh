#!/bin/bash

# Helper functions
log() {
  echo "$(date +%a-%d-%b-%Y-%H-%M-%S) $1"
}

# Retrieve MAS CA certificate
retrieve_mas_ca_cert() {
  uniqstr=$1
  filepath=$2
  # Wait until the secret is available
  found="false"
  counter=0
  while [[ $found == "false" ]] && [[ $counter < 20 ]]; do
    oc get secret mas-${uniqstr}-cert-public-ca -n ibm-common-services
    if [[ $? -eq 1 ]]; then
      log "OCP secret mas-${uniqstr}-cert-public-ca not found ($counter), waiting ..."
      sleep 30
      counter=$((counter+1))
      continue
    else
      log "OCP secret mas-${uniqstr}-cert-public-ca found"
      found="true"
    fi
    oc get secret mas-${uniqstr}-cert-public-ca -n ibm-common-services -o yaml | grep ca.crt | cut -d ':' -f 2 | tr -d " ,\"" | base64 -d > $filepath
  done
}

# Get credentials for MAS
get_mas_creds() {
  uniqstr=$1
  # Wait until the secret is available
  found="false"
  counter=0
  while [[ $found == "false" ]] && [[ $counter < 20 ]]; do
    oc get secret mas-${uniqstr}-credentials-superuser -n mas-mas-${uniqstr}-core
    if [[ $? -eq 1 ]]; then
      log "OCP secret mas-${uniqstr}-credentials-superuser not found ($counter), waiting ..."
      sleep 30
      counter=$((counter+1))
      continue
    else
      log "OCP secret mas-${uniqstr}-credentials-superuser found"
      found="true"
    fi
    sleep 60
    username=$(oc get secret mas-${uniqstr}-credentials-superuser -n mas-mas-${uniqstr}-core -o json | grep "\"username\"" | cut -d ':' -f 2 | tr -d " ,\"" | base64 -d)
    password=$(oc get secret mas-${uniqstr}-credentials-superuser -n mas-mas-${uniqstr}-core -o json | grep "\"password\"" | cut -d ':' -f 2 | tr -d " ,\"" | base64 -d)
  done

  if [[ $found == "false" ]]; then
    export MAS_USER=null
    export MAS_PASSWORD=null
    log "MAS username and password not found"
  else
    export MAS_USER=$username
    export MAS_PASSWORD=$password
    log "MAS username and password found"
  fi
}

get_sls_endpoint_url() {
  uniqstr=$1
  export CALL_SLS_URL="https://$(oc get route ${SLS_INSTANCE_NAME} -n ibm-sls-${uniqstr} | grep "sls" | awk {'print $2'})"
}

get_sls_registration_key() {
  uniqstr=$1
  
}

get_bas_endpoint_url() {
  uniqstr=$1
  export CALL_BAS_URL="https:\/\/$(oc get route bas-endpoint -n ibm-bas-${uniqstr} | grep "bas" | awk {'print $2'})"
}

get_bas_api_key() {
  uniqstr=$1
  
}

# Mark provisioning failed
mark_provisioning_failed() {
  retcode=$1
  log "Deployment failed"
  log "===== PROVISIONING FAILED ====="
  RESP_CODE=1
  export STATUS=FAILURE
  export STATUS_MSG=NA
  if [[ $retcode -eq 2 ]]; then
    export STATUS_MSG="Failed in the Ansible playbook execution."
  elif [[ $retcode -eq 11 ]]; then
    export STATUS_MSG="This region is not supported for MAS deployment."
  elif [[ $retcode -eq 12 ]]; then
    export STATUS_MSG="The provided ER key is not valid. It does not have access to download the MAS images."
  elif [[ $retcode -eq 13 ]]; then
    export STATUS_MSG="The provided Hosted zone is not a public hosted zone. Please provide a public hosted zone."
  elif [[ $retcode -eq 14 ]]; then
    export STATUS_MSG="The JDBC details for MAS Manage are missing or invalid."
  elif [[ $retcode -eq 15 ]]; then
    export STATUS_MSG="Please provide all the inputs to use existing SLS."
  elif [[ $retcode -eq 16 ]]; then
    export STATUS_MSG="Please provide all the inputs to use existing BAS."
  elif [[ $retcode -eq 17 ]]; then
    export STATUS_MSG="Please provide OCP pull secret."
  elif [[ $retcode -eq 18 ]]; then
    export STATUS_MSG="Please provide a valid MAS license URL."
  elif [[ $retcode -eq 19 ]]; then
    export STATUS_MSG="Please provide all the inputs to use existing OCP."
  elif [[ $retcode -eq 21 ]]; then
    export STATUS_MSG="Failure in creating OCP cluster."
  elif [[ $retcode -eq 22 ]]; then
    export STATUS_MSG="Failure in creating Bastion host."
  elif [[ $retcode -eq 23 ]]; then
    export STATUS_MSG="Failed in uploading deployment context to S3."
  elif [[ $retcode -eq 24 ]]; then
    export STATUS_MSG="Failure in configuring OCP cluster."
  fi
  export MESSAGE_TEXT=NA
  export OPENSHIFT_CLUSTER_CONSOLE_URL=NA
  export OPENSHIFT_CLUSTER_API_URL=NA
  export MAS_URL_INIT_SETUP=NA
  export MAS_URL_ADMIN=NA
  export MAS_URL_WORKSPACE=NA
  export CLUSTER_NAME=NA
  export BASE_DOMAIN=NA
  export OCP_USERNAME=NA
  export OCP_PASSWORD=NA
  export MAS_USER=NA
  export MAS_PASSWORD=NA
  export SLS_URL=NA
}

# Split the CLUSTER_NAME and BASE_DOMAIN from provided Openshift API url
split_ocp_api_url() {
  apiurl=$1
  apiurl="${apiurl//\// }"
  COUNTER=0
  BASE_DOMAIN=""
  CLUSTER_NAME=""
  oldIFS="$IFS"
  IFS='.'; for i in $apiurl; do 
      # echo $i 
      if [[ $COUNTER -eq 1 ]]; then
          CLUSTER_NAME=$i
      elif [[ $COUNTER -gt 1 ]]; then
          if [[ $COUNTER -eq 2 ]]; then
              BASE_DOMAIN=$i
          else
              BASE_DOMAIN=$BASE_DOMAIN"-"$i
          fi
      fi
      COUNTER=$((COUNTER + 1 ))
  done
  IFS="$oldIFS"
  # echo $CLUSTER_NAME
  BASE_DOMAIN=${BASE_DOMAIN//-/.}
  ## Remove any possible port number provided by user
  strindex() { 
    x="${1%%$2*}"
    [[ "$x" = "$1" ]] && echo -1 || echo "${#x}"
  }
  colIndex=`strindex $BASE_DOMAIN ":"`
  if [[ $colIndex -ge 0 ]]; then
      port=${BASE_DOMAIN:$colIndex:6}
      BASE_DOMAIN="${BASE_DOMAIN/$port/}"
  fi

  export CLUSTER_NAME=$CLUSTER_NAME
  export BASE_DOMAIN=$BASE_DOMAIN
}
