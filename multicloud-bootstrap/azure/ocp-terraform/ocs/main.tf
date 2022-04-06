locals {
  ocptemplates        = "${path.root}/ocpfourxtemplates"
  ocs-machineset-file = var.single-or-multi-zone == "single" ? "ocs-machineset-singlezone.yaml" : "ocs-machineset-multizone.yaml"

  ocpdir = "${path.root}/installer-files"
}

resource "local_file" "toolbox_yaml" {
  content  = data.template_file.ocs_toolbox.rendered
  filename = "${local.ocptemplates}/toolbox.yaml"
}

resource "local_file" "deploy-with-olm_yaml" {
  content  = data.template_file.ocs_olm.rendered
  filename = "${local.ocptemplates}/deploy-with-olm.yaml"
}

resource "local_file" "ocs-machineset-singlezone_yaml" {
  content  = data.template_file.ocs_machineset_singlezone.rendered
  filename = "${local.ocptemplates}/ocs-machineset-singlezone.yaml"
}

resource "local_file" "ocs-machineset-multizone_yaml" {
  content  = data.template_file.ocs_machineset_multizone.rendered
  filename = "${local.ocptemplates}/ocs-machineset-multizone.yaml"
}

resource "local_file" "ocs-storagecluster_yaml" {
  content  = data.template_file.ocs_storagecluster.rendered
  filename = "${local.ocptemplates}/ocs-storagecluster.yaml"
}

resource "null_resource" "install_ocs" {
  triggers = {
    openshift_api       = var.openshift_api
    openshift_username  = var.openshift_username
    openshift_password  = var.openshift_password
    openshift_token     = var.openshift_token
    installer_workspace = var.installer_workspace
    ocp_directory       = local.ocpdir
  }
  provisioner "local-exec" {
    when    = create
    command = <<EOF
echo "Attempting login.."
oc login ${self.triggers.openshift_api} -u '${self.triggers.openshift_username}' -p '${self.triggers.openshift_password}' --insecure-skip-tls-verify=true || oc login --server='${self.triggers.openshift_api}' --token='${self.triggers.openshift_token}'
CLUSTERID=$(oc get machineset -n openshift-machine-api -o jsonpath='{.items[0].metadata.labels.machine\.openshift\.io/cluster-api-cluster}' --kubeconfig ${self.triggers.ocp_directory}/auth/kubeconfig)
sed -i -e s#REPLACE_CLUSTERID#$CLUSTERID#g ${local.ocptemplates}/${local.ocs-machineset-file}
sed -i -e s#REPLACE_REGION#${var.region}#g ${local.ocptemplates}/${local.ocs-machineset-file}
sed -i -e s#REPLACE_VNET_RG#${var.resource-group}#g ${local.ocptemplates}/${local.ocs-machineset-file}
sed -i -e s#REPLACE_WORKER_SUBNET#${var.worker-subnet-name}#g ${local.ocptemplates}/${local.ocs-machineset-file}
sed -i -e s#REPLACE_VNET_NAME#${var.virtual-network-name}#g ${local.ocptemplates}/${local.ocs-machineset-file}
oc apply -f ${local.ocptemplates}/${local.ocs-machineset-file}
sleep 600
oc apply -f ${local.ocptemplates}/deploy-with-olm.yaml
sleep 300
oc apply -f ${local.ocptemplates}/ocs-storagecluster.yaml
sleep 600
oc apply -f ${local.ocptemplates}/toolbox.yaml
sleep 60

EOF
  }
  /* provisioner "local-exec" {
    when    = destroy
    command = <<EOF
echo "Logging in.."
oc login ${self.triggers.openshift_api} -u '${self.triggers.openshift_username}' -p '${self.triggers.openshift_password}' --insecure-skip-tls-verify=true || oc login --server=${self.triggers.openshift_api} --token=${self.triggers.openshift_token}
echo "Delete OCS toolbox"
oc delete -f ${self.triggers.installer_workspace}/ocs_toolbox.yaml
echo "Delete storagecluster"
oc delete -f ${self.triggers.installer_workspace}/ocs_storagecluster.yaml
echo "Delete Operator Group and Subscription."
oc delete -f ${self.triggers.installer_workspace}/ocs_olm.yaml
EOF
  } */
  depends_on = [
    local_file.toolbox_yaml,
    local_file.deploy-with-olm_yaml,
    local_file.ocs-storagecluster_yaml,
    local_file.ocs-machineset-singlezone_yaml,
    local_file.ocs-machineset-multizone_yaml
  ]
}
