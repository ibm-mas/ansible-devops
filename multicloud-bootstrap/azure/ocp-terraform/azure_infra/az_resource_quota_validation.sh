#!/bin/bash
#
## Code starts here

#
# Resource quota validation for the Azure subscription
#
# The script requires the below variables values to be set prior to the execution

## Handle bad usage of the script:

## Declaring the vCPUs required for each service.

export log_output_display="true"

## The minimum VCPU count required for each service. 
export WSL=12
export WKC=27
export WML=16
export DV=16
export WOS=30
export SPARK=7
export CDE=4
export STREAMS=1
export STREAMS_FLOWS=1
export DB2WH=9
export DS=6
export CA=11
export DB2OLTP=5
export DODS=1
export SPSS=11
#export WA=10
#export WD=26
export BIGSQL=48
export PA=13
export DEFAULT_VPC_COUNT=40 # For a openshift cluster with 1 master and 3 workers.

## Default values

INCLUDE_WSL="no"
INCLUDE_WKC="no"
INCLUDE_WML="no"
INCLUDE_DV="no"
INCLUDE_WOS="no"
INCLUDE_SPARK="no"
INCLUDE_CDE="no"
INCLUDE_STREAMS="no"
INCLUDE_STREAMS_FLOWS="no"
INCLUDE_DB2WH="no"
INCLUDE_DS="no"
INCLUDE_CA="no"
INCLUDE_DB2OLTP="no"
INCLUDE_DODS="no"
INCLUDE_SPSS="no"
INCLUDE_WA="no"
INCLUDE_WD="no"
INCLUDE_BIGSQL="no"
INCLUDE_PA="no"
INCLUDE_DEFAULT_VPC_COUNT="yes"

export vCPU_check="false"
export vNet_check="false"
export networkInterface_check="false"
export networkSecurityGroups_check="false"
export loadBalancers_check="false"
export publicIpAddresses_check="false"

handle_badusage() {
    echo
    echo "az_resource_quota_validation.sh usage:"
    echo "The following options are must:"
    echo " -appId: the value of appId of the service principal created"
    echo " -password: secret password of the service principal created"
    echo " -tenantId: the value of tenant ID"
    echo " -subscriptionId: the value of subscription ID"
    echo " -region: the region in which the resources will be deployed. eg., eastus"
    echo "The following are optional:"
    echo "  -printlog: set this value to print the logs else it will display. Default set to true. "

    echo

    exit
}

