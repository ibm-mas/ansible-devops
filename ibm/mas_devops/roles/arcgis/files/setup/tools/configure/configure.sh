#!/usr/bin/env bash

# shellcheck disable=SC1090

PROG=$(basename "$0")
CWD=$(cd "$(dirname "$0")" && pwd)

K8S_NAMESPACE=${K8S_NAMESPACE:-arcgis}
OS="$(uname -s)"

# Defined after sourcing configure.properties
ARCGIS_SITENAME="arcgis"
ENV_VARIABLES_SECRET_NAME="${ARCGIS_SITENAME}-env-variables"

# These values are picked up via cluster resources
SITE_CONTEXT=""
ORGANIZATION_HOST=""
SITE_URL=""

# Set up environment variables
CONFIG_DIR=$(cd "${CWD}/../../.install/.config" && pwd)
SETUP_CONFIG="${CONFIG_DIR}/setup-config.sh"
[ ! -f "$SETUP_CONFIG" ] && {
  echo "Setup configuration file not found: $SETUP_CONFIG"
  exit 1
}
. "$SETUP_CONFIG"

RESOURCES=${DIR_COMMON_RESOURCES}
COMMON="${RESOURCES}/scripts/common.sh"
TEMP_DIR="${RESOURCES}/tmp"
CONFIGURE_PROPERTIES_TEMPLATE="${FILE_CONFIGURE_PROPERTIES_TEMPLATE}"
CONFIGURE_PROPERTIES=""
STORAGE_JSON_TEMPLATE="${RESOURCES}/templates/storage.json.template"
STORAGE_JSON="${TEMP_DIR}/configure.storage.json"
USER_MANAGED_DATASTORES=""

FMT="cat"
DEBUG_LOG="${TEMP_DIR}/configure.debug.$$.log"

declare -a MESSAGE_LIST=()
declare -a WARNING_LIST=()
WARNINGS_FILE="${TEMP_DIR}/configure.warnings.log"

declare -a EMPTY_PROPERTY_EXCEPTIONS=()

# Flags
SILENT=false
VERBOSE=false
DEBUG=false
HELM_DEPLOY=${HELM_DEPLOY:-false}

# wait flags
SLEEP_SECONDS=10
MAX_MINUTES=30
ABORTED=false

# Flags for checking Pending pods/PVCs
SECONDS=0
PVC_CHECK_TIMEOUT=300
PVC_CHECK_CHECKED=false

VERSION_TAG=""

# Vars used for user input via config files, json, etc
USER_MANAGED_DATASTORES_JSON=""
CLOUD_CONFIG_JSON=""
PLACEMENT_POLICIES_CONFIG_JSON=""

# The maximum time in seconds that curl will
# take to complete an operation.
CURL_MAX_TIME=5

CURL_FLAGS="-s -k"

# Max number of minutes wait_for_url() will attempt
# connections before giving up.
URL_WAIT_TIMEOUT=2

# To pick up local binaries
export PATH="${RESOURCES}/bin/${OS}:${PATH}"
export LD_LIBRARY_PATH="${RESOURCES}/lib/${OS}:${LD_LIBRARY_PATH}"

if [ -f "${RESOURCES}/ssl/${OS}/openssl.cnf" ]; then
  export OPENSSL_CONF=${RESOURCES}/ssl/${OS}/openssl.cnf
fi



usage()
{
  local template="$CONFIGURE_PROPERTIES_TEMPLATE"

  cat <<EOF

  This script provides an alternate method for creating an ArcGIS Enterprise
  organization. It uses a properties file with defined values such as
  administrator credentials, a license file, log settings, and so on. 
  A properties file template is available here:

    ${template}

  It performs three tasks:

  * Verifies configure.properties values are valid
  * Creates storage JSON based on provided storage properties
  * Creates Enterprise Organization

  USAGE: % ./${PROG} [options] -f user_properties>

  OPTIONS:

    -h                      - Usage
    -f <properties_file>    - Use specified properties file (REQUIRED)
    -v                      - Show verbose output
    -s or -y                - Create organization without prompting for input
    -u <user_datastores>    - Specify user-managed data stores JSON file

  EXAMPLES:

  * Configure using specified properties file

      % ./${PROG} -f my.properties

  * Configure silently

      % ./${PROG} -s -f my.properties

  * Configure with user-managed data stores

      % ./${PROG} -f my.properties -u /path/to/my_data_stores.json

  To learn more, see the "Create an organization" documentation.

EOF
  exit 0
}

init_temp_dir()
{
  [ "$HELM_DEPLOY" = true ] && {
    TEMP_DIR="/arcgistmp"
    STORAGE_JSON="${TEMP_DIR}/configure.storage.json"
    DEBUG_LOG="${TEMP_DIR}/configure.debug.$$.log"
  }
}

cleanup()
{
  [ -f "$STORAGE_JSON" ] && rm -f "$STORAGE_JSON"
  [ "$DEBUG" = false ] && rm -f "${TEMP_DIR}"/configure.*
}

banner()
{
  draw_line
  text_bold
  if [ -n "$VERSION_TAG" ]; then
    print_center "Configure ${PRODUCT_NAME} (${VERSION_TAG})"
  else
    print_center "Configure ${PRODUCT_NAME}"
  fi
  text_normal
  draw_line
}

fail()
{
  echo ""
  printf "%sERROR%s: " "${fg_red}" "${txt_reset}"
  printf "$1" | fmt
  echo ""
  exit 1
}

info_exit()
{
  echo ""
  printf "%sINFO%s: " "${fg_cyan}" "${txt_reset}" 
  printf "$1" | fmt
  echo ""
  exit 0
}

exit_msg()
{
  echo ""
  echo "$1" | fmt
  echo ""
  exit 0
}

echo_v()
{
  local masked_pw="$ADMIN_PASSWORD"
  if [ "$HELM_DEPLOY" = false ]; then
    masked_pw=$(get_decrypted_password)
  fi

  [ "$VERBOSE" = true ] || [ "$DEBUG" = true ] && mask "$1" "$masked_pw"
}

printf_v()
{
  [ "$VERBOSE" = true ] || [ "$DEBUG" = true ] && printf "$@"
}

debug()
{
  [ "$DEBUG" = false ] && return

  local func="$1"
  local now=$(date +"%Y-%m-%d %H:%M:%S" | xargs)

  shift
  echo "----------------------------------------------------" >> "$DEBUG_LOG"
  echo "${func} ${now}:" >> "$DEBUG_LOG"
  echo -e "$@" >> "$DEBUG_LOG"
  echo "----------------------------------------------------" >> "$DEBUG_LOG"
}

clear_current_line()
{
  if [ "$HAS_TTY" = true ]; then
    echo -en "\033[2K\r" 
  else
    printf "%65s\r" '' ""
  fi
}

get_version_tag()
{
  local tag=$(get_env_variable_secret_value "VERSION_TAG")

  [ -n "$tag" ] && VERSION_TAG="$tag"
}


# ----------------------------------------------
# Sanity check
# ----------------------------------------------

