locals {
  openshift_installer_url_prefix = "https://mirror.openshift.com/pub/openshift-v4/clients/ocp"
  ocpdir                         = "${path.root}/installer-files"
  installer_workspace            = "${path.root}/installer-files"
  azuredir                       = pathexpand("~/.azure")
  install-config-file            = "install-config-${var.single-or-multi-zone}.tpl.yaml"
  machine-autoscaler-file        = "machine-autoscaler-${var.single-or-multi-zone}.tpl.yaml"
  machine-health-check-file      = "machine-health-check-${var.single-or-multi-zone}.tpl.yaml"
  ocptemplates                   = "${path.root}/ocpfourxtemplates"
  openshift_installer_url        = "${var.openshift_installer_url_prefix}/${var.ocp_version}/"
  ocs-machineset-file            = var.single-or-multi-zone == "single" ? "ocs-machineset-singlezone.yaml" : "ocs-machineset-multizone.yaml"
}

resource "null_resource" "download_binaries" {
  triggers = {
    installer_workspace = local.installer_workspace
  }
  provisioner "local-exec" {
    when    = create
    command = <<EOF
mkdir -p ${local.azuredir}
test -e ${self.triggers.installer_workspace} || mkdir ${self.triggers.installer_workspace}
case $(uname -s) in
  Darwin)
    wget -r -l1 -np -nd -q ${local.openshift_installer_url} -P ${self.triggers.installer_workspace} -A 'openshift-install-mac-4*.tar.gz'
    tar zxvf ${self.triggers.installer_workspace}/openshift-install-mac-4*.tar.gz -C ${self.triggers.installer_workspace}
    wget -r -l1 -np -nd -q ${local.openshift_installer_url} -P ${self.triggers.installer_workspace} -A 'openshift-client-mac-4*.tar.gz'
    tar zxvf ${self.triggers.installer_workspace}/openshift-client-mac-4*.tar.gz -C ${self.triggers.installer_workspace}
    ;;
  Linux)
    wget -r -l1 -np -nd -q ${local.openshift_installer_url} -P ${self.triggers.installer_workspace} -A 'openshift-install-linux-4*.tar.gz'
    tar zxvf ${self.triggers.installer_workspace}/openshift-install-linux-4*.tar.gz -C ${self.triggers.installer_workspace}
    wget -r -l1 -np -nd -q ${local.openshift_installer_url} -P ${self.triggers.installer_workspace} -A 'openshift-client-linux-4*.tar.gz'
    tar zxvf ${self.triggers.installer_workspace}/openshift-client-linux-4*.tar.gz -C ${self.triggers.installer_workspace}
    ;;
  *)
    echo 'Supports only Linux and Mac OS at this time'
    exit 1;;
esac
rm -f ${self.triggers.installer_workspace}/*.tar.gz ${self.triggers.installer_workspace}/README.md ${self.triggers.installer_workspace}/robots*.txt*
EOF
  }

  /* provisioner "local-exec" {
    when    = destroy
    command = <<EOF
rm -rf ${self.triggers.installer_workspace}
EOF
  } */
}

resource "local_file" "install_config_yaml" {
  content  = data.template_file.installconfig.rendered
  filename = "${local.ocpdir}/install-config.yaml"
  depends_on = [
    null_resource.download_binaries
  ]
}

resource "local_file" "machine-health-check_yaml" {
  content  = data.template_file.machine-health-check.rendered
  filename = "${local.ocptemplates}/machine-health-check-${var.single-or-multi-zone}.yaml"
  depends_on = [
    null_resource.download_binaries
  ]
}

resource "local_file" "azurecreds_yaml" {
  content  = data.template_file.azurecreds.rendered
  filename = "${local.azuredir}/osServicePrincipal.json"
  depends_on = [
    null_resource.download_binaries
  ]
}

resource "local_file" "registry-mc_yaml" {
  content  = data.template_file.registry-mc.rendered
  filename = "${local.ocptemplates}/insecure-registry-mc.yaml"
  depends_on = [
    null_resource.install_openshift
  ]
}

resource "local_file" "sysctl-mc_yaml" {
  content  = data.template_file.sysctl-mc.rendered
  filename = "${local.ocptemplates}/sysctl-mc.yaml"
  depends_on = [
    null_resource.install_openshift
  ]
}

resource "local_file" "limits-mc_yaml" {
  content  = data.template_file.limits-mc.rendered
  filename = "${local.ocptemplates}/limits-mc.yaml"
  depends_on = [
    null_resource.install_openshift
  ]
}

resource "local_file" "crio-mc_yaml" {
  content  = data.template_file.crio-mc.rendered
  filename = "${local.ocptemplates}/crio-mc.yaml"
  depends_on = [
    null_resource.install_openshift
  ]
}

resource "local_file" "chrony-mc_yaml" {
  content  = data.template_file.chrony-mc.rendered
  filename = "${local.ocptemplates}/chrony-mc.yaml"
  depends_on = [
    null_resource.install_openshift
  ]
}

