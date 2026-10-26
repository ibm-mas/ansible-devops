#!/usr/bin/env bash

# ---------------------------------------------------------------------------
# This script must be sourced by any front-facing script/tool that requires
# files in specific profile folders.
# ---------------------------------------------------------------------------

CONFIG_DIR="$(dirname "${BASH_SOURCE[0]}")"
ENV_DIR="${CONFIG_DIR}/env"
CURRENT_CONFIG_FILE="${CONFIG_DIR}/.current.config"

SETUP_ROOT=$(cd "${CONFIG_DIR}/../.." && pwd)
export SETUP_ROOT

# ---------------------------------------------------------------------------
# Read the current setup profile name in the file .config/.current.config
# unless $CURRENT_PROFILE is defined in the environment.
# ---------------------------------------------------------------------------
[ ! -f "$CURRENT_CONFIG_FILE" ] && echo "Current configuration file ${CURRENT_CONFIG_FILE} does not exist." && exit 1

if [ -z "$CURRENT_PROFILE" ]; then
  CURRENT_PROFILE=$(< "${CURRENT_CONFIG_FILE}" grep -Ev '^#|^$' | xargs)
fi

# ---------------------------------------------------------------------------
# Used by all setups and tools
# ---------------------------------------------------------------------------
export CURRENT_PROFILE

# ---------------------------------------------------------------------------
# Source the env/<profile>.sh script to pick up any setup profile-specific
# properties. That script will also source its parent profile script.
# ---------------------------------------------------------------------------
ENV_CONFIG="${ENV_DIR}/${CURRENT_PROFILE}.sh"
[ ! -f "$ENV_CONFIG" ] && echo "Environment configuration file ${ENV_CONFIG} does not exist." && exit 1

# shellcheck disable=SC1090
. "$ENV_CONFIG"
