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


echo "Wait 5 minutes to make sure all the Pipeline APIs are ready"
sleep 5m

cd pipelines
kustomize build  . | oc apply -f -


# Trigger pipeline
oc create -f ibm-mas-fvt-pipeline-run.yaml
