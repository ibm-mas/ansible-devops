#!/bin/bash

# Process command line arguments
while [[ $# -gt 0 ]]
do
    key="$1"
    shift
    case $key in
        -n|--namespace)
        NAMESPACE=$1
        shift
        ;;
    esac
done

## 1. Deploy Openshift Pipeline Operator
cat > subscription.yaml <<EOF
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
    name: openshift-pipelines-operator
    namespace: openshift-operators
spec:
    channel:  stable
    name: openshift-pipelines-operator-rh
    source: redhat-operators
    sourceNamespace: openshift-marketplace
EOF

oc apply -f subscription.yaml
echo "Wait for Pipeline operator to be ready"

oc wait --for=condition=Established  crd tasks.tekton.dev  --timeout=30m



# Setup Basic Insall Pipeline
echo "Installing Basic Install Pipeline"
oc new-project ${NAMESPACE}
oc project ${NAMESPACE}

FVT_W3_USERNAME_LOWER=${W3_USERNAME_FVT,,}

# Just incase we're re-using a namespace, cleanup any existing secret
oc delete secret generic pipeline-settings --ignore-not-found=true

# Create settings secret
oc create secret generic pipeline-settings \
# Content of MAS config directory
--from-file=$MAS_CONFIG_DIR/bascfg_masdeps1.yaml \
--from-file=$MAS_CONFIG_DIR/workspace_masdev.yaml -n ${NAMESPACE} \
--from-file=$MAS_CONFIG_DIR/entitlement.lic \
# Entitlement key
--from-literal=ibm_entitlement_key=$IBM_ENTITLEMENT_KEY \
# Access to artifactory for test container images
--from-literal=artifactory_apikey=$ARTIFACTORY_APIKEY_FVT \
--from-literal=artifactory_username=$FVT_W3_USERNAME_LOWER \
# Destination target to write to mongo
--from-literal=devops_mongo_uri=$DEVOPS_MONGO_URI \
# Information about the test target
--from-literal=build_num=$TRAVIS_BUILD_NUMBER \
--from-literal=mas_instance_id=$MAS_INSTANCE_ID \
--from-literal=mas_channel=$MAS_CHANNEL \
--from-literal=build_num=$TRAVIS_BUILD_NUMBER \
# Credentials used in the test
--from-literal=ddp_apikey=$DDP_APIKEY \
--from-literal=partium_username=$PARTIUM_USERNAME \
--from-literal=partium_password=$PARTIUM_PASSWORD

echo "Wait a few minutes to make sure all the Pipeline apis are ready"
sleep 5m
cd pipelines
kustomize edit set namespace ${NAMESPACE} | kustomize build  . | oc apply -f -


# Trigger pipeline
oc create -f ibm-mas-fvt-pipeline-run.yaml