resource "local_file" "registry-conf_yaml" {
  content  = data.template_file.registry-conf.rendered
  filename = "${local.ocptemplates}/registries.yaml"
  depends_on = [
    null_resource.install_openshift
  ]
}

resource "local_file" "multipath-mc_yaml" {
  content  = data.template_file.multipath-mc.rendered
  filename = "${local.ocptemplates}/multipath-machineconfig.yaml"
  depends_on = [
    null_resource.install_openshift
  ]
}

resource "local_file" "clusterautoscaler_yaml" {
  content  = data.template_file.clusterautoscaler.rendered
  filename = "${local.ocptemplates}/cluster-autoscaler.yaml"
  depends_on = [
    null_resource.install_openshift
  ]
}

resource "local_file" "machineautoscaler_yaml" {
  content  = data.template_file.machineautoscaler.rendered
  filename = "${local.ocptemplates}/machine-autoscaler-${var.single-or-multi-zone}.yaml"
  depends_on = [
    null_resource.install_openshift
  ]
}

resource "local_file" "htpasswd_yaml" {
  content  = data.template_file.htpasswd.rendered
  filename = "${local.ocptemplates}/auth.yaml"
  depends_on = [
    null_resource.install_openshift
  ]
}

# resource "local_file" "nfs-template_yaml" {
#   count    = var.storage == "nfs" ? 1 : 0
#   content  = data.template_file.nfs-template[count.index].rendered
#   filename = "${local.ocptemplates}/nfs-template.yaml"
#   depends_on = [
#     null_resource.install_openshift
#   ]
# }

resource "null_resource" "install_openshift" {
  triggers = {
    username  = var.admin-username
    directory = local.ocpdir
  }
  provisioner "local-exec" {
    when    = create
    command = <<EOF
mkdir -p ${local.ocptemplates}
cp ${local.ocpdir}/install-config.yaml ${local.ocpdir}/install-config.yaml_backup
chmod +x ${local.ocpdir}/openshift-install
cd ${local.ocpdir} && ./openshift-install create cluster --log-level=debug
EOF
  }

  # Destroy OCP Cluster before destroying the bootnode

  provisioner "local-exec" {
    when    = destroy
    command = <<EOF
cd ${self.triggers.directory} && ./openshift-install destroy cluster --log-level=debug
sleep 5
EOF
  }
  depends_on = [
    azurerm_subnet.masternode,
    azurerm_subnet.workernode,
    local_file.azurecreds_yaml,
    local_file.install_config_yaml
  ]
}

resource "null_resource" "openshift_post_install" {
  triggers = {
    username      = var.admin-username
    ocp_directory = local.ocpdir
  }
  provisioner "local-exec" {
    command = <<EOF
CLUSTERID=$(oc get machineset -n openshift-machine-api -o jsonpath='{.items[0].metadata.labels.machine\.openshift\.io/cluster-api-cluster}' --kubeconfig ${self.triggers.ocp_directory}/auth/kubeconfig)
sed -i -e s/${random_id.randomId.hex}/$CLUSTERID/g ${local.ocptemplates}/machine-health-check-${var.single-or-multi-zone}.yaml
#oc login -u kubeadmin -p $(cat ${local.ocpdir}/auth/kubeadmin-password) -n openshift-machine-api --kubeconfig ${self.triggers.ocp_directory}/auth/kubeconfig
oc create -f ${local.ocptemplates}/machine-health-check-${var.single-or-multi-zone}.yaml --kubeconfig ${self.triggers.ocp_directory}/auth/kubeconfig
htpasswd -c -B -b /tmp/.htpasswd '${var.openshift-username}' '${var.openshift-password}'
sleep 3
oc create secret generic htpass-secret --from-file=htpasswd=/tmp/.htpasswd -n openshift-config --kubeconfig ${self.triggers.ocp_directory}/auth/kubeconfig
oc apply -f ${local.ocptemplates}/auth.yaml --kubeconfig ${self.triggers.ocp_directory}/auth/kubeconfig
oc adm policy add-cluster-role-to-user cluster-admin '${var.openshift-username}' --kubeconfig ${self.triggers.ocp_directory}/auth/kubeconfig
oc project kube-system --kubeconfig ${self.triggers.ocp_directory}/auth/kubeconfig
#sudo mv ${local.ocptemplates}/registries.conf /etc/containers/registries.conf
oc create -f ${local.ocptemplates}/insecure-registry-mc.yaml --kubeconfig ${self.triggers.ocp_directory}/auth/kubeconfig
oc create -f ${local.ocptemplates}/sysctl-mc.yaml --kubeconfig ${self.triggers.ocp_directory}/auth/kubeconfig
oc create -f ${local.ocptemplates}/limits-mc.yaml --kubeconfig ${self.triggers.ocp_directory}/auth/kubeconfig
oc create -f ${local.ocptemplates}/crio-mc.yaml --kubeconfig ${self.triggers.ocp_directory}/auth/kubeconfig
oc create -f ${local.ocptemplates}/chrony-mc.yaml --kubeconfig ${self.triggers.ocp_directory}/auth/kubeconfig
oc create -f ${local.ocptemplates}/multipath-machineconfig.yaml --kubeconfig ${self.triggers.ocp_directory}/auth/kubeconfig
oc patch configs.imageregistry.operator.openshift.io/cluster --type merge -p '{"spec":{"defaultRoute":true, "replicas":${var.worker-node-count}}}' --kubeconfig ${self.triggers.ocp_directory}/auth/kubeconfig
echo 'Sleeping for 15 mins while MCs apply and the cluster restarts' 
sleep 15m
result=$(oc wait machineconfigpool/worker --for condition=updated --timeout=15m --kubeconfig ${self.triggers.ocp_directory}/auth/kubeconfig)
echo $result
oc login https://api.${var.cluster-name}.${var.dnszone}:6443 -u '${var.openshift-username}' -p '${var.openshift-password}' --insecure-skip-tls-verify=true
EOF
  }
  depends_on = [
    null_resource.install_openshift,
    local_file.machine-health-check_yaml,
    local_file.registry-mc_yaml,
    local_file.sysctl-mc_yaml,
    local_file.limits-mc_yaml,
    local_file.crio-mc_yaml,
    local_file.chrony-mc_yaml,
    local_file.registry-conf_yaml,
    local_file.multipath-mc_yaml,
  ]
}

