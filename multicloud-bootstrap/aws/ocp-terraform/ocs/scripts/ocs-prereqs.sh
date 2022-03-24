#!/bin/bash

#OCS Operator will install its components only on nodes labelled for OCS with the key
OCS_NODES=$(oc get nodes --show-labels | grep node-role.kubernetes.io/worker= |cut -d' ' -f1)
for ocsnode in ${OCS_NODES[@]}; do
oc label nodes $ocsnode cluster.ocs.openshift.io/openshift-storage=''
done