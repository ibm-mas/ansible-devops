#!/bin/bash
export K8S_AUTH_HOST=https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_SERVICE_PORT_HTTPS
export K8S_AUTH_VERIFY_SSL=false
export K8S_AUTH_API_KEY=$(cat /run/secrets/kubernetes.io/serviceaccount/token)


# Information about what we are testing
# -------------------------------------------------------------------------
export MAS_INSTANCE_ID=$(cat /workspace/settings/mas_instance_id)
export MAS_CHANNEL=$(cat /workspace/settings/mas_channel)
export TRAVIS_BUILD_NUMBER=$(cat /workspace/settings/build_num)

# Credentials to access the FVT container images
# -------------------------------------------------------------------------
export W3_USERNAME=$(cat /workspace/settings/artifactory_username)
export ARTIFACTORY_APIKEY=$(cat /workspace/settings/artifactory_apikey)

# Destination for FVT results
# -------------------------------------------------------------------------
export DEVOPS_MONGO_URI=$(cat /workspace/settings/devops_mongo_uri)

# Credentials used by tests
# -------------------------------------------------------------------------
export DDP_APIKEY=$(cat /workspace/settings/ddp_apikey)
export PARTIUM_USERNAME=$(cat /workspace/settings/partium_username)
export PARTIUM_PASSWORD=$(cat /workspace/settings/partium_password)
