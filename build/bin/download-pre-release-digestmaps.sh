#!/bin/bash

# We can't access the image maps from the case bundles at install time, because we're likely running in
# and environment with limited connectivity, so everything needs to be self-contained.
#
# Soon, we will improve our airgap implemention to not need these seperate digests, they were a
# tactical solution to accelerate airgap delivery.

function download_pre_release_case() {
  bundle_name=$1
  bunndle_version=$2
  inventory_name=$3

  ARTIFACTORY_TOKEN=
  ARTIFACTORY_BASE_URL=https://na.artifactory.swg-devops.com:443/artifactory/wiotp-generic-release/maximoappsuite
  ARTIFACTORY_RESOURCE_URL="${ARTIFACTORY_BASE_URL}/${bundle_name}/${bunndle_version}/${bundle_name}-bundle-${bunndle_version}.tgz"

  echo "Downloading ${ARTIFACTORY_RESOURCE_URL} to downloads/${bundle_name}-bundle-${bunndle_version}.tgz"

  mkdir -p downloads
  if [[ ! -e "downloads/${case_name}-${case_version}.tgz" ]]; then
    curl -H "Authorization: Bearer ${ARTIFACTORY_TOKEN}" "${ARTIFACTORY_RESOURCE_URL}" --output downloads/${bundle_name}-bundle-${bunndle_version}.tgz || exit 1
  fi

  mkdir -p digests/${bundle_name}
  tar -xvf downloads/${bundle_name}-bundle-${bunndle_version}.tgz -C digests/${bundle_name} ${bundle_name}-bundle/case/${bundle_name}/inventory/${inventory_name}/files/image-map.yaml --no-same-owner --strip-components 6
  mv digests/${bundle_name}/image-map.yaml digests/${bundle_name}/${bunndle_version}.yaml
}

# SLS
# -----------------------------------------------------------------------------
download_pre_release_case ibm-sls 3.6.0 ibmSlsSetup

# Truststore Manager
# -----------------------------------------------------------------------------
download_pre_release_case ibm-truststore-mgr 1.5.0 ibmTrustStoreMgrSetup

# MAS Core
# -----------------------------------------------------------------------------
download_pre_release_case ibm-mas 8.10.0 ibmMasSetup

# MAS Assist
# -----------------------------------------------------------------------------
# Not supported for airgap
download_pre_release_case ibm-mas-assist 8.7.0 ibmMasAssistSetup

# MAS HP Utilities
# -----------------------------------------------------------------------------
# Not supported for airgap
download_pre_release_case ibm-mas-hputilities 8.6.0 ibmMasHPUtilitiesSetup

# MAS IoT
# -----------------------------------------------------------------------------
download_pre_release_case ibm-mas-iot 8.7.0 ibmMasIotSetup

# MAS Manage
# -----------------------------------------------------------------------------
download_pre_release_case ibm-mas-manage 8.6.0 ibmMasManageSetup

# MAS Monitor
# -----------------------------------------------------------------------------
download_pre_release_case ibm-mas-monitor 8.10.0 ibmMasMonitorSetup


# MAS Predict
# -----------------------------------------------------------------------------
# Not supported for airgap
download_pre_release_case ibm-mas-predict 8.8.0 ibmMasPredictSetup

# MAS Optimizer
# -----------------------------------------------------------------------------
download_pre_release_case ibm-mas-optimizer 8.4.0 ibmMasOptimizerSetup


# MAS Visual Inspection
# -----------------------------------------------------------------------------
download_pre_release_case ibm-mas-visualinspection 8.8.0 ibmMasVisualInspectionSetup
