#!/bin/bash
# Script to cleanup the MAS deployment on Azure.
# It will delete the resource group which in turn deletes all the resources from that resource group."
# Hence, make sure you do not have any other resources created in the same resource group.
#

# Fail the script if any of the steps fail
set -e

RED='\033[0;31m'
BLUE='\033[0;36m'
GREEN='\033[0;32m'
NC='\033[0m'

# Functions
usage() {
  echo "Usage: cleanup-mas-deployment.sh -r bootnode-resource-group -u unique-string"
  echo " "
  echo "  - If resource group is present and it has the tag 'clusterUniqueString', you can delete the MAS instance by resource group name."
  echo "  - If you want to cleanup the resources based on the unique string, then provide the 'unique-string' parameter."
  echo "    In this case, the associated resource group won't be deleted even if it exists. It should be deleted explicitly."
  echo ""
  echo "  Do not specify both 'bootnode-resource-group' and 'unique-string' parameters at the same time."
  echo "  For example, "
  echo "   cleanup-mas-deployment.sh -r mas-instance-rg"
  echo "   cleanup-mas-deployment.sh -u gr5t67"
  exit 1
}

echoGreen() {
  echo -e "${GREEN}$1${NC}"
}

echoBlue() {
  echo -e "${BLUE}$1${NC}"
}

echoRed() {
  echo -e "\n${RED}$1${NC}"
}

# Read arguments
if [[ $# -eq 0 ]]; then
  echoRed "No arguments provided with $0. Exiting.."
  usage
else
  while getopts 'r:u:?h' c; do
    case $c in
    r)
      RG_NAME=$OPTARG
      ;;
    u)
      UNIQUE_STR=$OPTARG
      ;;
    h | *)
      usage
      ;;
    esac
  done
fi
echoBlue "==== Execution started at `date` ===="
echo "Script Inputs:"
echo " Bootnode resource group = $RG_NAME"
echo " Unique string = $UNIQUE_STR"

# Check if bootnode resource group or unique string is provided
if [[ (-z $RG_NAME) && (-z $UNIQUE_STR) ]]; then
  echoRed "ERROR: Both the parameters 'bootnode-resource-group' and 'unique-string' are empty, one of these should have a value" 
  usage
fi

# If resource group is provided, do not specify unique string
if [[ (-n $RG_NAME) && (-n $UNIQUE_STR) ]]; then
  echoRed "ERROR: Do not specify both 'bootnode-resource-group' and 'unique-string'. If 'bootnode-resource-group' is specified, do not specify 'unique-string'."
  usage
fi

# Check if bootnode resource group exists
if [[ -n $RG_NAME ]]; then
  set +e
  output=$(az group exists -n $RG_NAME)
  if [[ $output == "false" ]]; then
    echoRed "ERROR: Bootnode resource group $RG_NAME does not exist"
    exit 1
  fi
  set -e
fi

# Get subscription Id
SUB_ID=$(az account show | jq ".id" | tr -d '"')
echo "SUB_ID: $SUB_ID"

## Delete OCP cluster resource group
echoBlue "Trying to delete OCP cluster resource group"
if [[ -n $RG_NAME ]]; then
  # Get the cluster unique string
  UNIQ_STR=$(az deployment group list --resource-group $RG_NAME | jq ".[] | select(.properties.outputs.clusterUniqueString.value != null).properties.outputs.clusterUniqueString.value" | tr -d '"')
  echo "Deleting by 'bootnode-resource-group' $RG_NAME"
else
  UNIQ_STR=$UNIQUE_STR
  echo "Deleting by 'unique-string' $UNIQ_STR"
fi
echo "UNIQ_STR: $UNIQ_STR"
if [[ ($UNIQ_STR == "null") || (-z $UNIQ_STR) ]]; then
  echo "Could not retrieve the unique string from the resource group. Could not find a tag 'clusterUniqueString' on the resource group."
  echo "Skipping the deletion of OCP cluster resource group, will continue to delete the bootnode resource group"
