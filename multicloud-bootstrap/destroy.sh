#!/bin/bash
#
# This is the destroy script that will call the individual Cloud specific script
#

# Variables
export GIT_REPO_HOME=$(pwd)
CLOUD_TYPE=aws

# Load helper functions
. helper.sh
export -f log
export -f get_mas_creds
export -f retrieve_mas_ca_cert

# Call cloud specific script
chmod +x $CLOUD_TYPE/*.sh
log "===== DEPROVISIONING STARTED ====="
log "Calling cloud specific automation ..."
cd $CLOUD_TYPE
log "Running the undeployment using command: undeploy.sh"
./undeploy.sh
if [[ $? -eq 0 ]]; then
  log "Undeployment successful"
  log "===== DEPROVISIONING COMPLETED ====="
  status=SUCCESS
else
  log "Undeployment failed"
  log "===== DEPROVISIONING FAILED ====="
fi
