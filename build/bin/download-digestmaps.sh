#!/bin/bash

# We can't access the image maps from the case bundles at install time, because we're likely running in
# and environment with limited connectivity, so everything needs to be self-contained.
#
# Soon, we will improve our airgap implemention to not need these seperate digests, they were a
# tactical solution to accelerate airgap delivery.

function download_case() {
  case_name=$1
  case_version=$2
  inventory_name=$3

  mkdir -p downloads
  if [[ ! -e "downloads/${case_name}-${case_version}.tgz" ]]; then
    wget -k https://github.com/IBM/cloud-pak/blob/master/repo/case/${case_name}/${case_version}/${case_name}-${case_version}.tgz?raw=true -O downloads/${case_name}-${case_version}.tgz || exit 1
  fi

  mkdir -p digests/${case_name}
  tar -xvf downloads/${case_name}-${case_version}.tgz -C digests/${case_name} ${case_name}/inventory/${inventory_name}/files/image-map.yaml --strip-components 4
  mv digests/${case_name}/image-map.yaml digests/${case_name}/${case_version}.yaml
}

# SLS
# -----------------------------------------------------------------------------
#download_case ibm-sls 3.5.0 ibmSlsSetup

# Truststore Manager
# -----------------------------------------------------------------------------
download_case ibm-truststore-mgr 1.4.0 ibmTrustStoreMgrSetup

# MAS Core
# -----------------------------------------------------------------------------
download_case ibm-mas 8.8.3 ibmMasSetup
download_case ibm-mas 8.9.0 ibmMasSetup

# MAS Assist
# -----------------------------------------------------------------------------
# Not supported for airgap
# download_case ibm-mas-assist 8.5.0 ibmMasAssistSetup

# MAS HP Utilities
# -----------------------------------------------------------------------------
# Not supported for airgap
# download_case ibm-mas-hputilities 8.4.0 ibmMasHPUtilitiesSetup

# MAS IoT
# -----------------------------------------------------------------------------
download_case ibm-mas-iot 8.5.3 ibmMasIotSetup
download_case ibm-mas-iot 8.6.0 ibmMasIotSetup

# MAS Manage
# -----------------------------------------------------------------------------
download_case ibm-mas-manage 8.4.3 ibmMasManageSetup
download_case ibm-mas-manage 8.5.0 ibmMasManageSetup

# MAS Monitor
# -----------------------------------------------------------------------------
download_case ibm-mas-monitor 8.9.0 ibmMasMonitorSetup
download_case ibm-mas-monitor 8.8.2 ibmMasMonitorSetup

# MAS Predict
# -----------------------------------------------------------------------------
# Not supported for airgap
# download_case ibm-mas-predict 8.6.0 ibmMasPredictSetup

# MAS Optimizer
# -----------------------------------------------------------------------------
download_case ibm-mas-optimizer 8.2.2 ibmMasOptimizerSetup
download_case ibm-mas-optimizer 8.3.0 ibmMasOptimizerSetup

# MAS Visual Inspection
# -----------------------------------------------------------------------------
download_case ibm-mas-visualinspection 8.7.0 ibmMasVisualInspectionSetup
