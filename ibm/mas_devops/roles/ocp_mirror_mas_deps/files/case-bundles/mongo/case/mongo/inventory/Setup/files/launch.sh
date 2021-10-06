#!/bin/bash +x
#
# (C) Copyright IBM Corp. 2020  All Rights Reserved.
#
# This script is a utility to install a product bundled in CASE in online and air gap environment
# This script can be invoked using cloudctl tool (github.com/IBM/cloud-pak-cli](https://github.com/IBM/cloud-pak-cli)
# This script serves as an interface which defines install actions, functions and their inputs

# Parameters are documented within print_usage function.

# ***** GLOBALS *****

# ----- DEFAULTS -----

# Command line tooling & path
kubernetesCLI="oc"
scriptName=$(basename "$0")
scriptDir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Script invocation defaults for parms populated via cloudctl
action="install"
caseJsonFile=""
casePath="${scriptDir}/../../.."
caseName=""
instance=""

# - optional parameter / argument defaults
dryRun=""
deleteCRDs=0
namespace=""
src_registry=""
registry=""
pass=""
secret=""
user=""
inputcasedir=""
mirror_image_chunks=""
image_groups=""
skip_delta=""
recursive_action=0
tolerance_val=0

# docker registry variables
registry_clean=
registry_dir=
registry_engine=
registry_image=
registry_subject=
registry_port=

# script version
version=0.7.0