sanity_check()
{
  [ ! -d "${RESOURCES}" ] && fail "Resources folder not found: ${RESOURCES}"
  [ ! -d "${TEMP_DIR}" ] && fail "Local tmp dir not found: ${TEMP_DIR}"
  [ ! -f "${COMMON}" ] && fail "Common script not found: ${COMMON}"
  [ ! -f "${CONFIGURE_PROPERTIES_TEMPLATE}" ] && fail "Configure properties template not found: ${CONFIGURE_PROPERTIES_TEMPLATE}"
  [ ! -f "${STORAGE_JSON_TEMPLATE}" ] && fail "Storage json template not found: ${STORAGE_JSON_TEMPLATE}"
  which fmt > /dev/null 2>&1
  [ $? -eq 0 ] && FMT="fmt"
}

validation_check()
{
  header "Running Validation Checks..."
  check_os
  check_bash_version
  check_openssl_version
  check_configure_properties
  check_curl_install
  check_jq
  read_properties_file
  check_properties_vars
  validate_encryption
  validate_architecture_profile
  validate_storage_class_names
  validate_cloud_config_filename
  validate_placement_policies_filename
  validate_cloud_config_secret
  validate_portal_federation
}

check_os()
{
  local script="${RESOURCES}/scripts/os-check.sh"
  local output=""

  [ ! -f "$script" ] && fail "OS check script not found: $script"

  echo "Checking operating system..." 

  output=$($script)

  if [ $? -eq 99 ]; then
    echo "WARNING: ${output}" | fmt -s -w 79
  fi
}

check_bash_version()
{
  local result=$STATUS_SUCCESS
  local script="${RESOURCES}/scripts/os-check.sh"
  local major_version="${BASH_VERSION%%.*}"
  local required_major_version=4

  echo "Checking bash version"

  if [ "$major_version" -lt "$required_major_version" ]; then
    fail "Your Bash version is ${BASH_VERSION}. This script requires Bash version ${required_major_version}.x or higher."
  fi
}

check_curl_install()
{
  which curl > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    fail "The curl utility was not found."
  fi
}

check_jq()
{
  jq --version > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    fail "The jq JSON parser was not found or failed to run."
  fi
}

# ----------------------------------------------
# Properties file handling
# ----------------------------------------------
check_openssl_version()
{
  [ "$(uname -s)" != "Darwin" ] && return

  # Should be "openssl" or "libressl"
  local dist=$(openssl version -v | awk '{print $1}' | tr '[A-Z]' '[a-z]')
  local vers=$(openssl version -v | awk '{print $2}')

  # Convert "1.1.1k" to "111" or "2.9.1" to "291"
  local vers_stripped=$(echo "$vers" | sed 's/[^0-9]*//g' | sed 's/\.//g')

  [ "$dist" = "openssl" ] && return

  echo "Checking OpenSSL version..."

  if [ $vers_stripped -lt 291 ]; then
    echo ""
    printf "%sERROR%s: LibreSSL version $vers is too low.  This version does not support\n" "${fg_red}" "${txt_reset}"
    printf "the -pbkdf2 flag.  The version of Libressl needs to be at least 2.9.1\n\n"
    printf "Run 'brew upgrade libressl' to upgrade your version of LibreSSL.\n" 
    echo ""
    exit 1
  fi
}

check_configure_properties()
{
  if [ ! -f "${CONFIGURE_PROPERTIES}" ]; then
    usage
    
    exit 0
  fi
}

validate_security_question_index()
{
  local -i value=$1
  local ret=0

  if [ $value -lt 1 ] || [ $value -gt 14 ]; then
    ret=1
  fi 

  [ $ret -eq 0 ]
}

validate_architecture_profile()
{
  echo "Checking architecture profile..."

  [ -z "$SYSTEM_ARCH_PROFILE" ] && fail "You need to set SYSTEM_ARCH_PROFILE in your properties file."

  if [ "$SYSTEM_ARCH_PROFILE" != "development" ] &&
     [ "$SYSTEM_ARCH_PROFILE" != "standard-availability" ] &&
     [ "$SYSTEM_ARCH_PROFILE" != "enhanced-availability" ]; then
    fail "Your SYSTEM_ARCH_PROFILE needs to be set to 'development', 'standard-availability' or 'enhanced-availability'."
  fi
}

validate_encryption()
{
  [ "$HELM_DEPLOY" = true ] && return

  [ -z "${ENCRYPTION_KEYFILE}" ] && fail "Variable ENCRYPTION_KEYFILE is not defined."
  [ ! -f "${ENCRYPTION_KEYFILE}" ] && fail "Encryption keyfile not found: ${ENCRYPTION_KEYFILE}"

  local pw="$ADMIN_PASSWORD"

  is_portal_federation_enabled && pw="$PORTAL_ADMIN_PASSWORD"

  if ! can_decrypt_aes256_string "$pw" "$ENCRYPTION_KEYFILE" ; then
    echo ""
    printf "%sERROR%s: Failed to decrypt admin password.\n" "${fg_red}" "${txt_reset}"
    echo ""
    echo "Create an encrypted password using the following command:"
    echo ""
    echo "    % echo \"my.admin.password\" | ../password-encrypt/password-encrypt.sh -f \"${ENCRYPTION_KEYFILE}\""
    echo ""
    echo "Then set ADMIN_PASSWORD or PORTAL_ADMIN_PASSWORD to that encrypted value."
    echo ""
    exit 1
  fi
}

