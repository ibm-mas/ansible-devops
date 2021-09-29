# (C) Copyright IBM Corp. 2020  All Rights Reserved.
#
# This script implements/overrides the abstract functions defined in launch.sh interface

# operator specific variables
caseName="ibm-mas"
inventory="ibmMasSetup"
caseCatalogName="ibm-mas-operator-catalog"
channelName="8.5.x"

# variables specific to catalog installation
catalogNamespace="openshift-marketplace"

# implement functions to install or uninstall products
# example

# overriding dynamic args thats passed with --args
parse_custom_dynamic_args() {
    key=$1
    val=$2
    case $key in
    --foo)
        echo "$val"
        ;;
    --bar)
        echo "do something"
        ;;
    esac
}

# Installs the catalog source and operator group
install_catalog() {
    echo "Catalog installation is performed by the MAS Installer"
}

# Install utilizing default OLM method
install_operator() {
    # Verfiy arguments are valid
    validate_install_args

    # create the image-map config map for the operator, to provide the image digests
    local image_map_file="${casePath}/inventory/${inventory}/files/image-map.yaml"
    local cm_name="${caseName}-image-map"
    if [[ -f ${image_map_file} ]]; then
      echo "creating image map configmap: ${cm_name}..."
      oc create configmap ${cm_name} --dry-run=client --from-file=${image_map_file} -o yaml > "${casePath}/inventory/${inventory}/files/image-map-cm.yaml"
      oc apply -n ${namespace} -f "${casePath}/inventory/${inventory}/files/image-map-cm.yaml"
      rm "${casePath}/inventory/${inventory}/files/image-map-cm.yaml"
    else
      echo "not creating image map configmap as no image map file was found at ${image_map_file}"
    fi

}

install() {
    install_operator
}

# deletes the catalog source and operator group
uninstall_catalog() {
    echo "Catalog uninstallation is performed by the MAS Uninstaller"
}

# Uninstall operator installed via OLM
uninstall_operator() {
    # delete the image-map config map which provided  image digests
    local cm_name="${caseName}-image-map"
    $kubernetesCLI delete configmap "${cm_name}" -n "${namespace}" --ignore-not-found=true ${dryRun}
}