# Display usage information with return code (if specified)
print_usage() {
    # Determine context of call (via cloudctl or script directly) based on presence of cananical json parameter
    if [ -z "$caseJsonFile" ]; then
        usage="${scriptName} --casePath <CASE-PATH>"
        caseParmDesc="--casePath value, -c value  : root director to extracted CASE file to parse"
        toleranceParm=""
        toleranceParmDesc=""
    else
        usage="cloudctl case launch --case <CASE-PATH>"
        caseParmDesc="--case value, -c value      : local path or URL containing the CASE file to parse"
        toleranceParm="--tolerance tolerance"
        toleranceParmDesc="
  --tolerance value, -t value : tolerance level for validating the CASE
                                 0 - maximum validation (default)
                                 1 - reduced valiation"
    fi
    echo "
USAGE: ${usage} --inventory inventoryItemOfLauncher --action launchAction --instance instance
                  --args \"args\" --namespace namespace ${toleranceParm}

OPTIONS:
   --action value, -a value    : the name of the action item launched
   --args value, -r value      : arguments specific to action (see 'Action Parameters' below).
   ${caseParmDesc}
   --instance value,  -i value : name of instance of target application (release)
   --inventory value, -e value : name of the inventory item launched
   --namespace value, -n value : name of the target namespace
   ${toleranceParmDesc}

 ARGS per Action:
    configure-creds-airgap
      --registry               : source/target container image registry (required)
      --user                   : login user name for the container image registry (required)
      --pass                   : login password for the container image registry (required)

    configure-cluster-airgap
      --dryRun                 : print the actions that would be taken and exit without writing to the destinations
      --inputDir               : path to saved CASE directory
      --registry               : target container image registry (required)

    image-info                 : list image registries and namespaces used in mirroring
      --inputDir               : path to saved CASE directory (required)

    mirror-images
      --dryRun                 : print the actions that would be taken and exit without writing to the destinations
      --inputDir               : path to saved CASE directory (required)
      --fromRegistry           : override the source image registry in the CASE
      --registry               : target container image registry (required)
      --chunks                 : mirror the images in batches with a given size. Default is 100
      --groups                 : list of image groups to mirror
      --skipDelta              : copy all of the images and not just the delta

    install
      --registry               : source/target container image registry
      --user                   : login user name for the container image registry
      --pass                   : login password for the container image registry
      --secret                 : name of existing image pull secret for the container image registry
      --groups                 : list of image groups to install

    install-catalog:
      --dryRun                 : print the actions that would be taken and exit without writing to the destinations
      --registry               : target container image registry
      --recursive              : recursively install dependent catalogs
      --inputDir               : path to saved CASE directory ( required if --recurse is set)
      --groups                 : list of image groups to filter catalog

    install-operator:
      --dryRun                 : print the actions that would be taken and exit without writing to the destinations
      --channelName            : name of channel for subscription (packagemanifest default used if not specified)
      --secret                 : name of existing image pull secret for the container image registry
      --registry               : container image registry (required if pass|user specified)
      --user                   : login user name for the container image registry (required if registry|pass specified)
      --pass                   : login password for the container image registry (required if registry|user specified)

    install-operator-native:
      --secret                 : name of existing image pull secret for the container image registry
      --registry               : container image registry (required if pass|user specified)
      --user                   : login user name for the container image registry (required if pass specified)
      --pass                   : login password for the container image registry (required if user specified)
      --recursive              : recursively install dependent catalogs
      --inputDir               : path to saved CASE directory ( required if --recurse is set)
      --groups                 : list of image groups to install

    uninstall                  : uninstall the product

    uninstall-catalog          : uninstalls the catalog source and operator group
      --dryRun                 : print the actions that would be taken and exit without writing to the destinations
      --recursive              : recursively install dependent catalogs
      --inputDir               : path to saved CASE directory ( required if --recurse is set)

    uninstall-operator         : delete the operator deployment via OLM
      --dryRun                 : print the actions that would be taken and exit without writing to the destinations

    uninstall-operator-native  : deletes the operator deployment via native way
      --deleteCRDs             : deletes CRD's associated with this operator (if not set, crds won't get deleted)
      --recursive              : recursively install dependent catalogs
      --inputDir               : path to saved CASE directory ( required if --recurse is set)

    apply-custom-resources     : creates the sample custom resource

    delete-custom-resources    : deletes the same custom resource

    init-registry              : configure a local docker registry with self-sign certificate
      --user                   : login user name for the container image registry
      --pass                   : login password for the container image registry
      --dir                    : local directory for the docker registry (default: /tmp/docker-registry)
      --subject                : self-sign TLS certificate subject
      --registry               : IP or FQDN for the docker registry ( default: $(hostname -f))
      --clean                  : clean up all existing repositories data


    start-registry             : start a local docker registry container
      --port                   : registry service port (default: 5000 )
      --dir                    : local directory for the docker registry (default: /tmp/docker-registry)
      --engine                 : container engine to run the container (docker or podman)
      --image                  : docker registry image (default: docker.io/library/registry:2.6)

    stop-registry              : stop a local docker registry container
      --engine                 : container engine to run the container (docker or podman)
"

    if [ -z "$1" ]; then
        exit 1
    else
        exit "$1"
    fi
}

# ----- Actions -----
# Run the action specified
run_action() {
    echo "Executing inventory item ${inventory}, action ${action} : ${scriptName}"
    case $action in
    configureCredsAirgap)
        configure_creds_airgap
        ;;
    configureClusterAirgap)
        configure_cluster_airgap
        ;;
    install)
        install
        ;;
    installCatalog)
        install_catalog
        ;;
    installOperator)
        install_operator
        ;;
    installOperatorNative)
        install_operator_native
        ;;
    imageInfo)
        image_info
        ;;
    mirrorImages)
        mirror_images
        ;;
    uninstall)
        uninstall
        ;;
    uninstallCatalog)
        uninstall_catalog
        ;;
    uninstallOperator)
        uninstall_operator
        ;;
    uninstallOperatorNative)
        uninstall_operator_native
        ;;
    applyCustomResources)
        apply_custom_resources
        ;;
    deleteCustomResources)
        delete_custom_resources
        ;;
    initRegistry)
        init_registry
        ;;
    startRegistry)
        start_registry
        ;;
    stopRegistry)
        stop_registry
        ;;
    *)
        err "Invalid Action ${action}"
        print_usage 1
        ;;
    esac
}

