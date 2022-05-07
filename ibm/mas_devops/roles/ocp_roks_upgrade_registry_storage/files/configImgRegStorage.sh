#!/bin/bash

VOLUME=$1
IR_SIZE=$2

if [[ $? -eq 0 ]]; then
capval=$(ibmcloud sl file volume-detail $VOLUME | awk '$1=="Capacity" {print $3}')
  if [[ $capval < $IR_SIZE ]]; then
     ibmcloud sl file volume-modify $VOLUME --new-size $IR_SIZE --force
     COMPLETE=0
     for i in {1..10}; do
       cap=$(ibmcloud sl file volume-detail $VOLUME | awk '$1=="Capacity" {print $3}')
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
       echo "Before proceeding verify that the Image Registy volume $VOLUME size has been modified to the desired $IR_SIZE GB"
     fi
  else
    echo "Image registry volume already meets the minimum size requirements (i.e. $IR_SIZE GB)"
  fi
else
  echo "The current ibmcloud user does not have the privilege required to modify the volume. Before proceeding with the install, please make sure the registry volume size has been modified"
fi
