#!/bin/bash
#
# This is the async init script that calls the actual init script in the background
#
echo "Starting async deployment ..." > mas-provisioning-asynch.log
./init.sh "$@" > mas-provisioning.log 2>&1 &
echo "Started async deployment, exiting" >> mas-provisioning-asynch.log