# Parses the args (--args) parameter if any are specified
parse_dynamic_args() {
    _IFS=$IFS
    IFS=" "
    read -ra arr <<<"${1}"
    IFS="$_IFS"
    arr+=("")
    idx=0
    v="${arr[${idx}]}"

    while [ "$v" != "" ]; do
        case $v in
        # Enable debug from cloudctl invocation
        --debug)
            idx=$((idx + 1))
            set -x
            ;;
        --dryRun)
            dryRun="--dry-run"
            ;;
        --deleteCRDs)
            deleteCRDs=1
            ;;
        --channelName)
            idx=$((idx + 1))
            v="${arr[${idx}]}"
            channelName="${v}"
            ;;
        --fromRegistry)
            idx=$((idx + 1))
            v="${arr[${idx}]}"
            src_registry="${v}"
            ;;
        --registry)
            idx=$((idx + 1))
            v="${arr[${idx}]}"
            registry="${v}"
            ;;
        --chunks)
            idx=$((idx + 1))
            v="${arr[${idx}]}"
            mirror_image_chunks="${v}"
            ;;
        --groups)
            idx=$((idx + 1))
            v="${arr[${idx}]}"
            image_groups="${v}"
            ;;
        --skipDelta)
            idx=$((idx + 1))
            v="${arr[${idx}]}"
            skip_delta="${v}"
            ;;
        --inputDir)
            idx=$((idx + 1))
            v="${arr[${idx}]}"
            inputcasedir="${v}"
            ;;
        --user)
            idx=$((idx + 1))
            v="${arr[${idx}]}"
            user="${v}"
            ;;
        --pass)
            idx=$((idx + 1))
            v="${arr[${idx}]}"
            pass="${v}"
            ;;
        --secret)
            idx=$((idx + 1))
            v="${arr[${idx}]}"
            secret="${v}"
            ;;
        --recursive)
            recursive_action=1
            ;;
        # flags related to starting/stopping local docker registry
        --subject)
            idx=$((idx + 1))
            v="${arr[${idx}]}"
            registry_subject="${v}"
            ;;
        --dir)
            idx=$((idx + 1))
            v="${arr[${idx}]}"
            registry_dir="${v}"
            ;;
        --engine)
            idx=$((idx + 1))
            v="${arr[${idx}]}"
            registry_engine="${v}"
            ;;
        --port)
            idx=$((idx + 1))
            v="${arr[${idx}]}"
            registry_port="${v}"
            ;;
        --clean)
            registry_clean=1
            ;;
        --help)
            print_usage 0
            ;;
        *)
            # pass arr[i], arr[i+1] to the override function
            parse_custom_dynamic_args "${arr[${idx}]}" "${arr[$((idx + 1))]}"
            ;;
        esac
        idx=$((idx + 1))
        v="${arr[${idx}]}"
    done
}

# ***** ARGUMENT CHECKS *****

# Validates that the required parameters were specified for script invocation
check_cli_args() {
    # Verify required parameters were specifed and are valid (including environment setup)
    # - case path
    [[ -z "${casePath}" ]] && { err_exit "The case path parameter was not specified."; }
    [[ ! -f "${casePath}/case.yaml" ]] && { err_exit "No case.yaml in the root of the specified case path parameter."; }

    # Verify kubernetes connection and namespace
    # skip this check for certain actions
    skip_actions="imageInfo mirrorImages configureCredsAirgap initRegistry startRegistry stopRegistry"
    if [[ "$skip_actions" != *$action* ]]; then
        check_kube_connection
        check_kube_namespace
    fi
}

