#!/bin/bash

# echo "Usage ./create_apikey.sh tenant_name_in_lower_case"

TENANT=$1
AIBROKER=$2
WATSONXAI_APIKEY=$3
WATSONXAI_URL=$4
WATSONXAI_PROJECT_ID=$5

# if [ -z ${TENANT} ]; then
#     #echo "❌ Missing tenant name"
#     echo "using default tenant name=aiserviceuser"
#     TENANT='aiserviceuser'
#     #exit 1
# fi

# if [[ "$TENANT" =~ [[:upper:]] ]]; then
#     echo "❌ uppercase character found"
#     exit 1
# fi

# echo -n "Enter watsonxai apikey > "
# read watsonxaiapikey
# echo "You entered: $watsonxaiapikey"

# echo -n "Enter watsonxai url > "
# read watsonxai_url
# echo "You entered: $watsonxai_url"

# echo -n "Enter watsonxai project id > "
# read watsonxai_project_id
# echo "You entered: $watsonxai_project_id"

# echo "TENANT = ${TENANT}"
# echo "watsonxaiapikey =${watsonxaiapikey}"
# echo "watsonxai_url =${watsonxai_url}"
# echo "watsonxai_project_id =${watsonxai_project_id}"

# if [ -z ${TENANT} ]; then
#     #echo "❌ Missing tenant name"
#     echo "using default tenant name=aiserviceuser"
#     TENANT='aiserviceuser'
#     #exit 1
# fi

# if [ -z ${watsonxaiapikey} ]; then
#     echo "❌ Missing watsonxai apikey"
#     exit 1
# fi

# if [ -z ${watsonxai_project_id} ]; then
#     echo "❌ Missing watsonxai project id"
#     exit 1
# fi

# Add testing code to make sure the watsonx apikey works
# python3 ../roles/aiservice/files/access_wx.py $WATSONXAI_APIKEY $WATSONXAI_URL $WATSONXAI_PROJECT_ID
if [ $? -eq 0 ]; then
    echo "Successfully executed script"
    echo "Creating watsonx secret in k8s"
    oc create secret generic ${TENANT}----wx-secret -n ${AIBROKER} \
        --from-literal=wx_apikey=${WATSONXAI_APIKEY} \
        --from-literal=wx_url=${WATSONXAI_URL} \
        --from-literal=wx_project_id=${WATSONXAI_PROJECT_ID}
    echo "Created watsonx secret successfully in k8s."
else
    # Redirect stdout from echo command to stderr.
    echo "Script exited with error. The secret for the watsonx is not created in k8s. Please fix the error and rerun the script." >&2
fi