# NOTE: This check requires cluster admin privileges.
validate_storage_class_names()
{
  local failed_storage_class_names=()

  # For issue #12367
  [ "$HELM_DEPLOY" = true ] && return

  # Don't bother validating if we can't list storage classes
  kubectl auth can-i list storageclasses --all-namespaces > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo "Skipping storage class validation."
    return
  fi

  echo "Checking storage class names..."

  while IFS= read line
  do
    local var=$(echo "$line" | cut -d= -f1)
    local val=${!var}

    if [[ $var == *_STORAGE_CLASS* ]]; then

      # Don't validate empty properties
      [ -z "$val" ] && continue

      if ! is_storage_class_valid "$val" ; then
        failed_storage_class_names+=("${var}=\"$val\"")
      fi
    fi
  done < <(< "${CONFIGURE_PROPERTIES}" grep -Ev "^#|^$")

  if [ ${#failed_storage_class_names[@]} -gt 0 ]; then
    echo ""
    echo "The following storage class names were not found or are invalid:"
    echo ""

    for i in ${failed_storage_class_names[@]}
    do
      echo "    ${i}"
    done
    fail "Storage class name validation failed."
  fi
}

validate_cloud_config_filename()
{
  [ -z "$CLOUD_CONFIG_JSON_FILENAME" ] && return

  [ ! -f "$CLOUD_CONFIG_JSON_FILENAME" ] && fail "Cloud-config filename in CLOUD_CONFIG_JSON_FILENAME not found: $CLOUD_CONFIG_JSON_FILENAME"
}

validate_placement_policies_filename()
{
  [ -z "$PLACEMENT_POLICIES_CONFIG_FILENAME" ] && return

  [ ! -f "$PLACEMENT_POLICIES_CONFIG_FILENAME" ] && fail "Placement polices filename in PLACEMENT_POLICIES_CONFIG_FILENAME not found: $PLACEMENT_POLICIES_CONFIG_FILENAME"
}

validate_cloud_config_secret()
{
  [ -z "$CLOUD_CONFIG_SECRET_NAME" ] && return

  echo "Checking cloud config secret name..."

  kubectl get secret ${CLOUD_CONFIG_SECRET_NAME} -n ${K8S_NAMESPACE} > /dev/null 2>&1

  if [ $? -ne 0 ]; then
    echo ""
    echo "The property CLOUD_CONFIG_SECRET_NAME is set to $CLOUD_CONFIG_SECRET_NAME but that secret"
    echo "was not be found in the ${K8S_NAMESPACE} namespace."
    fail "Cloud config secret name validation failed."
  fi

  local json=""
  json=$(kubectl get secret ${CLOUD_CONFIG_SECRET_NAME} -n ${K8S_NAMESPACE} -o 'go-template={{ .data.cloudConfig | base64decode }}')

  echo "$json" | jq -rc > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo ""
    echo "The cloud config secret data was not recognized as json or there was a parsing error."
    fail "Failed to process json data from cloud config secret ${CLOUD_CONFIG_SECRET_NAME}"
  fi
}

validate_portal_federation()
{
  ! is_portal_federation_enabled && return

  echo "Checking deploy type..."

  if is_enterprise_deployment ; then
    warning "The configure properties PRIVATE_PORTAL_URL and PORTAL_URL are set but the deploy property DEPLOY_TYPE is either unset or set to 'enterprise'."
  fi

  if [ -z "$PORTAL_ADMIN_USERNAME" ] || [ -z "$PORTAL_ADMIN_PASSWORD" ]; then
    warning "You need to set the configure properties PORTAL_ADMIN_USERNAME and PORTAL_ADMIN_PASSWORD when running configure with portal federation enabled."
  fi
}

create_empty_property_exceptions()
{
  # Properties that can be null or ""
  local exceptions=(
    "REGISTERED_FOLDER_PATHS"
    "LOG_SETTING"
    "CLOUD_CONFIG_JSON_FILENAME"
    "CLOUD_CONFIG_SECRET_NAME"
    "LOG_RETENTION_MAX_DAYS"
    "ARCGIS_ENTERPRISE_FQDN"
    "RELATIONAL_STORAGE_TYPE"
    "RELATIONAL_STORAGE_SIZE"
    "RELATIONAL_STORAGE_CLASS"
    "CONTEXT"
    "PLACEMENT_POLICIES_CONFIG_FILENAME"
  )

  local federated_exceptions=(
    "ADMIN_USERNAME"
    "ADMIN_PASSWORD"
    "ADMIN_EMAIL"
    "ADMIN_FIRST_NAME"
    "ADMIN_LAST_NAME"
    "SECURITY_QUESTION_INDEX"
    "SECURITY_QUESTION_ANSWER"
  )

  if is_portal_federation_enabled ; then
    exceptions+=("${federated_exceptions[@]}")
  fi

  # Make storage class name exception when set to "STATIC"
  local storage_exceptions=()

  # Will fill in storage_exceptions
  get_ignored_storage_class_properties storage_exceptions

  exceptions+=("${storage_exceptions[@]}")

  EMPTY_PROPERTY_EXCEPTIONS=("${exceptions[@]}")

  echo_v "  Empty property exceptions:"
  for prop in ${EMPTY_PROPERTY_EXCEPTIONS[@]}
  do
    echo_v "    $prop"
  done
}

# Helper for check_properties_vars()
is_property_exception()
{
  local property="$1"

  # Check explicit property exceptions
  for p in ${EMPTY_PROPERTY_EXCEPTIONS[@]}
  do
    if [ "$p" = "$property" ]; then
      true
      return
    fi
  done

  # Helm doesn't use the ENCRYPTION_KEYFILE
  if [ "$property" = "ENCRYPTION_KEYFILE" ] && [ "$HELM_DEPLOY" = true ]; then
    true
    return
  fi

  # Ignore empty labels.  They will be validated separately
  if [[ $property =~ _LABEL_ ]]; then
    true
    return
  fi

  # The OBJECT_STORAGE vars can be null if CLOUD_CONFIG_JSON_FILENAME is used
  if [ -n "$CLOUD_CONFIG_JSON_FILENAME" ]; then
    if [[ $property == OBJECT_STORAGE_* ]]; then
      true
      return
    fi
  fi

  false
}

check_properties_vars()
{
  local -a unset_vars=()
  local -a errors=()

  echo "Checking property values..."

  # Create a list of allowed empty properties
  create_empty_property_exceptions

  # Check for unset variables
  while IFS= read line
  do
    local var=$(echo "$line" | cut -d= -f1)
    local val=${!var}

    is_property_exception "$var" && continue

    [ -z "$val" ] && unset_vars+=("$var")
  done < <(< "${CONFIGURE_PROPERTIES}" grep -Ev "^#|^$")

  if [ ${#unset_vars} -gt 0 ]; then
    echo ""
    echo "The following variables need to be set:"
    echo ""
    for v in "${unset_vars[@]}"
    do
      echo "    - $v"
    done
    echo ""
    exit 1
  fi

  # Validate some known variables
  [ ! -f "$LICENSE_FILE" ] && errors+=("License file not found: $LICENSE_FILE")

  # Check "SECURITY_QUESTION_INDEX
  if ! validate_security_question_index "$SECURITY_QUESTION_INDEX" ; then
    errors+=("SECURITY_QUESTION_INDEX should be an integer between 1 and 14")
  fi

  if [ ${#errors} -gt 0 ]; then
    echo ""
    echo "The following errors were detected in your property file:"
    echo ""
    for e in "${errors[@]}"
    do
      echo "    - $e"
    done
    echo ""
    exit 1
  fi
}

get_ignored_storage_class_properties()
{
  [ -z "$1" ] && return

  # Array is passed in as a nameref
  declare -n arr=$1

  local storage_props=""
  storage_props=$(grep "_STORAGE_TYPE=" "$CONFIGURE_PROPERTIES")

  for line in $storage_props
  do
    local key=$(echo "$line" | cut -d= -f1)
    local val=${!key}

    if [ "${val^^}" = "STATIC" ]; then
      local prefix=$(echo "$key" | cut -d_ -f1)
      local storage_class_name="${prefix}_STORAGE_CLASS"

      # Add ignored storage class property
      arr+=( "$storage_class_name" )
    fi
  done
}

replace_json_placeholders()
{
  echo "Creating storage JSON..."
  while IFS= read line
  do
    var=$(echo "$line" | cut -d= -f1)
    val=${!var}

    echo_v "  ${var} = ${val}"

    edit_in_file 's^<'${var}'>^'"${val}"'^g' "${STORAGE_JSON}"

  done < <(< "${CONFIGURE_PROPERTIES}" grep -Ev "^#|^$" | grep STORAGE)
}

handle_labels()
{
  local prefix="$1"
  local place_holder="$2"
  local file="$3"
  local -a var_list=()
  local tmp_file="${TEMP_DIR}/configure.labels.$$.tmp"

  echo_v "  Setting labels for $place_holder..."

  found=$(< "${CONFIGURE_PROPERTIES}" grep -Ev "^#|^$" | grep "$prefix")
  [ -z "$found" ] && fail "Property $prefix not found in $(basename ${CONFIGURE_PROPERTIES}).  Is this file up to date?"

  # Create var_list of label variables
  while IFS= read line
  do
    local value_string="$(echo "$line" | cut -d= -f2- | sed 's/"//g')"

    if [ -n "$value_string" ]; then
      var_list+=("$value_string")
    fi
  done < <(< "${CONFIGURE_PROPERTIES}" grep -Ev "^#|^$" | grep "$prefix")

  local len=${#var_list[@]}

  rm -f "$tmp_file"

  # Convert var_list into key/value JSON format
  for i in "${!var_list[@]}"
  do
    local key="${var_list[$i]%%:*}"
    local val="${var_list[$i]##*:}"

    if [ $i -lt $(($len - 1)) ]; then
      echo "        \"$key\": \"$val\"," >> "$tmp_file"
    else
      echo "        \"$key\": \"$val\"" >> "$tmp_file"
    fi
  done

  # Create bash variable with hard \n's in it
  local data=""
  if [ $len -gt 0 ]; then
    local data=$(cat "$tmp_file")
    data=${data//$'\n'/\\n}
  fi

  # Replace the labels placeholder with json list
  edit_in_file "s^${place_holder}^${data}^g" "$file"

  rm -f "$tmp_file"
}

# If $CLOUD_CONFIG_JSON_FILENAME is defined remove certain
# storage sections if their storage class is blank.
check_remove_storage_sections()
{
  [ -z "$CLOUD_CONFIG_JSON_FILENAME" ] && return

  echo_v "  CLOUD_CONFIG_JSON_FILENAME is defined. Checking storage properties..."

  if [ -z "$RELATIONAL_STORAGE_CLASS" ]; then
    echo_v "    - Removing RELATIONAL_STORAGE_XXXX sections of storage json."
    cat "$STORAGE_JSON" | jq -r 'del(.volumesConfig[] | select(.id == "vd58dbe95-ef94-4a1a-bfa9-771a1a107dba"))' | tee "$STORAGE_JSON" > /dev/null
    cat "$STORAGE_JSON" | jq -r 'del(.volumesConfig[] | select(.id == "vfe7e3e14-1f6e-49a3-baef-ea60ccd28faa"))' | tee "$STORAGE_JSON" > /dev/null
  fi

  if [ -z "$OBJECT_STORAGE_CLASS" ]; then
    echo_v "    - Removing OBJECT_STORAGE_XXXX section of storage json."
    cat "$STORAGE_JSON" | jq -r 'del(.volumesConfig[] | select(.id == "vbb1542cb-76cd-4247-9704-8da7308b9091"))' | tee "$STORAGE_JSON" > /dev/null
  fi
}

create_storage_json()
{
  cp -p "${STORAGE_JSON_TEMPLATE}" "${STORAGE_JSON}"
  [ $? -ne 0 ] && "Failed to copy JSON storage template: ${STORAGE_JSON_TEMPLATE}"

  replace_json_placeholders

  handle_labels "RELATIONAL_STORAGE_LABEL" "<RELATIONAL_LABELS>" "${STORAGE_JSON}"
  handle_labels "OBJECT_STORAGE_LABEL" "<OBJECT_LABELS>" "${STORAGE_JSON}"
  handle_labels "MEMORY_STORAGE_LABEL" "<MEMORY_LABELS>" "${STORAGE_JSON}"
  handle_labels "QUEUE_STORAGE_LABEL" "<QUEUE_LABELS>" "${STORAGE_JSON}"
  handle_labels "INDEXER_STORAGE_LABEL" "<INDEXER_LABELS>" "${STORAGE_JSON}"
  handle_labels "SHARING_STORAGE_LABEL" "<SHARING_LABELS>" "${STORAGE_JSON}"
  handle_labels "PROMETHEUS_STORAGE_LABEL" "<PROMETHEUS_LABELS>" "${STORAGE_JSON}"

  # Remove storage sections if necessary
  # issue 21371: Using jq del() to remove elements of an array can produce unexpected results
  # check_remove_storage_sections

  echo_v "  STORAGE_JSON = $STORAGE_JSON"
}

minify_json_file()
{
  local file="$1"

  [ ! -f "$file" ] && fail "JSON file not found: $file"

  jq -rc < "${file}"
}

# labels are required for STATIC storage sections optional for DYNAMIC
check_storage_labels()
{
  check_storage_label "RELATIONAL_STORAGE"
  check_storage_label "OBJECT_STORAGE"
  check_storage_label "MEMORY_STORAGE"
  check_storage_label "QUEUE_STORAGE"
  check_storage_label "INDEXER_STORAGE"
  check_storage_label "SHARING_STORAGE"
  check_storage_label "PROMETHEUS_STORAGE"
}

check_storage_label()
{
  local prefix="$1"
  local -a var_list=()

  # Create var_list of variables
  while IFS= read line
  do
    local value_string="$(echo "$line" | cut -d= -f2- | sed 's/"//g')"

    if [ -n "$line" ]; then
      var_list+=("$line")
    fi
  done < <(< "${CONFIGURE_PROPERTIES}" grep -Ev "^#|^$" | grep "$prefix")

  local len=${#var_list[@]}

  local is_static=false

  # Check for DYNAMIC or STATIC storage type
  for i in "${var_list[@]}"
  do
    local key="$(echo $i | cut -d= -f1 | xargs)"
    local val="$(echo $i | cut -d= -f2 | xargs)"

    if [[ $key =~ STORAGE_TYPE ]]; then
      if [ "$val" = "STATIC" ]; then
        is_static=true
        break
      fi
    fi
  done

  # Return if using DYNAMIC storage
  [ "$is_static" = false ] && return

  local has_labels=false
  local -a empty_labels=()

  # Loop through the list of variables for this storage section
  # and check for empty labels for STATIC storage only
  for i in "${var_list[@]}"
  do
    local key="$(echo $i | cut -d= -f1 | xargs)"
    local val="$(echo $i | cut -d= -f2 | xargs)"

    if [[ $key =~ _LABEL_ ]]; then
      if [ -z "$val" ]; then
        empty_labels+=("$key")
      else
        has_labels=true
      fi
    fi
  done

  if [ "$has_labels" = false ]; then
    echo ""
    echo "ERROR: Static storage type $prefix requires at least one label."
    echo ""
    for i in "${var_list[@]}"
    do
      echo "    $i"
    done
    echo ""
    cleanup
    exit 1
  fi
}

# ----------------------------------------------
# Create Site/Organization
# ----------------------------------------------
is_pod_running()
{
  local pod="$1"
  local output=""
  output=$(kubectl get pods -n $K8S_NAMESPACE -o name | grep -w $pod)
  [ -n "$output" ] && true || false
}

get_pod_name()
{
  local pod="$1"
  local name=""
  name=$(kubectl get pods -n $K8S_NAMESPACE -o name | cut -d/ -f2 | grep -w "$pod")
  echo "$name"
}

is_storage_class_valid()
{
  local storage_class="$1"
  local output=""
  output=$(kubectl get sc -n $K8S_NAMESPACE | grep -w "$storage_class")
  [ -n "$output" ] && true || false
}

is_admin_pod_running()
{
  is_pod_running "rest-administrator-api"
}

secs_to_min_sec()
{
  local secs="$1"
  printf "%02dm:%02ds" "$(($secs%3600/60))" "$(($secs%60))"
}

get_admin_pod_name()
{
  local name=$(kubectl get pods -n $K8S_NAMESPACE  | grep rest-administrator-api | awk '{print $1}')
  echo "$name"
}

get_env_variable_secret_value()
{
  local var="$1"
  local val=""
  local secret="$ENV_VARIABLES_SECRET_NAME"

  val=$(kubectl get secret ${secret} -n ${K8S_NAMESPACE} -o jsonpath='{.data.*}' | base64 -d | jq -r . | grep -w ${var} | xargs | sed 's/,//g' | awk '{print $NF}')

  echo "$val"
}

# Collect ARCGIS_ENTERPRISE_FQDN, INGRESS_NODE_FQDN, NodePort and 
# CONTEXT from deployed resources like arcgis-ingress-nginx service, 
# arcgis-en-variables secret.
#
# If the user is using a NodePort use https://<ingress_node>:<node_port> as
# the SITE_URL otherwise use https://${ARCGIS_ENTERPRISE_FQDN}
collect_site_config_info()
{
  local arcgis_enterprise_fqdn=""
  local ingress_pod=""
  local ingress_pod_node=""
  local ingress_service=""
  local ingress_service_type=""
  local context=""
  local node_port=""

  echo "Checking deployed resources..."

  kubectl get secret ${ENV_VARIABLES_SECRET_NAME} -n ${K8S_NAMESPACE} > /dev/null 2>&1
  [ $? -ne 0 ] && fail "The ${ENV_VARIABLES_SECRET_NAME} secret was not found. Could be missing ARCGIS_SITENAME definition in your configure.properties file."

  context=$(get_env_variable_secret_value "CONTEXT")
  [ -z "$context" ] && fail "Could not find CONTEXT in the env-variable secret."

  arcgis_enterprise_fqdn=$(get_env_variable_secret_value "ARCGIS_ENTERPRISE_FQDN")
  [ -z "$arcgis_enterprise_fqdn" ] && fail "Could not find ARCGIS_ENTERPRISE_FQDN in the env-variable secret."

  ingress_pod=$(get_pod_name "${ARCGIS_SITENAME}-ingress-controller")
  [ -z "$ingress_pod" ] && fail "Could not determine the ingress-controllerr pod name."

  ingress_pod_node=$(kubectl get pod ${ingress_pod} -n ${K8S_NAMESPACE} -o jsonpath='{.spec.nodeName}')
  [ -z "$ingress_pod_node" ] && fail "Could not determine ingress-controller pod node name."

  ingress_service=${ARCGIS_SITENAME}-ingress-nginx

  ingress_service_type=$(kubectl get svc ${ingress_service} -n $K8S_NAMESPACE -o jsonpath='{.spec.type}')
  [ -z "$ingress_service_type" ] && fail "Could not determine ingress controller service type."

  if [ "$ingress_service_type" = "NodePort" ]; then
    node_port=$(kubectl get svc ${ingress_service} -n $K8S_NAMESPACE -o jsonpath='{.spec.ports[*].nodePort}')
    [ -z "$node_port" ] && fail "Failed to get the ${ingress_service} service nodePort."
  fi

  # Set globals
  ORGANIZATION_HOST="$arcgis_enterprise_fqdn"
  SITE_URL="https://${ORGANIZATION_HOST}"

  if [ "$ingress_service_type" = "NodePort" ]; then
    ORGANIZATION_HOST="$ingress_pod_node"
    SITE_URL="https://${ORGANIZATION_HOST}:${node_port}"
  fi

  # Override the arcgis-env-variable version of ARCGIS_ENTERPRISE_FQDN if defined in configure.properties
  if [ -n "$ARCGIS_ENTERPRISE_FQDN" ]; then
    ORGANIZATION_HOST="$ARCGIS_ENTERPRISE_FQDN"
    SITE_URL="https://${ORGANIZATION_HOST}"
  fi

  SITE_CONTEXT="$context"

  echo_v "  ARCGIS_SITENAME:        $ARCGIS_SITENAME"
  echo_v "  arcgis_enterprise_fqdn: $arcgis_enterprise_fqdn"
  echo_v "  ingress_pod_node:       $ingress_pod_node"
  echo_v "  ingress_pod:            $ingress_pod"
  echo_v "  ingress_service:        $ingress_service"
  echo_v "  ingress_service_type:   $ingress_service_type"
  echo_v "  node_port:              $node_port"
  echo_v "  ORGANIZATION_HOST:      $ORGANIZATION_HOST"
  echo_v "  SITE_URL:               $SITE_URL"
  echo_v "  SITE_CONTEXT:           $SITE_CONTEXT"
}



wait_for_url()
{
  local url="$1"
  local flags="$2"
  local timeout=$(expr 60 \* ${URL_WAIT_TIMEOUT})
  local timer=0
  local delay=3
  local found=false

  SECONDS=0

  while :
  do
    timer=$(expr $timeout - $SECONDS)

    printf_v "  Waiting ${timer} seconds for ${url}..."

    local http_code=0

    http_code=$(curl -o /dev/null ${CURL_FLAGS} --max-time ${CURL_MAX_TIME} -w "%{http_code}\n" ${flags} "${url}")
    http_code=$(printf "%d" "$http_code")  # Strip leading 000 zeros

    printf_v "(%s)\n" "${http_code}"

    if [ $http_code -ge 200 ] && [ $http_code -lt 400 ]; then
      printf_v "  Connection successful. Http code: %s\n" "$http_code"
      found=true
      break
    fi

    sleep $delay

    [ $SECONDS -ge $timeout ] && {
      found=false
      break
    }
  done

  [ "$found" = true ]
}

check_admin_url()
{
  echo "Checking organization URL..."

  # Check host if possible
  which host > /dev/null 2>&1
  if [ $? -eq 0 ]; then
    host ${ORGANIZATION_HOST} > /dev/null 2>&1
    if [ $? -ne 0 ]; then
      echo ""
      echo "Failed to validate host: ${ORGANIZATION_HOST}"
      echo ""
      echo "Check the ARCGIS_ENTERPRISE_FQDN for a valid FQDN in your deployment properties file."

      fail "Failed to validate organization hostname."
    fi
  fi

  wait_for_url "${SITE_URL}/${SITE_CONTEXT}/admin"

  [ $? -eq 0 ] && return

  echo ""
  echo "Error validating organization URL: ${SITE_URL}/${SITE_CONTEXT}/admin"
  echo "Error code from server: $http_code"
  echo ""
  fail "Failed to validate organization URL."
}

get_decrypted_password()
{
  local pw="$ADMIN_PASSWORD"
  local keyfile="$ENCRYPTION_KEYFILE"

  is_portal_federation_enabled && pw="$PORTAL_ADMIN_PASSWORD"

  get_decrypted_aes256_string "$pw" "$keyfile"
}

get_token()
{

  if ! is_token_needed ; then
    debug "$FUNCNAME" "Token is not needed yet"
    return
  fi

  local token=""

  local base_url="$SITE_URL"
  local admin_user="${ADMIN_USERNAME}"
  local admin_pass="${ADMIN_PASSWORD}"
  local token_url="${base_url}/${SITE_CONTEXT}/sharing/rest/generateToken"

  if [ "$HELM_DEPLOY" = false ]; then
    admin_pass="$(get_decrypted_password)"
  fi

  if is_portal_federation_enabled ; then
    base_url="$PORTAL_URL"
    admin_user="$PORTAL_ADMIN_USERNAME"
    token_url="${base_url}/sharing/rest/generateToken"
  fi

  local cmd="curl -X POST ${CURL_FLAGS} \
             -F 'username=${admin_user}' \
             -F 'password=${admin_pass}' \
             -F 'client=referer' \
             -F 'expiration=60' \
             -F 'f=pjson' \
             -F 'referer=${SITE_URL}/${SITE_CONTEXT}' \
             \"${token_url}\""

  debug "$FUNCNAME" "req=$cmd"

  res=$(eval ${cmd})

  debug "$FUNCNAME" "res=$res"

  # A token will only be available when a site it up
  echo "$res" | jq -r '.token' > /dev/null 2>&1
  if [ $? -eq 0 ]; then 
    token=$(echo "$res" | jq -r '.token')
  fi

  echo "$token"
}

# Hit the admin endpoint and look for an error
#
# {
#   "error" : {
#     "code" : 499,
#     "message" : "Token Required.",
#     "details" : null
#   }
# }
is_token_needed()
{
  local url="${SITE_URL}/${SITE_CONTEXT}/admin?f=json"
  local res=""
  local code=""

  res=$(curl ${CURL_FLAGS} "$url")

  code=$(echo "$res" | jq -r -e '.error.code')
  [ "$code" = "499" ] 
}

# get_site_status() - Query for global site status
# {
#    . . .
#    "currentVersion": 10.9,
#    "status": {
#	    . . .
#        "warnings": [
#            "Warning message 1",
#            "Warning message 2"
#        ],
#        "stages": [
#            ...
#        ],
#        "state": "in_progress",
#        "message": "Creating a new organization."
#    },
#}
# NOTE: message won't exist if state=not_configured
# state = not_configured(0), in_progress(1), configured(2), failed(3), ready(4)
#
get_site_status()
{
  local res=""
  local token=""
  local state=""
  local message=""
  local warnings=""
  local url="${SITE_URL}/${SITE_CONTEXT}/admin?f=json"

  token=$(get_token)

  if [ -n "$token" ]; then
    url="${SITE_URL}/${SITE_CONTEXT}/admin?f=json&token=$token"
  fi

  debug "$FUNCNAME" "\ncurl ${CURL_FLAGS} \"$url\""

  res=$(curl ${CURL_FLAGS} "$url")

  [ -n "$res" ] && {

    debug "$FUNCNAME" "res = ${res}"
    
    state=$(echo $res | jq -r '.status.state')

    # Handle warnings differently.  Base64 them since they may contain
    # newlines. Also, we can't just add them to an array since
    # get_site_status() is run in a subshell. So use a temp file.
    echo "$res" | jq -r '.status.warnings[]' > /dev/null 2>&1
    if [ $? -eq 0 ]; then
      warnings=$(echo "$res" | jq -r '.status.warnings[] | @base64')

      [ -n "$warnings" ] && echo "$warnings" > "$WARNINGS_FILE"
    fi

    if [ "$state" != "not_configured" ]; then
      message=$(echo $res | jq -r '.status.message')
    fi
  }

  echo "${state}|${message}"
}

# get_stages_list() - Just retrieve the stages[] array:
#
#    "status": {
#        "stages": [
#            {
#               "lastUpdated": 1612473621303,
#                "name": "Configuration Store",
#                "state": "completed"
#            },
#            {
#                "lastUpdated": 1612473704542,
#                "name": "Relational Store",
#                "state": "completed"
#            },
#            {
#                "lastUpdated": 1612473637963,
#                "name": "Queue Store",
#                "state": "in_progress"
#            },
#            . . .
# The stages will only be available once configure is initiated.
#
# The result returns will be a long string of "name1:state1,name2:state2,name3:state3, etc..."
# which will be parsed below in poll_site_status().
get_stages_list()
{
  local token=""
  local stages=""
  local url="${SITE_URL}/${SITE_CONTEXT}/admin?f=json"

  token=$(get_token)

  if [ -n "$token" ]; then
    url="${SITE_URL}/${SITE_CONTEXT}/admin?f=json&token=$token"
  fi

  debug "$FUNCNAME" "\ncurl ${CURL_FLAGS} \"$url\""

  local res=$(curl ${CURL_FLAGS} "$url")

  [ -n "$res" ] && {

    debug "$FUNCNAME" "res = ${res}"

    stages=$(echo $res | jq -r '.status.stages[] | [.name, .state] | @csv' | sed 's/,/:/g' | sed 's/"//g' | paste -sd ',' -)
  }

  echo "${stages}"
}

get_log_settings()
{
  local log_level=""
  local log_retention=60

  [ -n "$LOG_RETENTION_MAX_DAYS" ] && log_retention=${LOG_RETENTION_MAX_DAYS}
  [ -n "$LOG_SETTING" ] && log_level="$LOG_SETTING"

  local json=$(cat <<EOF
  {
    "maxLogAgeDays": ${log_retention},
    "logLevel": "${log_level}"
  }
EOF
)

  # Minify
  echo "$json" | jq -rc
}

get_user_managed_datastores()
{
  local json=""

  if [ -n "$USER_MANAGED_DATASTORES" ]; then
    [ ! -f "$USER_MANAGED_DATASTORES" ] && fail "Could not find userManagedStores file: $USER_MANAGED_DATASTORES"
 
    # Redefine it based on .json contents
    json=$(minify_json_file "$USER_MANAGED_DATASTORES")
  fi
  
  USER_MANAGED_DATASTORES_JSON="$json"
}

get_cloud_config_file_data()
{
  local json=""

  if [ -n "$CLOUD_CONFIG_JSON_FILENAME" ]; then

    # Redefine it based on .json contents
    json=$(minify_json_file "$CLOUD_CONFIG_JSON_FILENAME")
  fi

  CLOUD_CONFIG_JSON="$json"
}

get_placement_policy_file_data()
{
  local json=""

  if [ -n "$PLACEMENT_POLICIES_CONFIG_FILENAME" ]; then

    # Redefine it based on .json contents
    json=$(minify_json_file "$PLACEMENT_POLICIES_CONFIG_FILENAME")
  fi

  PLACEMENT_POLICIES_CONFIG_JSON="$json"
}

# NOT CALLED YET. Needs to be modified to use encrypted secret (plan A)
get_cloud_config_secret_data()
{
  local json=""

  if [ -n "$CLOUD_CONFIG_SECRET_NAME" ]; then
    json=$(kubectl get secret ${CLOUD_CONFIG_SECRET_NAME} -n ${K8S_NAMESPACE} -o 'go-template={{ .data.cloudConfig | base64decode }}')

    # minify
    json=$(echo $json | jq -rc)
  fi

  CLOUD_CONFIG_JSON="$json"
}

is_enterprise_deployment()
{
  local deploy_type=""

  deploy_type=$(get_env_variable_secret_value "DEPLOY_TYPE")

  if [ -z "$deploy_type" ] || [ "$deploy_type" = "enterprise" ]; then
    return 0
  fi

  return 1
}

is_portal_federation_enabled()
{
  [ -n "$PRIVATE_PORTAL_URL" ] && [ -n "$PORTAL_URL" ]
}

get_portal_federation_data()
{
  local json=""

  if is_portal_federation_enabled ; then
    local private_portal_url="$PRIVATE_PORTAL_URL"
    local portal_url="$PORTAL_URL"
    local admin_user="$PORTAL_ADMIN_USERNAME"
    local admin_pass=""
    local portal_mode="${PORTAL_MODE:-ARCGIS_PORTAL_FEDERATION}"
    local server_id="${SERVER_ID:-null}"
    local secret_key="${SECRET_KEY:-null}"
    local webgis_server_trust_key="${WEBGIS_SERVER_TRUST_KEY:-null}"

    admin_pass="$(get_decrypted_password)"

    json=$(printf '{
      "privatePortalUrl": "%s",
      "portalUrl": "%s",
      "username": "%s",
      "password": "%s",
      "portalMode": "%s",
      "serverId": "%s",
      "secretKey": "%s",
      "webgisServerTrustKey": "%s"
    }' "$private_portal_url" "$portal_url" "$admin_user" "$admin_pass" "$portal_mode" "$server_id" "$secret_key" "$webgis_server_trust_key")

    # minify
    json=$(echo $json | jq -rc)
  fi

  echo "$json"
}

validate_license()
{
  local license_file="$1"
  local license_type="$2"

  echo "Checking ${license_type} license..."

  local base_url="${SITE_URL}/${SITE_CONTEXT}/admin/orgs/0123456789ABCDEF/license/validateLicense"

  wait_for_url "$base_url" "-F 'file=@${license_file};headers=\"Expect:\"' -F 'listAdministratorUserTypes=true' -F 'f=pjson'"

  [ $? -ne 0 ] && fail "Could not connect to license validation API."

  local cmd="curl ${CURL_FLAGS} \
    -F 'file=@${license_file}' \
    -F 'listAdministratorUserTypes=true' \
    -F 'f=pjson' \
    ${base_url}"

  debug "$FUNCNAME" "\n$cmd"

  res=$(eval $cmd)

  echo_v "res=$res"

  echo "$res" | jq -r -e '.error.message' > /dev/null 2>&1

  if [ $? -eq 0 ]; then
     message=$(echo $res | jq -r '.error.message')
     fail "$message"
  fi

}

validate_k8s_license()
{
  validate_license "$LICENSE_FILE" "Kubernetes"
}

get_configure_curl_cmd()
{
  local license_file="${LICENSE_FILE}"
  local storage_json=$(minify_json_file "${STORAGE_JSON}")

  local admin_user="${ADMIN_USERNAME}"
  local admin_pass="${ADMIN_PASSWORD}"

  if [ "$HELM_DEPLOY" = false ]; then
    admin_pass="$(get_decrypted_password)"
  fi

  local log_settings="$(get_log_settings)"

  get_user_managed_datastores
  # get_cloud_config_secret_data
  get_cloud_config_file_data
  get_placement_policy_file_data

  local user_managed_datastores="$USER_MANAGED_DATASTORES_JSON"
  local cloud_config="$CLOUD_CONFIG_JSON"
  local placement_policy_config="$PLACEMENT_POLICIES_CONFIG_JSON"
  local portal_federation_data=$(get_portal_federation_data)
  local cmd=""

  if is_portal_federation_enabled ; then
    cmd="curl ${CURL_FLAGS} \
      -F 'licenseFile=@${license_file}' \
      -F 'volumesConfig=${storage_json}' \
      -F 'systemArchitectureProfile={\"name\":\"${SYSTEM_ARCH_PROFILE}\"}' \
      -F 'logSettings=${log_settings}' \
      -F 'userManagedStores=${user_managed_datastores}' \
      -F 'placementPoliciesConfig=${placement_policy_config}' \
      -F 'portalFederation=${portal_federation_data}' \
      -F 'f=pjson' \
      ${SITE_URL}/${SITE_CONTEXT}/admin/configure"
  else
    cmd="curl ${CURL_FLAGS} \
      -F 'username=${admin_user}' \
      -F 'password=${admin_pass}' \
      -F 'email=${ADMIN_EMAIL}' \
      -F 'fullName=${ADMIN_FIRST_NAME} ${ADMIN_LAST_NAME}' \
      -F 'securityQuestionIdx=${SECURITY_QUESTION_INDEX}' \
      -F 'securityQuestionAns=${SECURITY_QUESTION_ANSWER}' \
      -F 'userLicenseTypeId=${LICENSE_TYPE_ID}' \
      -F 'licenseFile=@${license_file}' \
      -F 'volumesConfig=${storage_json}' \
      -F 'systemArchitectureProfile={\"name\":\"${SYSTEM_ARCH_PROFILE}\"}' \
      -F 'logSettings=${log_settings}' \
      -F 'userManagedStores=${user_managed_datastores}' \
      -F 'cloudConfig=${cloud_config}' \
      -F 'placementPoliciesConfig=${placement_policy_config}' \
      -F 'f=pjson' \
      ${SITE_URL}/${SITE_CONTEXT}/admin/configure"
  fi

  echo "$cmd"
}

create_site()
{
  local cmd=$(get_configure_curl_cmd)

  echo ""
  draw_line

  debug "$FUNCNAME" "\ncmd=$cmd"
  echo_v "cmd=$cmd"

  # Execute the curl and get the json response
  res=$(eval $cmd)

  [ -n "$res" ] && {

    debug "$FUNCNAME" "res = ${res}"
    echo_v "res=$res"

    # check for an error and fail
    echo "$res" | jq -r -e '.error.message' > /dev/null 2>&1
    [ $? -eq 0 ] && {
      local message=$(echo "$res" | jq -r '.error.message')

      fail "$message"
    }
  }

}

is_site_configured()
{
  local state=$(get_site_status | awk -F "|" '{print $1}')

  # not_configured, in_progress, configured, failed, ready
  #
  # We can only run configure when the state = not_configured
  [ "$state" = "ready" ] || [ "$state" = "configured" ]
}

is_configure_in_progress()
{
  local state=$(get_site_status | awk -F "|" '{print $1}')
  [ "$state" = "in_progress" ]
}

is_message_in_list()
{
  local msg="$1"
  local found=1

  for i in "${MESSAGE_LIST[@]}"
  do
    if [ "$i" = "$msg" ]; then
      found=0
      break
    fi
  done

  [ $found -eq 0 ]
}

print_status_line()
{
  local name="$1"
  local state="$2"
  local status_color="${fg_green}"

  [ "$state" = "failed" ] && status_color="${fg_red}"

  printf -- "- %-32s %s%s%s\n" "$name" "$status_color" "$state" "${txt_reset}"
}

exit_with_ctrlc_message()
{
  echo ""
  echo ""
  echo "The configure process will continue to run on the server. If you run this"
  echo "script again while the process is still running, it will reflect the"
  echo "current status."
  echo ""
  exit 0
}

pvc_check()
{
  # Add more as needed
  check_pending_pvc_pod "relational-store"
}

check_pending_pvc_pod()
{
  local name="$1"
  local pvc=""
  local pod=""
  local status=""

  [ $SECONDS -lt $PVC_CHECK_TIMEOUT ] && return
  [ "$PVC_CHECK_CHECKED" = true ] && return

  # Do not check again.
  PVC_CHECK_CHECKED=true

  # Check if pod exists.  If not return.
  pod=$(kubectl get pods --no-headers -n ${K8S_NAMESPACE} | grep "$name" | head -1)
  [ -z "$pod" ] && return

  # Check pod status.  If it's not Pending return.
  status=$(kubectl get pvc --no-headers -n ${K8S_NAMESPACE} | grep "$name" | awk '{ print $2 }')
  [ "$status" != "Pending" ] && return

  # Check PVC status
  pvc=$(kubectl get pvc --no-headers -n ${K8S_NAMESPACE} | grep "$name" | awk '{ print $1 }')
  status=$(kubectl get pvc --no-headers -n ${K8S_NAMESPACE} | grep "$name" | awk '{ print $2 }')

  if [ "$status" = "Pending" ]; then
    warning "Failed to bind PVC ($pvc). Check the storage class name (or labels if using static PVs) in your properties file ($(basename "$CONFIGURE_PROPERTIES"))."
  fi
}

poll_site_status()
{
  local msg="$1"
  local dots=0

  echo ""
  echo "$msg"
  echo ""

  trap exit_with_ctrlc_message SIGINT SIGTERM SIGHUP

  # reset bash timer
  SECONDS=0

  while :
  do
    local res=""
    local current_stages=()
    local org_state=""
    local stages=""
    
    res=$(get_site_status)

    org_state=$(echo $res | awk -F "|" '{print $1}')
    stages=$(get_stages_list)

    # Create current_stages array
    while IFS=, read line
    do
      [ ${#line} -gt 0 ] && current_stages+=("$line")
    done < <(echo "$stages" | tr "," "\n")

    for msg in "${current_stages[@]}"
    do
      local name=$(echo "$msg" | awk -F: '{print $1}' | xargs)
      local state=$(echo "$msg" | awk -F: '{print $2}' | xargs)

      if [ "$state" == "completed" ] || [ "$state" == "failed" ]; then
        if ! is_message_in_list "$name" ; then

          MESSAGE_LIST+=("$name")

          clear_current_line
          
          print_status_line "$name" "$state"

        fi
      fi
    done

    sleep 2

    [ "$HAS_TTY" = true ] &&  printf "%s.%s" "${fg_green}" "${txt_reset}" || printf "."
    (( dots++ ))

    if [ $dots -ge 45 ]; then
      clear_current_line
      dots=0
    fi

    # not_configured, in_progress, configured, failed, ready
    if [ "$org_state" = "not_configured" ] || [ "$org_state" = "failed" ] || [ "$org_state" = "ready" ]; then
      clear_current_line
      break
    fi
    
    pvc_check

  done

  echo ""

}

get_warnings()
{
  [ ! -f "$WARNINGS_FILE" ] && return

  while IFS= read line
  do
    WARNING_LIST+=( "$line" )
  done < "$WARNINGS_FILE"
}

show_warnings()
{
  get_warnings

  [ ${#WARNING_LIST[@]} -eq 0 ] && return

  echo "Warnings:"
  echo ""

  for i in "${WARNING_LIST[@]}"
  do
    warning=$(echo -e "$i" | base64 -d)
    printf "* %s\n" "$warning" | ${FMT}
  done

  echo ""
}

show_success()
{
  local message="$1"

  draw_line
  echo "                           ${fg_green}S U C C E S S !${txt_reset}"
  draw_line
  echo "${message}" | ${FMT}
  echo ""
  show_warnings

  echo "You can use the URLs below to access your "
  echo "${PRODUCT_NAME} deployment."
  echo ""
  local portal_url="${SITE_URL}/${SITE_CONTEXT}/home"
  local manager_url="${SITE_URL}/${SITE_CONTEXT}/manager"
  echo -e "Enterprise portal URL:\n\n\t${portal_url}"
  echo ""
  echo -e "Manager URL:\n\n\t${manager_url}"
  echo ""
}

read_properties_file()
{
  local properties_file="$CONFIGURE_PROPERTIES"

  [ ! -f "$properties_file" ] && fail "Properties file not found ($properties_file).  Cannot determine site URL."

  . "$properties_file"

  ARCGIS_SITENAME="${ARCGIS_SITENAME:-arcgis}"
  ENV_VARIABLES_SECRET_NAME="${ARCGIS_SITENAME}-env-variables"
}

prompt_user()
{
  local deploy_type=""

  deploy_type=$(get_env_variable_secret_value "DEPLOY_TYPE")

  echo ""
  echo "Current deployment properties:"
  echo ""
  echo "  CONFIGURE PROPERTIES FILE: $CONFIGURE_PROPERTIES"
  echo ""
  echo "  LICENSE FILE:              $LICENSE_FILE"
  echo ""
  echo "  DEPLOY_TYPE:               $deploy_type"

  if is_portal_federation_enabled ; then

    echo "  PRIVATE_PORTAL_URL:        $PRIVATE_PORTAL_URL"
    echo "  PORTAL_URL:                $PORTAL_URL"
    echo "  PORTAL_ADMIN_USERNAME:     $PORTAL_ADMIN_USERNAME"
    mask "  PORTAL_ADMIN_PASSWORD:     $PORTAL_ADMIN_PASSWORD" "$PORTAL_ADMIN_PASSWORD"
    echo "  PORTAL_MODE:               $PORTAL_MODE"
  else
    echo "  USERNAME:                  $ADMIN_USERNAME"
    mask "  PASSWORD:                  $ADMIN_PASSWORD" "$ADMIN_PASSWORD"
    echo "  EMAIL:                     $ADMIN_EMAIL"
    echo "  FIRST NAME:                $ADMIN_FIRST_NAME"
    echo "  LAST NAME:                 $ADMIN_LAST_NAME"
  fi
  echo ""
  echo "  SYSTEM ARCHITECTURE:       $SYSTEM_ARCH_PROFILE"
  echo ""
  echo "  NAMESPACE:                 $K8S_NAMESPACE"
  echo "  ORGANIZATION_HOST:         $ORGANIZATION_HOST"
  echo "  CONTEXT:                   $SITE_CONTEXT"
  echo "  ORGANIZATION URL:          $SITE_URL/$SITE_CONTEXT"
  echo ""

  echo_v "  COMMAND=$(get_configure_curl_cmd)"
  echo_v ""

  if [ "$SILENT" = false ]; then
    echo -n "Create organization using these properties ([y]/n)? "
    read ans

    [ -z "$ans" ] && ans="y"

    [ "$ans" != "y" ] && exit_msg "Exiting."
  fi
}

process_args()
{
  while getopts "hf:u:syvd?" opt
  do
    case "$opt" in
      h)
        banner
        usage
        ;;
      f)
        CONFIGURE_PROPERTIES=${OPTARG}
        ;;
      u)
        USER_MANAGED_DATASTORES=${OPTARG}
        ;;
      s|y)
        SILENT=true
        ;;
      v)
        VERBOSE=true
        ;;
      d)
        DEBUG=true
        ;;
      *)
        echo "-- What? --"
        usage
        ;;
    esac
  done

  if [ -z "$CONFIGURE_PROPERTIES" ]; then
    banner
    usage
  fi
}

Main()
{
  init_temp_dir
  sanity_check

  . "${COMMON}"

  process_args "$@"
  
  validation_check

  if ! is_admin_pod_running ; then
    info_exit "${PRODUCT_NAME} is currently not deployed in the namespace ${K8S_NAMESPACE}. Run the 'deploy.sh' script before running this script."
  fi

  # Read ARCGIS_ENTERPRISE_FQDN, INGRESS_NODE_FQDN, NodePort and CONTEXT from deployed resources
  collect_site_config_info

  check_admin_url

  if is_site_configured ; then
    info_exit "An ArcGIS Enterprise organization is already defined in the namespace ${K8S_NAMESPACE}. You will need to undeploy and redeploy to recreate the ArcGIS Enterprise organization."
  fi

  check_storage_labels
  validate_k8s_license

  if is_configure_in_progress ; then
    poll_site_status "Configuration status (in progress):"
  else
    create_storage_json
    echo ""
    get_version_tag
    banner
    prompt_user
    create_site
    poll_site_status "Configuration status:"
  fi

  local res=$(get_site_status)
  local state=$(echo $res | awk -F "|" '{print $1}')
  local message=$(echo $res | awk -F "|" '{print $2}')

  if [ "$state" = "failed" ]; then
    fail "$message"
  else
    show_success "$message"
  fi

  echo ""
  cleanup
}

Main "$@"