# Verifies that we have a connection to the Kubernetes cluster
check_kube_connection() {
    # Check if default oc CLI is available and if not fall back to kubectl
    command -v $kubernetesCLI >/dev/null 2>&1 || { kubernetesCLI="kubectl"; }
    command -v $kubernetesCLI >/dev/null 2>&1 || { err_exit "No oc or kubectl found in path"; }

    # Query apiservices to verify connectivity
    if ! $kubernetesCLI get apiservices >/dev/null 2>&1; then
        # Developer note: A kubernetes CLI should be included in your prereqs.yaml as a client prereq if it is required for your script.
        err_exit "Verify that $kubernetesCLI is installed and you are connected to a Kubernetes cluster."
    fi
}

check_kube_namespace() {
    [[ -z "${namespace}" ]] && { err_exit "The namespace parameter was not specified."; }
    if ! $kubernetesCLI get namespace "${namespace}" >/dev/null; then
        err_exit "Unable to retrieve namespace specified ${namespace}"
    fi
}

check_secret_params() {

    local foundError=0

    [[ -z ${secret} ]] && {
        foundError=1
        err "'--secret' is required for creating a registry secret"
    }
    [[ -z ${registry} ]] && {
        foundError=1
        err "'--registry' is required for creating a registry secret"
    }
    [[ -z ${user} ]] && {
        foundError=1
        err "'--user' is required for creating a registry secret"
    }
    [[ -z ${pass} ]] && {
        foundError=1
        err "'--pass' is required for creating a registry secret"
    }

    # Print usage if missing parameter
    [[ $foundError -eq 1 ]] && { print_usage 1; }
}

# Validates that the required args were specified for install action
validate_install_args() {
    # using a mode flag to share the validation code between install and uninstall
    local mode="$1"

    # Verify arguments required per install method were provided
    echo "Checking install arguments for ${mode:-install}"

    if [[ ${recursive_action} -eq 1 && -z "${inputcasedir}" ]]; then
        err "'--inputDir' must be specified with the '--args' parameter when '--recursive' is set"
        print_usage 1
    fi

    # Validate secret arguments provided are valid combination and
    #   either create or check for existence of secret in cluster.
    if [[ -n "${registry}" && -z "${user}" && -z "${pass}" && -z "${secret}" ]]; then
        # registry is provided, but not a user/pass/secret, continue
        :
    elif [[ -n "${registry}" || -n "${user}" || -n "${pass}" ]]; then
        check_secret_params
        set -e
        $kubernetesCLI create secret docker-registry "${secret}" \
            --docker-server="${registry}" \
            --docker-username="${user}" \
            --docker-password="${pass}" \
            --docker-email="${user}" \
            --namespace "${namespace}"
        set +e
    elif [[ -n ${secret} ]]; then
        if ! $kubernetesCLI get secrets "${secret}" -n "${namespace}" >/dev/null 2>&1; then
            err "Secret $secret does not exist, either create one or supply additional registry parameters to create one"
            print_usage 1
        fi
    fi
}

validate_install_catalog() {

    # using a mode flag to share the validation code between install and uninstall
    local mode="$1"

    echo "Checking arguments for ${mode:-install} catalog action"

    if [[ ${recursive_action} -eq 1 && -z "${inputcasedir}" ]]; then
        err "'--inputDir' must be specified with the '--args' parameter when '--recursive' is set"
        print_usage 1
    fi
}

# Validates that the required args were specified for secret creation
validate_configure_creds_airgap_args() {
    # Verify arguments required to create secret were provided
    local foundError=0
    [[ -z "${registry}" ]] && {
        foundError=1
        err "'--registry' must be specified with the '--args' parameter"
    }
    [[ -z "${user}" ]] && {
        foundError=1
        err "'--user' must be specified with the '--args' parameter"
    }
    [[ -z "${pass}" ]] && {
        foundError=1
        err "'--pass' must be specified with the '--args' parameter"
    }

    # Print usgae if missing parameter
    [[ $foundError -eq 1 ]] && { print_usage 1; }
}

