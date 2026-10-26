#!/usr/bin/env bash

# shellcheck disable=SC1091
ENV_DIR="$(dirname "${BASH_SOURCE[0]}")"
. "${ENV_DIR}/common.sh"

export PRODUCT_NAME="ArcGIS Enterprise ${PRODUCT_VERSION} on Kubernetes"
export PRODUCT_NAME_SHORT="ArcGIS Enterprise on Kubernetes"

SETUP_ROOT_DIR=$(cd "${ENV_DIR}/../../.." && pwd)
ENTERPRISE_ROOT=$(cd "${SETUP_ROOT_DIR}/.install/enterprise" && pwd)

# ---------------------------------------------------------------------------
# Enterprise
# ---------------------------------------------------------------------------
export DIR_ARCGIS_MANAGER=${ENTERPRISE_ROOT}/arcgis-manager
export DIR_HELP=${ENTERPRISE_ROOT}/help