## Block to check the commandline parameters
while [ $# -gt 0 ]; do
    case $1 in
    -appId)
        az_client_id="$2"
        shift
        ;;
    -password)
        az_client_secret="$2"
        shift
        ;;
    -tenantId)
        az_tenant_id="$2"
        shift
        ;;
    -subscriptionId)
        az_subscription_id="$2"
        shift
        ;;
    -region)
        az_location_name="$2"
        shift
        ;;
    -printlog)
        log_output_display="$2"
        shift
        ;;
    -is_wsl)
        INCLUDE_WSL="$2"
        shift
        ;;
    -is_wkc)
        INCLUDE_WKC="$2"
        shift
        ;;
    -is_wml)
        INCLUDE_WML="$2"
        shift
        ;;
    -is_dv)
        INCLUDE_DV="$2"
        shift
        ;;
    -is_wos)
        INCLUDE_WOS="$2"
        shift
        ;;
    -is_spark)
        INCLUDE_SPARK="$2"
        shift
        ;;
    -is_cde)
        INCLUDE_CDE="$2"
        shift
        ;;
    -is_streams)
        INCLUDE_STREAMS="$2"
        shift
        ;;
    -is_streams_flows)
        INCLUDE_STREAMS_FLOWS="$2"
        shift
        ;;
    -is_db2wh)
        INCLUDE_DB2WH="$2"
        shift
        ;;
    -is_ds)
        INCLUDE_DS="$2"
        shift
        ;;
    -is_ca)
        INCLUDE_CA="$2"
        shift
        ;;
    -is_db2oltp)
        INCLUDE_DB2OLTP="$2"
        shift
        ;;
    -is_dods)
        INCLUDE_DODS="$2"
        shift
        ;;
    -is_spss)
        INCLUDE_SPSS="$2"
        shift
        ;;
    -is_bigsql)
        INCLUDE_BIGSQL="$2"
        shift
        ;;
    -is_pa)
        INCLUDE_PA="$2"
        shift
        ;;
    *)
        handle_badusage
        exit
        ;;
    esac
    if [ $# -gt 0 ]; then
        shift
    fi
done

## Setting  the required vcpus based on the service addons selected.
calculate_total_vcpus_required() {
    #WSL
    if [[ $INCLUDE_WSL == "yes" ]]; then
        WSL_VCPU_REQ=$WSL
    else
        WSL_VCPU_REQ=0
    fi
    # WKC
    if [[ $INCLUDE_WKC == "yes" ]]; then
        WKC_VCPU_REQ=$WKC
    else
        WKC_VCPU_REQ=0
    fi
    # WML
    if [[ $INCLUDE_WML == "yes" ]]; then
        WML_VCPU_REQ=$WML
    else
        WML_VCPU_REQ=0
    fi

    # DV
    if [[ $INCLUDE_DV == "yes" ]]; then
        DV_VCPU_REQ=$DV
    else
        DV_VCPU_REQ=0
    fi

    # WOS
    if [[ $INCLUDE_WOS == "yes" ]]; then
        WOS_VCPU_REQ=$WOS
    else
        WOS_VCPU_REQ=0
    fi

    # SPARK
    if [[ $INCLUDE_SPARK == "yes" ]]; then
        SPARK_VCPU_REQ=$SPARK
    else
        SPARK_VCPU_REQ=0
    fi

    # CDE
    if [[ $INCLUDE_CDE == "yes" ]]; then
        CDE_VCPU_REQ=$CDE
    else
        CDE_VCPU_REQ=0
    fi

    # STREAMS
    if [[ $INCLUDE_STREAMS == "yes" ]]; then
        STREAMS_VCPU_REQ=$STREAMS
    else
        STREAMS_VCPU_REQ=0
    fi

    # STREAMS_FLOWS
    if [[ $INCLUDE_STREAMS_FLOWS == "yes" ]]; then
        STREAMS_FLOWS_VCPU_REQ=$STREAMS_FLOWS
    else
        STREAMS_FLOWS_VCPU_REQ=0
    fi

    # DB2WH
    if [[ $INCLUDE_DB2WH == "yes" ]]; then
        DB2WH_VCPU_REQ=$DB2WH
    else
        DB2WH_VCPU_REQ=0
    fi

    # DS
    if [[ $INCLUDE_DS == "yes" ]]; then
        DS_VCPU_REQ=$DS
    else
        DS_VCPU_REQ=0
    fi

    # CA
    if [[ $INCLUDE_CA == "yes" ]]; then
        CA_VCPU_REQ=$CA
    else
        CA_VCPU_REQ=0
    fi

    # DB2OLTP
    if [[ $INCLUDE_DB2OLTP == "yes" ]]; then
        DB2OLTP_VCPU_REQ=$DB2OLTP
    else
        DB2OLTP_VCPU_REQ=0
    fi

    # DODS
    if [[ $INCLUDE_DODS == "yes" ]]; then
        DODS_VCPU_REQ=$DODS
    else
        DODS_VCPU_REQ=0
    fi

    # SPSS
    if [[ $INCLUDE_SPSS == "yes" ]]; then
        SPSS_VCPU_REQ=$SPSS
    else
        SPSS_VCPU_REQ=0
    fi


    # WA
#    if [[ $INCLUDE_WA == "yes" ]]; then
#        WA_VCPU_REQ=$WA
#    else
#        WA_VCPU_REQ=0
#    fi

    # WD
#    if [[ $INCLUDE_WD == "yes" ]]; then
#        WD_VCPU_REQ=$WD
#    else
#        WD_VCPU_REQ=0
#    fi

    # BIGSQL
    if [[ $INCLUDE_BIGSQL == "yes" ]]; then
        BIGSQL_VCPU_REQ=$BIGSQL
    else
        BIGSQL_VCPU_REQ=0
    fi

    # PA
    if [[ $INCLUDE_PA == "yes" ]]; then
        PA_VCPU_REQ=$PA
    else
        PA_VCPU_REQ=0
    fi
    
    total_vcpu_required=$((DEFAULT_VPC_COUNT + WSL_VCPU_REQ + WKC_VCPU_REQ + WML_VCPU_REQ + DV_VCPU_REQ + WOS_VCPU_REQ + SPARK_VCPU_REQ + CDE_VCPU_REQ + STREAMS_VCPU_REQ + STREAMS_FLOWS_VCPU_REQ + DB2WH_VCPU_REQ + DS_VCPU_REQ + CA_VCPU_REQ + DB2OLTP_VCPU_REQ + DODS_VCPU_REQ + SPSS_VCPU_REQ + BIGSQL_VCPU_REQ + PA_VCPU_REQ))
    
    if [[ $log_output_display == "true" ]]; then
    echo "Total vcpu rquired is $total_vcpu_required "
    fi
    
    az_vcpu_quota_required=$total_vcpu_required

}

setvalues() {

    if [[ $log_output_display == "true" ]]; then

        echo -e "\n**************************************************"
        echo " List of values entered"
        echo -e "**************************************************\n"

        echo -e "The client_id entered is : $az_client_id"
        echo -e "The client secret entered is : $az_client_secret"
        echo -e "The TENANT_ID value entered is: $az_tenant_id"
        echo -e "The subscriptionId value entered is : $az_subscription_id"
        echo -e "The location which has been selected is : $az_location_name"
    fi

    ### Getting the access_token using the curl command with the input values entered like client_id, client_secret and tenant_id

    export az_access_token=$(curl -X POST -d "grant_type=client_credentials&client_id=${az_client_id}&client_secret=${az_client_secret}&resource=https%3A%2F%2Fmanagement.azure.com%2F" https://login.microsoftonline.com/$az_tenant_id/oauth2/token 2>/dev/null | python -c "import json,sys;obj=json.load(sys.stdin);print (obj['access_token']);")

    if [[ $log_output_display == "true" ]]; then
        echo -e "\n**************************************************"
        echo " Executing curl command to get the usage data"
        echo -e "**************************************************"
    fi

    export vcpu_limit_output_file=az_vcpu_limit_$az_location_name_$(date -u +"%Y%m%d-%H%M%S").json
    curl -X GET -H "Authorization: Bearer $az_access_token" -H "Content-Type:application/json" -H "Accept:application/json" https://management.azure.com/subscriptions/$az_subscription_id/providers/Microsoft.Compute/locations/$az_location_name/usages?api-version=2019-12-01 2>/dev/null >>$vcpu_limit_output_file

    if [[ $log_output_display == "true" ]]; then

        echo -e "\nThe vCPU usage limit is written into the file : $vcpu_limit_output_file "

        echo -e "\n**************************************************"
        echo " Executing curl command to get the Network data"
        echo -e "**************************************************"
    fi

    export network_limit_output_file=az_network_limit_$az_location_name_$(date -u +"%Y%m%d-%H%M%S").json

    curl -X GET -H "Authorization: Bearer $az_access_token" -H "Content-Type:application/json" -H "Accept:application/json" https://management.azure.com/subscriptions/$az_subscription_id/providers/Microsoft.Network/locations/$az_location_name/usages?api-version=2020-05-01 2>/dev/null >>$network_limit_output_file

    if [[ $log_output_display == "true" ]]; then

        echo -e "\nThe Network usage limit is written into the file : $network_limit_output_file "

        echo -e "\n****************************************************************************************************"
        echo -e " Please find the default resource quota's required"
        echo -e " As per the OCP4.5 documentation for azure, the minimum quota required are as follows:
****************************************************************************************************
Component                     Number of components required by default(minimum)
-----------------             ---------------------------------------------------
vCPU                          40
vNet                          1
Network Interfaces            6
Network security groups       2
Network load balancers        3
Public IP addresses           3
Private IP addresses          7
****************************************************************************************************"
    fi
}
## Setting up the variable for default limit of the resource.

az_vnet_quota_required=1
az_network_interface_quota_required=6
az_network_security_groups_quota_required=2
az_network_loadbalancer_quota_required=3
az_public_ip_address_quota_required=3

## Creating a function to find the available quota:

calculate_available_resource_quota() { 
    quota_name=$1
    quota_string_pattern=$2
    quota_usage_output_json=$3
    quota_required=$4
    test_check=$1_check

    az_quota_limit_temp=$(grep -B6 -A2 "$quota_string_pattern" $quota_usage_output_json)
    az_limit=$(echo "$az_quota_limit_temp" | grep limit | awk '{gsub(/\"|\,/,"",$2)}1' | awk '{print $2}')
    az_current_value=$(echo "$az_quota_limit_temp" | grep currentValue | awk '{gsub(/\"|\,/,"",$2)}1' | awk '{print $2}')
    az_available_quota=$(echo $az_limit $az_current_value | awk '{ print $1 - $2 }')

    # az_available_$quota_name_quota=$az_available_quota
    if [ $az_available_quota -ge $quota_required ]; then
        condition_met="PASSED"

    else
        condition_met="FAILED"

    fi

    #echo -e "Resource name:$quota_name Required:$quota_required Available:$az_available_quota Conditional_check:$condition_met" | column -t -s' '
    printf "%-25s |  %-25s |  %-25s |  %-25s" "$quota_name" "$quota_required" "$az_available_quota" "$condition_met"
    printf "\n"

    if [ $condition_met == "PASSED" ]; then
        return 0
    else
        return 1
    fi
}

## Calculating the available resource quota.:

## Main script starts here

### Function calling starts here:

calculate_total_vcpus_required
setvalues

echo -e " Summary of the resource quota details for the subscriptionId : $az_subscription_id "
echo -e "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
printf "%-25s |  %-25s |  %-25s |  %-25s" "Resource_name" "Required" "Available" "Validation_check"
printf "\n"
printf "%-25s |  %-25s |  %-25s |  %-25s" "-----------------------" "-----------------------" "-----------------------" "-----------------------"
printf "\n"

calculate_available_resource_quota vCPU '"localizedValue": "Total Regional vCPUs"' $vcpu_limit_output_file $az_vcpu_quota_required

if [ $? -ne 1 ]; then
    vCPU_check="true"
else
    vCPU_check="false"
fi

calculate_available_resource_quota vNet '"value": "VirtualNetworks"' $network_limit_output_file $az_vnet_quota_required

if [ $? -ne 1 ]; then
    vNet_check="true"
else
    vNet_check="false"
fi

calculate_available_resource_quota networkInterface '"value": "NetworkInterfaces"' $network_limit_output_file $az_network_interface_quota_required

if [ $? -ne 1 ]; then
    networkInterface_check="true"
else
    networkInterface_check="false"
fi

calculate_available_resource_quota networkSecurityGroups '"value": "NetworkSecurityGroups"' $network_limit_output_file $az_network_security_groups_quota_required

if [ $? -ne 1 ]; then
    networkSecurityGroups_check="true"
else
    networkSecurityGroups_check="false"
fi

calculate_available_resource_quota loadBalancers '"value": "LoadBalancers"' $network_limit_output_file $az_network_loadbalancer_quota_required

if [ $? -ne 1 ]; then
    loadBalancers_check="true"
else
    loadBalancers_check="false"
fi

calculate_available_resource_quota publicIpAddresses '"value": "PublicIPAddresses"' $network_limit_output_file $az_public_ip_address_quota_required

if [ $? -ne 1 ]; then
    publicIpAddresses_check="true"
else
    publicIpAddresses_check="false"
fi

echo -e "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"

# echo -e $vCPU_check
# echo -e $vNet_check
# echo -e $networkInterface_check
# echo -e $networkSecurityGroups_check
# echo -e $loadBalancers_check
# echo -e $publicIpAddresses_check

if [ $vCPU_check == 'true' ] && [ $vNet_check == 'true' ] && [ $networkInterface_check == 'true' ] && [ $networkSecurityGroups_check == 'true' ] && [ $loadBalancers_check == 'true' ] && [ $publicIpAddresses_check == 'true' ]; then
    echo "all pass"
    exit 0
else
    echo "failed"
    exit 1
fi
## End of Script