validate_configure_cluster_airgap_args() {
    # Verify arguments required to create secret were provided
    local foundError=0
    [[ -z "${registry}" ]] && {
        foundError=1
        err "'--registry' must be specified with the '--args' parameter"
    }

    [[ -z "${inputcasedir}" ]] && {
        foundError=1
        err "'--inputDir' must be specified with the '--args' parameter"
    }

    # Print usgae if missing parameter
    [[ $foundError -eq 1 ]] && { print_usage 1; }
}

validate_file_exists() {
    local file=$1
    [[ ! -f ${file} ]] && { err_exit "${file} is missing, exiting deployment."; }
}

# ***** UTILS *****

# Print version
print_version() {
    echo "[INFO] Version ${version}"
    exit 0
}

get_case_name() {

    validate_file_exists $casePath/case.yaml

    caseName="$(grep '^name: ' $casePath/case.yaml)"        #get name from case.yaml
    caseName=$(echo $caseName | awk -F':' '{print $2}')     #get everything after ':', ex. `name: ibm-sample-panamax` becomes `ibm-sample-panamax`
    caseName="$(echo -e "${caseName}" | tr -d '[:space:]')" #trim ALL whitespaces
}

get_case_version() {

    validate_file_exists $casePath/case.yaml

    caseVersion="$(grep '^version: ' $casePath/case.yaml)"        #get name from case.yaml
    caseVersion=$(echo $caseVersion | awk -F':' '{print $2}')     #get everything after ':', ex. `version: 2.0.0` becomes `2.0.0`
    caseVersion="$(echo -e "${caseVersion}" | tr -d '[:space:]')" #trim ALL whitespaces
}

# Error reporting functions
err() {
    echo >&2 "[ERROR] $1"
}
err_exit() {
    echo >&2 "[ERROR] $1"
    exit 1
}

# ----- REGISTRY ACTIONS -----

init_registry() {
    "${scriptDir}"/airgap.sh registry service init \
        ${user:+'--username' "$user"} \
        ${pass:+'--password' "$pass"} \
        ${registry_dir:+'--dir' "$registry_dir"} \
        ${registry_subject:+'--subject' "$registry_subject"} \
        ${registry:+'--registry' "$registry"} \
        ${registry_clean:+'--clean'}
}

start_registry() {
    "${scriptDir}"/airgap.sh registry service start \
        ${registry_dir:+'--dir' "$registry_dir"} \
        ${registry_engine:+'--engine' "$registry_engine"} \
        ${registry_port:+'--port' "$registry_port"} \
        ${registry_image:+'--image' "$registry_image"}
}

stop_registry() {
    "${scriptDir}"/airgap.sh registry service stop \
        ${registry_engine:+'--engine' "$registry_engine"}
}

# ----- CONFIGURE ACTIONS -----

# Add / update local authentication store with user/password specified (~/.airgap/secrets/<registy>.json)
configure_creds_airgap() {
    echo "-------------Configuring authentication secret-------------"

    validate_configure_creds_airgap_args

    # Create registry secret for user information provided

    "${scriptDir}"/airgap.sh registry secret -c -u "${user}" -p "${pass}" "${registry}"
}

# Append secret to Global Cluster Pull Secret (pull-secret in openshif-config)
configure_cluster_pull_secret() {

    echo "-------------Configuring cluster pullsecret-------------"

    # configure global pull secret if an authentication secret exists on disk
    if "${scriptDir}"/airgap.sh registry secret -l | grep "${registry}"; then
        "${scriptDir}"/airgap.sh cluster update-pull-secret --registry "${registry}" "${dryRun}"
    else
        echo "Skipping configuring cluster pullsecret: No authentication exists for ${registry}"
    fi
}

