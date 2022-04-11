locals {
  ocs_ami_id = var.ocs.ami_id == "" ? var.aws_amis[var.region]["hvm"] : var.ocs.ami_id
}

resource "aws_kms_key" "ocs_key" {
  description = "Key used to encrypt OCS PVCs"
}

resource "local_file" "ocs_olm_yaml" {
  content  = data.template_file.ocs_olm.rendered
  filename = "${var.installer_workspace}/ocs_olm.yaml"
}

resource "local_file" "ocs_storagecluster_yaml" {
  content  = data.template_file.ocs_storagecluster.rendered
  filename = "${var.installer_workspace}/ocs_storagecluster.yaml"
}

resource "local_file" "ocs_toolbox_yaml" {
  content  = data.template_file.ocs_toolbox.rendered
  filename = "${var.installer_workspace}/ocs_toolbox.yaml"
}

resource "local_file" "ocs_machineset_yaml" {
  content  = data.template_file.ocs_machineset.rendered
  filename = "${var.installer_workspace}/ocs_machineset.yaml"
}

resource "null_resource" "deploy_storage_nodes" {
  count = var.ocs.enable && var.ocs.dedicated_nodes ? 1 : 0
  triggers = {
    openshift_api       = var.openshift_api
    openshift_username  = var.openshift_username
    openshift_password  = var.openshift_password
    openshift_token     = var.openshift_token
    installer_workspace = var.installer_workspace
  }
  provisioner "local-exec" {
    when    = create
    command = <<EOF
echo "Attempting login.."
export KUBECONFIG=${self.triggers.installer_workspace}/auth/kubeconfig
oc login ${self.triggers.openshift_api} -u '${self.triggers.openshift_username}' -p '${self.triggers.openshift_password}' --insecure-skip-tls-verify=true || oc login --server='${self.triggers.openshift_api}' --token='${self.triggers.openshift_token}'
echo "Creating OCS MachineSet"
CLUSTERID=$(oc get machineset -n openshift-machine-api -o jsonpath='{.items[0].metadata.labels.machine\.openshift\.io/cluster-api-cluster}')
sed -i -e s/CLUSTERID/$CLUSTERID/g ${self.triggers.installer_workspace}/ocs_machineset.yaml
oc create -f ${self.triggers.installer_workspace}/ocs_machineset.yaml
echo "Waiting 5mins to deploy nodes"
sleep 300
EOF
  }
  depends_on = [
    local_file.ocs_machineset_yaml,
  ]
}

resource "null_resource" "label_nodes" {
  count = var.ocs.dedicated_nodes ? 0 : 1
  triggers = {
    openshift_api       = var.openshift_api
    openshift_username  = var.openshift_username
    openshift_password  = var.openshift_password
    openshift_token     = var.openshift_token
    installer_workspace = var.installer_workspace
  }
  provisioner "local-exec" {
    when    = create
    command = <<EOF
echo "Attempting login.."
oc login ${self.triggers.openshift_api} -u '${self.triggers.openshift_username}' -p '${self.triggers.openshift_password}' --insecure-skip-tls-verify=true || oc login --server='${self.triggers.openshift_api}' --token='${self.triggers.openshift_token}'
echo "Label worker nodes as storage nodes"
chmod +x ocs/scripts/ocs-prereqs.sh
bash ocs/scripts/ocs-prereqs.sh
EOF
  }
  depends_on = [
    null_resource.deploy_storage_nodes,
  ]
}

resource "null_resource" "install_ocs" {
  triggers = {
    openshift_api       = var.openshift_api
    openshift_username  = var.openshift_username
    openshift_password  = var.openshift_password
    openshift_token     = var.openshift_token
    installer_workspace = var.installer_workspace
  }
  provisioner "local-exec" {
    when    = create
    command = <<EOF
echo "Attempting login.."
oc login ${self.triggers.openshift_api} -u '${self.triggers.openshift_username}' -p '${self.triggers.openshift_password}' --insecure-skip-tls-verify=true || oc login --server='${self.triggers.openshift_api}' --token='${self.triggers.openshift_token}'
echo "Creating namespace, operator group and subscription"
oc create -f ${self.triggers.installer_workspace}/ocs_olm.yaml
echo "Sleeping for 5mins"
sleep 300
echo "Creating storagecluster"
oc create -f ${self.triggers.installer_workspace}/ocs_storagecluster.yaml
echo "Creating OCS toolbox"
oc create -f ${self.triggers.installer_workspace}/ocs_toolbox.yaml
echo "Sleeping for 5mins"
sleep 300
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
    local_file.ocs_olm_yaml,
    local_file.ocs_storagecluster_yaml,
    local_file.ocs_toolbox_yaml,
    null_resource.label_nodes,
    null_resource.deploy_storage_nodes,
  ]
}
