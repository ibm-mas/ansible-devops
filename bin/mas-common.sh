#!/bin/bash

# !!!! INCOMPLETE / WORK IN PROGRESS / USE AT OWN RISK !!!!

# Show Target
# -----------------------------------------------------------------------------
function show_target() {
  echo "IBMCLOUD_APIKEY ........... $IBMCLOUD_APIKEY"
  echo "MAS_INSTANCE_ID ........... $MAS_INSTANCE_ID"
  echo "CLUSTER_NAME .............. $CLUSTER_NAME"
  echo "OCP_VERSION ............... $OCP_VERSION"
  echo "MAS_CONFIG_DIR ............ $MAS_CONFIG_DIR"
  echo "MAS_CATALOG_SOURCE ........ $MAS_CATALOG_SOURCE"
  echo "MAS_CHANNEL ............... $MAS_CHANNEL"

  echo "MAS_ICR_CP ................ $MAS_ICR_CP"
  echo "MAS_ICR_CPOPEN ............ $MAS_ICR_CPOPEN"
  echo "MAS_ENTITLEMENT_USERNAME .. $MAS_ENTITLEMENT_USERNAME"
  echo "MAS_ENTITLEMENT_KEY ....... $MAS_ENTITLEMENT_KEY"

  echo "SLS_ICR_CP ................ $SLS_ICR_CP"
  echo "SLS_ICR_CPOPEN ............ $SLS_ICR_CPOPEN"
  echo "SLS_ENTITLEMENT_USERNAME .. $SLS_ENTITLEMENT_USERNAME"
  echo "SLS_ENTITLEMENT_KEY ....... $SLS_ENTITLEMENT_KEY"
  echo "SLS_LICENSE_ID ............ $SLS_LICENSE_ID"

  echo "UDS_CONTACT_EMAIL ......... $UDS_CONTACT_EMAIL"
  echo "UDS_CONTACT_FIRSTNAME ..... $UDS_CONTACT_FIRSTNAME"
  echo "UDS_CONTACT_LASTNAME ...... $UDS_CONTACT_LASTNAME"
}


# Prompt for confirmation to continue
# -----------------------------------------------------------------------------
confirm() {
  read -r -p "${1:-Proceed? [y/N]} " response
  case "$response" in
    [yY][eE][sS]|[yY])
      true
      ;;
    *)
      false
      ;;
  esac
}
