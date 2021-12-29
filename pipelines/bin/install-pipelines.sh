#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

SAMPLES_DIR=$(realpath $DIR/../samples)
oc apply -f $SAMPLES_DIR/subscription.yaml

oc get crd tasks.tekton.dev &> /dev/null
LOOKUP_RESULT=$?
while [ "$LOOKUP_RESULT" == "1" ]; do
  echo "Waiting 5s for tasks.tekton.dev CRD to be installed before checking again ..."
  sleep 5
  oc get crd tasks.tekton.dev &> /dev/null
  LOOKUP_RESULT=$?
done

echo "Wait for Pipeline operator to be ready"
oc wait --for=condition=Established  crd tasks.tekton.dev  --timeout=30m

echo "Installation complete"
