#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

oc apply -f $DIR/../samples/subscription.yaml

echo "Wait for Pipeline operator to be ready"
oc wait --for=condition=Established  crd tasks.tekton.dev  --timeout=30m

echo "Installation complete"
