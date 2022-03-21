#!/bin/bash

# !!!! INCOMPLETE / WORK IN PROGRESS / USE AT OWN RISK !!!!

# Load common functions
# -----------------------------------------------------------------------------
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
. $DIR/mas-common.sh


function run_pipeline() {
  echo ""
  echo "Deploying via in-cluster Tekton Pipeline"

  # Install pipelines support
  # -----------------------------------------------------------------------------
  bash pipelines/bin/install-pipelines.sh

  # Build Pipeline definitions
  # -----------------------------------------------------------------------------
  if [[ -z "$PIPELINE_VERSION" ]]; then
    read -p 'PIPELINE_VERSION> ' PIPELINE_VERSION
  else
    read -e -p 'PIPELINE_VERSION> ' -i "$PIPELINE_VERSION" PIPELINE_VERSION
  fi
  export VERSION=$PIPELINE_VERSION
  export DEV_MODE=true
  bash pipelines/bin/build-pipelines.sh


  # Install the MAS pipeline definition
  # -----------------------------------------------------------------------------
  oc apply -f pipelines/ibm-mas_devops-clustertasks-$PIPELINE_VERSION.yaml

  oc project mas-sample-pipelines &> /dev/null || oc new-project mas-sample-pipelines
  oc apply -f pipelines/samples/sample-pipelinesettings-roks-donotcommit.yaml


  # Clean up existing secrets
  # -----------------------------------------------------------------------------
  oc delete secret pipeline-additional-configs --ignore-not-found=true
  oc delete secret pipeline-sls-entitlement --ignore-not-found=true


  # Create new secrets
  # -----------------------------------------------------------------------------
  oc create secret generic pipeline-additional-configs --from-file=$MAS_CONFIG_DIR/workspace_masdev.yaml
  oc create secret generic pipeline-sls-entitlement --from-file=$MAS_CONFIG_DIR/entitlement.lic


  # Start pipeline execution
  # -----------------------------------------------------------------------------
  oc apply -f pipelines/samples/sample-pipeline.yaml
  oc create -f pipelines/samples/sample-pipelinerun.yaml
}


case $1 in

  show|show-target)
    show_target
    ;;

  set|set-target)
    (return 0 2>/dev/null) && sourced=yes || sourced=no
    if [[ $sourced == "no" ]]; then
      echo "Error: Use "source $0" to set target environment"
      exit 1
    fi
    set_target
    show_target
    ;;

  run|run-pipeline)
    run_pipeline
    ;;

  *)
    echo "unknown parameter"
    exit 1
    ;;
esac