resource "null_resource" "cluster_autoscaler" {
  count = var.clusterAutoscaler == "yes" ? 1 : 0
  triggers = {
    username = var.admin-username
  }
  provisioner "local-exec" {
    command = <<EOF
CLUSTERID=$(oc get machineset -n openshift-machine-api -o jsonpath='{.items[0].metadata.labels.machine\.openshift\.io/cluster-api-cluster}' --kubeconfig ${self.triggers.ocp_directory}/auth/kubeconfig)
sed -i s/${random_id.randomId.hex}/$CLUSTERID/g ${local.ocptemplates}/machine-autoscaler-${var.single-or-multi-zone}.yaml
oc create -f ${local.ocptemplates}/cluster-autoscaler.yaml --kubeconfig ${self.triggers.ocp_directory}/auth/kubeconfig
oc create -f ${local.ocptemplates}/machine-autoscaler-${var.single-or-multi-zone}.yaml --kubeconfig ${self.triggers.ocp_directory}/auth/kubeconfig
EOF
  }
  depends_on = [
    null_resource.install_openshift,
    local_file.clusterautoscaler_yaml,
    local_file.clusterautoscaler_yaml,
    local_file.machineautoscaler_yaml
  ]
}


# module "portworx" {
#   count                   = var.storage == "portworx" ? 1 : 0
#   source                  = "../portworx"
#   openshift_api           = var.openshift_api
#   openshift_username      = var.openshift-username
#   openshift_password      = var.openshift-password
#   openshift_token         = ""
#   installer_workspace     = local.installer_workspace
#   region                  = var.region
#   storage                 = var.storage
#   portworx-encryption     = var.portworx-encryption
#   portworx-encryption-key = var.portworx-encryption-key
#   portworx-spec-url       = var.portworx-spec-url

#   depends_on = [
#     null_resource.install_openshift,
#     null_resource.openshift_post_install,
#   ]
# }

# module "ocs" {
#   count                = var.storage == "ocs" ? 1 : 0
#   source               = "../ocs"
#   openshift_api        = var.openshift_api
#   openshift_username   = var.openshift-username
#   openshift_password   = var.openshift-password
#   openshift_token      = ""
#   installer_workspace  = local.installer_workspace
#   region               = var.region
#   storage              = var.storage
#   single-or-multi-zone = var.single-or-multi-zone
#   master-subnet-name   = var.master-subnet-name
#   worker-subnet-name   = var.worker-subnet-name
#   virtual-network-name = var.virtual-network-name
#   resource-group       = var.resource-group

#   depends_on = [
#     null_resource.install_openshift,
#     null_resource.openshift_post_install,
#   ]
# }

# resource "null_resource" "install_nfs_client" {
#   count = var.storage == "nfs" ? 1 : 0
#   triggers = {
#     username = var.admin-username
#   }
#   provisioner "local-exec" {
#     command = <<EOF
# oc adm policy add-scc-to-user hostmount-anyuid system:serviceaccount:kube-system:nfs-client-provisioner
# oc process -f ${local.ocptemplates}/nfs-template.yaml | oc create -n kube-system -f -
# EOF
#   }
#   depends_on = [
#     null_resource.install_openshift,
#     null_resource.openshift_post_install,
#     local_file.nfs-template_yaml
#   ]
# }