else
  # Get the OCP cluster resource group name
  OCP_CLUSTER_RG_NAME=$(az group list | jq ".[] | select(.name | contains(\"masocp-$UNIQ_STR\")).name" | tr -d '"')
  echo "OCP_CLUSTER_RG_NAME: $OCP_CLUSTER_RG_NAME"
  if [[ -n $OCP_CLUSTER_RG_NAME ]]; then
    # Check if OCP cluster resource group exists
    rg=$(az group list | jq ".[] | select(.name | contains(\"$OCP_CLUSTER_RG_NAME\")).name" | tr -d '"')
    if [[ -z $rg ]]; then
      echo "OCP cluster resource group $OCP_CLUSTER_RG_NAME does not exist"
    else
      # Delete the resource group of OCP cluster
      echo "Deleting resource group $OCP_CLUSTER_RG_NAME ..."
      az group delete --yes --name $OCP_CLUSTER_RG_NAME
      echo "Deleted resource group $OCP_CLUSTER_RG_NAME"
    fi
  else
    echo "OCP cluster resource group does not seem to exist"
    echo "Skipping the deletion of OCP cluster resource group, will continue to delete the bootnode resource group"
  fi

  # Get domain and domain resource group
  BASE_DOMAIN=$(az deployment group list --resource-group $RG_NAME | jq ".[] | select(.properties.outputs.clusterUniqueString.value != null).properties.parameters.publicDomain.value" | tr -d '"')
  BASE_DOMAIN_RG_NAME=$(az deployment group list --resource-group $RG_NAME | jq ".[] | select(.properties.outputs.clusterUniqueString.value != null).properties.parameters.publicDomainResourceGroup.value" | tr -d '"')
  echo "BASE_DOMAIN=$BASE_DOMAIN"
  echo "BASE_DOMAIN_RG_NAME=$BASE_DOMAIN_RG_NAME"
  if [[ (-n $BASE_DOMAIN) || (-n $BASE_DOMAIN_RG_NAME) ]]; then
    # Delete the DNS zone A records
    A_RECS=$(az network dns record-set a list -g $BASE_DOMAIN_RG_NAME -z $BASE_DOMAIN | jq ".[] | select(.name == \"*.apps.masocp-$UNIQ_STR\").name" | tr -d '"')
    echo "A_RECS = $A_RECS"
    if [[ -n $A_RECS ]]; then
      for inst in $A_RECS; do
        # Delete A record
        az network dns record-set a delete -g $BASE_DOMAIN_RG_NAME -z $BASE_DOMAIN -n $inst --yes
        echo "Deleted record set $inst"
      done
    fi
    # Delete the DNS zone CNAME records
    CNAME_RECS=$(az network dns record-set cname list -g $BASE_DOMAIN_RG_NAME -z $BASE_DOMAIN | jq ".[] | select(.name == \"api.masocp-$UNIQ_STR\").name" | tr -d '"')
    echo "CNAME_RECS = $CNAME_RECS"
    if [[ -n $CNAME_RECS ]]; then
      for inst in $CNAME_RECS; do
        # Delete A record
        az network dns record-set cname delete -g $BASE_DOMAIN_RG_NAME -z $BASE_DOMAIN -n $inst --yes
        echo "Deleted record set $inst"
      done
    fi
  fi
fi

## Delete bootnode resource group
if [[ -n $RG_NAME ]]; then
  echoBlue "Trying to delete bootnode resource group"
  # Delete the role assignments
  ROLEASMNTS=$(az role assignment list --all | jq ".[] | select(.resourceGroup == \"$RG_NAME\").id" | tr -d '"')
  echo "ROLEASMNTS = $ROLEASMNTS"
  if [[ -n $ROLEASMNTS ]]; then
    echo "Found role assignments for this MAS instance"
    roleasnmnts=""
    for inst in $ROLEASMNTS; do
      # Add to the list
      roleasnmnts="$roleasnmnts $inst"
    done
    echo "Role assignment list: $roleasnmnts"
    az role assignment delete --ids $roleasnmnts
    sleep 10
  else
    echo "No role assignments for this MAS instance"
  fi
  # Check if bootnode resource group exist
  rg=$(az group list | jq ".[] | select(.name | contains(\"$RG_NAME\")).name" | tr -d '"')
  if [[ -z $rg ]]; then
    echo "Bootnode resource group $RG_NAME does not exist"
  else
    # Delete the resource group of bootnode
    echo "Deleting resource group $RG_NAME ..."
    az group delete --yes --name $RG_NAME
    echo "Deleted resource group $RG_NAME"
  fi
else
  echo "No 'bootnode-resource-group' specified, you may need to delete the resource group explicitly if exists, or run the script with -r 'bootnode-resource-group' parameter"
fi
echoBlue "==== Execution completed at `date` ===="