configure_content_image_source_policy() {

    echo "-------------Configuring imagecontentsourcepolicy-------------"

    get_case_name

    echo "name is ${caseName}"
    echo "dir is ${inputcasedir}"

    "${scriptDir}"/airgap.sh cluster apply-image-policy \
        --name "${caseName}" \
        --dir "${inputcasedir}" \
        --registry "${registry}" "${dryRun}"
}

# Apply ImageContentSourcePolicy required for airgap
configure_cluster_airgap() {

    echo "-------------Configuring cluster for airgap-------------"

    validate_configure_cluster_airgap_args

    configure_cluster_pull_secret

    configure_content_image_source_policy
}

# Mirror required images
mirror_images() {
    echo "-------------Mirroring images-------------"

    get_case_name
    get_case_version

    case_archive="${caseName}-${caseVersion}.tgz"

    validate_configure_cluster_airgap_args

    "${scriptDir}"/airgap.sh image mirror \
        --dir "${inputcasedir}" \
        ${src_registry:+'--from-registry' "$src_registry"} \
        --to-registry "${registry}" \
        ${mirror_image_chunks:+'--split-size' "$mirror_image_chunks"} \
        ${image_groups:+'--groups' "$image_groups"} \
        ${skip_delta:+'--skip-delta' "$skip_delta"} \
        ${case_archive:+'--archive' "$case_archive"} \
        "${dryRun}" 
}

# list image registries
image_info() {
    echo "-------------Listing Image Registries and Namespaces -------------"

    [[ -z "${inputcasedir}" ]] && {
        foundError=1
        err "'--inputDir' must be specified with the '--args' parameter"
    }

    "${scriptDir}"/airgap.sh image mirror --show-registries-namespaces --dir "${inputcasedir}"
}

# ----- ABSTRACT FUNCTIONS -----
# the below functions can be overridden in launch implementation script

parse_custom_dynamic_args() {
    err_exit "Invalid Option ${v}"
}

# ----- INSTALL ACTIONS -----

# products can choose to implement the install/uninstall mechanism they support in launch_impl.sh

install() {
    echo "Action not supported"
}

install_dependent_catalogs() {
    echo "Action not supported"
}

install_operator_group() {
    echo "Action not supported"
}

install_catalog() {
    echo "Action not supported"
}

install_operator() {
    echo "Action not supported"
}

install_operator_native() {
    echo "Action not supported"
}

apply_custom_resources() {
    echo "Action not supported"
}

# ----- UNINSTALL ACTIONS -----

uninstall() {
    echo "Action not supported"
}

uninstall_dependent_catalogs() {
    echo "Action not supported"
}

uninstall_catalog() {
    echo "Action not supported"
}

uninstall_operator() {
    echo "Action not supported"
}

uninstall_operator_native() {
    echo "Action not supported"
}

delete_custom_resources() {
    echo "Action not supported"
}

# ----- END ACTIONS -----

##
# Main
##
source "$scriptDir"/launch-impl.sh

# Parse CLI parameters
while [ "${1-}" != "" ]; do
    case $1 in
    # Supported parameters for cloudctl & direct script invocation
    --casePath | -c)
        shift
        casePath="${1}"
        ;;
    --caseJsonFile)
        shift
        caseJsonFile="${1}"
        ;;
    --inventory | -e)
        shift
        inventory="${1}"
        ;;
    --action | -a)
        shift
        action="${1}"
        ;;
    --namespace | -n)
        shift
        namespace="${1}"
        ;;
    --tolerance | -t)
        shift
        tolerance_val="${1}"
        ;;
    --instance | -i)
        shift
        instance="${1}"
        ;;
    --args | -r | --)
        shift
        parse_dynamic_args "${1}"
        ;;
    # Additional supported parameters for direct script invocation ONLY
    --help)
        print_usage 0
        ;;
    --debug)
        set -x
        ;;
    --version)
        print_version
        ;;
    *)
        echo "Invalid Option ${1}" >&2
        exit 1
        ;;
    esac
    shift
done

# Execution order
check_cli_args
run_action
