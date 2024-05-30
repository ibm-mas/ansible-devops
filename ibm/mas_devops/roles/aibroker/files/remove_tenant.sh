#!/bin/bash

TENANT=$1

if [ -z ${TENANT} ]; then
  echo "❌ Missing tenant name"
  exit 1
fi

# Verify no inference servers are running
if [ ! -z "$(oc get isvc -n ${TENANT} -oname)" ] ||  [ ! -z "$(oc get ig -n ${TENANT} -oname)" ]; then
  echo "❗ Please remove all models before deleting kmodels"
  exit 1
fi

# Delete tenant resources
oc delete cm monitor-config -n ${TENANT}
oc delete cm connector-config -n ${TENANT}
oc delete sa km-s3-sa -n ${TENANT}
oc delete secret km-s3-secret -n ${TENANT}
oc delete secret regcred -n ${TENANT}

# Delete tenant namesapce
oc delete ns ${TENANT}

echo "Tenant was deleted"
