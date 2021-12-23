#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

SAMPLES_DIR=$(realpath $DIR/../samples)
oc apply -f $SAMPLES_DIR/subscription.yaml

# TODO: do while STATE != ready
# otherwise the CRD lookup will fail, as the timeout only helps AFTER the CRD initially exists
# STATE=$(oc get subscription  openshift-pipelines-operator -n openshift-operators -o=jsonpath="{.status.state}")

echo "Wait for Pipeline operator to be ready"
oc wait --for=condition=Established  crd tasks.tekton.dev  --timeout=30m

echo "Installation complete"
