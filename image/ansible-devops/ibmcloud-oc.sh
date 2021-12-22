# Install Plugin
echo "Install IBM Cloud plugin"
ibmcloud plugin install container-service
ibmcloud plugin list

# Authenticate
echo "Authenticate in IBM Cloud"
ibmcloud login --apikey ${IBMCLOUD_APIKEY} --no-region --quiet
