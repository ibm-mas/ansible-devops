#!/bin/bash

# -----------------------------------------------------------------------------
# Configure Junit report
# -----------------------------------------------------------------------------
export JUNIT_OUTPUT_DIR=/opt/app-root/ansible/junit/
export JUNIT_HIDE_TASK_ARGUMENTS=true
export JUNIT_TASK_CLASS=true

# -----------------------------------------------------------------------------
# Connect to the local cluster
# -----------------------------------------------------------------------------
export K8S_AUTH_HOST=https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_SERVICE_PORT_HTTPS
export K8S_AUTH_VERIFY_SSL=false
export K8S_AUTH_API_KEY=$(cat /run/secrets/kubernetes.io/serviceaccount/token)


# -----------------------------------------------------------------------------
# Export everything in /workspace/settings
# -----------------------------------------------------------------------------
echo "Export all env vars defined in /workspace/settings"
for file in /workspace/settings/*; do
  if [[ -f $file ]]; then
    echo "Exporting $file"
    # Temporarily turn off glob, otherwise any wildcard characters (*) in the
    # vars will be expanded to matching filenames.
    set -f
    export $(basename $file)="$(cat $file)"
    set +f
  fi
done


# Print out all env vars
# -----------------------------------------------------------------------------
env | sort
