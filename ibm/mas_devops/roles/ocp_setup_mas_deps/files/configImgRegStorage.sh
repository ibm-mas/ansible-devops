#!/bin/bash

# Image Registry volume size (GB)
IR_SIZE=400

# Login to the target OCP cluster
if ! oc whoami > /dev/null 2>&1; then
    echo "Logging in to openshift cluster ..."
    oc login -u apikey -p $IBMCLOUD_API_KEY || { echo "failed to login to cluster, check your IBMCLOUD_API_KEY=$IBMCLOUD_API_KEY" ; exit 1; }
else
    echo "Already logged in to openshift cluster."
fi

#Increase storage for internal image registry
registry_pv=$(oc get pvc -n openshift-image-registry | grep "image-registry-storage" | awk '{print $3}')

if [ "$registry_pv" == "" ] ; then
  echo "PVC for image-registry-storage was not found, be sure you are logged into the cluster before running this script"
  exit 1
fi

volid=$(oc describe pv $registry_pv -n openshift-image-registry | grep volumeId)
IFS='='
read -ra vol <<< "$volid"
volume=${vol[1]}

echo
echo "Openshift image registry volume id is $volume, pvc id is $registry_pv"

echo
echo "Openshift image registry volume details..."
ibmcloud sl file volume-detail $volume ; rc=$?
if [ "$rc" != "0" ] ; then
  echo "Could not get details for volume $volume, be sure your are logged into the IBM cloud account that matches the OCP cluster"
  exit 1
fi

if [[ $? -eq 0 ]]; then
capval=$(ibmcloud sl file volume-detail $volume | awk '$1=="Capacity" {print $3}')
  if [[ $capval < $IR_SIZE ]]; then
     ibmcloud sl file volume-modify $volume --new-size $IR_SIZE --force
     COMPLETE=0
     for i in {1..10}; do
       cap=$(ibmcloud sl file volume-detail $volume | awk '$1=="Capacity" {print $3}')
       if [[ $cap == $IR_SIZE ]]; then
         echo "Image registry Volume is modified"
         COMPLETE=1
         break
       else
         sleep 30
       fi
       echo "Looks like it is taking time to reflect the updated size for Image Registry volume (check count $i)"
     done
     if [ "$COMPLETE" == "0" ] ; then
       echo "Before proceeding verify that the Image Registy volume $volume size has been modified to the desired $IR_SIZE GB"
     fi
  else
    echo "Image registry volume already meets the minimum size requirements (i.e. $IR_SIZE GB)"
  fi
else
  echo "The current ibmcloud user does not have the privilege required to modify the volume. Before proceeding with the install, please make sure the registry volume size has been modified"
fi
