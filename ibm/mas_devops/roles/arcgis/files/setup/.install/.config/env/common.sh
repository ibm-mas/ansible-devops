#!/usr/bin/env bash

export PRODUCT_VERSION="12.0"

ENV_DIR="$(dirname "${BASH_SOURCE[0]}")"
INSTALL_ROOT="$(cd "${ENV_DIR}/../../" && pwd)"

# ---------------------------------------------------------------------------
# Base dirs
# ---------------------------------------------------------------------------
export INSTALL_COMMON="${INSTALL_ROOT}/common"
export INSTALL_ENTERPRISE="${INSTALL_ROOT}/enterprise"
export INSTALL_FRONTIER="${INSTALL_ROOT}/frontier"
export INSTALL_INTERNAL="${INSTALL_ROOT}/enterprise.internal"

# ---------------------------------------------------------------------------
# Common
# ---------------------------------------------------------------------------
export DIR_ARCGIS_ENTERPRISE=${INSTALL_COMMON}/arcgis-enterprise
export DIR_ELASTIC=${INSTALL_COMMON}/elastic
export DIR_INGRESS_CONTROLLER=${INSTALL_COMMON}/ingress-controller
export DIR_PROMETHEUS=${INSTALL_COMMON}/prometheus
export DIR_RABBITMQ=${INSTALL_COMMON}/rabbitmq
export DIR_COMMON_RESOURCES=${INSTALL_COMMON}/resources
export DIR_COMMON_SCRIPTS=${DIR_COMMON_RESOURCES}/scripts
export DIR_COMMON_TEMPLATES=${DIR_COMMON_RESOURCES}/templates

# ---------------------------------------------------------------------------
# File overrides
#
# If a file ever needs to be duplicated in different setups then add it here
# then override it in the appropriate env/xxxxx.sh script.
# ---------------------------------------------------------------------------
export FILE_CONFIGURE_USER=${DIR_COMMON_SCRIPTS}/configure_user.sh
export FILE_CONFIGURE_PROPERTIES_TEMPLATE=${DIR_COMMON_TEMPLATES}/configure.properties.template
export FILE_DEPLOY_PROPERTIES_TEMPLATE=${DIR_COMMON_TEMPLATES}/deploy.properties.template
