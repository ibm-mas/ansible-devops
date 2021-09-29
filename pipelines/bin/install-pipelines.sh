#!/bin/bash
set -e

oc apply -f samples/subscription.yaml

echo "Wait for Pipeline operator to be ready"
oc wait --for=condition=Established  crd tasks.tekton.dev  --timeout=30m

echo "Wait 5 minutes to make sure all the Pipeline APIs are ready"
sleep 5m

echo "Installation complete"
