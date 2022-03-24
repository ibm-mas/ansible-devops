locals {
  classic_lb_timeout = 600
  installer_workspace     = "${path.root}/installer-files"
  openshift_installer_url = "${var.openshift_installer_url}/${var.openshift_version}"
}

resource "null_resource" "download_binaries" {
  triggers = {
    installer_workspace = local.installer_workspace
  }
  provisioner "local-exec" {
    when    = create
    command = <<EOF
test -e ${self.triggers.installer_workspace} || mkdir ${self.triggers.installer_workspace}
case $(uname -s) in
  Darwin)
    wget -r -l1 -np -nd -q ${local.openshift_installer_url} -P ${self.triggers.installer_workspace} -A 'openshift-install-mac-4*.tar.gz'
    tar zxvf ${self.triggers.installer_workspace}/openshift-install-mac-4*.tar.gz -C ${self.triggers.installer_workspace}
    wget -r -l1 -np -nd -q ${local.openshift_installer_url} -P ${self.triggers.installer_workspace} -A 'openshift-client-mac-4*.tar.gz'
    tar zxvf ${self.triggers.installer_workspace}/openshift-client-mac-4*.tar.gz -C ${self.triggers.installer_workspace}
    ;;
  Linux)
    wget -r -l1 -np -nd -q ${local.openshift_installer_url}/openshift-install-linux-${var.openshift_version}.tar.gz -P ${self.triggers.installer_workspace}
    tar zxvf ${self.triggers.installer_workspace}/openshift-install-linux-4*.tar.gz -C ${self.triggers.installer_workspace}
    wget -r -l1 -np -nd -q ${local.openshift_installer_url}/openshift-client-linux-${var.openshift_version}.tar.gz -P ${self.triggers.installer_workspace}
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

resource "null_resource" "install_openshift" {
  triggers = {
    installer_workspace = local.installer_workspace
  }
  provisioner "local-exec" {
    when    = create
    command = <<EOF
cd ${self.triggers.installer_workspace} && ./openshift-install create cluster --log-level=debug
EOF
  }
  provisioner "local-exec" {
    when    = destroy
    command = <<EOF
cd ${self.triggers.installer_workspace} && ./openshift-install destroy cluster --log-level=debug
sleep 5
EOF
  }
  depends_on = [
    null_resource.download_binaries,
    local_file.install_config_yaml,
  ]
}

resource "local_file" "aws_nlb_yaml" {
  content  = data.template_file.aws_nlb.rendered
  filename = "${local.installer_workspace}/aws_nlb.yaml"
}

resource "null_resource" "change_clb_to_nlb" {
  triggers = {
    installer_workspace = local.installer_workspace
  }
  provisioner "local-exec" {
    command =<<EOF
#oc replace --force --wait -f ${self.triggers.installer_workspace}/aws_nlb.yaml --kubeconfig ${self.triggers.installer_workspace}/auth/kubeconfig
#echo "Sleeping 10mins to create new network load balancer"
#sleep 600
EOF
}
  depends_on = [
    null_resource.install_openshift,
    local_file.aws_nlb_yaml,
  ]
}

resource "null_resource" "create_openshift_user" {
  triggers = {
    installer_workspace = local.installer_workspace
  }
  provisioner "local-exec" {
    command = <<EOF
htpasswd -c -B -b /tmp/.htpasswd '${var.openshift_username}' '${var.openshift_password}'
sleep 30
oc create secret generic htpass-secret --from-file=htpasswd=/tmp/.htpasswd -n openshift-config --kubeconfig ${self.triggers.installer_workspace}/auth/kubeconfig
oc apply -f ${self.triggers.installer_workspace}/htpasswd.yaml --kubeconfig ${self.triggers.installer_workspace}/auth/kubeconfig
oc adm policy add-cluster-role-to-user cluster-admin '${var.openshift_username}' --kubeconfig ${self.triggers.installer_workspace}/auth/kubeconfig
sleep 60
EOF
  }

  /* provisioner "local-exec" {
    when = destroy
    command = <<EOF
rm -f /tmp/.htpasswd
oc delete secret htpass-secret -n openshift-config --kubeconfig ${self.triggers.installer_workspace}/auth/kubeconfig
oc delete -f ${self.triggers.installer_workspace}/htpasswd.yaml --kubeconfig ${self.triggers.installer_workspace}/auth/kubeconfig
EOF
  } */
  depends_on = [
    null_resource.download_binaries,
    null_resource.install_openshift,
    null_resource.change_clb_to_nlb,
    local_file.htpasswd_yaml,
  ]
}

resource "null_resource" "enable_autoscaler" {
  count = var.enable_autoscaler ? 1 : 0
  triggers = {
    installer_workspace     = local.installer_workspace
  }
  provisioner "local-exec" {
    when = create
    command = <<EOF
echo "Creating Cluster Autoscaler"
oc create -f ${self.triggers.installer_workspace}/cluster_autoscaler.yaml --kubeconfig ${self.triggers.installer_workspace}/auth/kubeconfig
CLUSTERID=$(oc get machineset -n openshift-machine-api --kubeconfig ${self.triggers.installer_workspace}/auth/kubeconfig -o jsonpath='{.items[0].metadata.labels.machine\.openshift\.io/cluster-api-cluster}')
sed -i -e s/CLUSTERID/$CLUSTERID/g ${self.triggers.installer_workspace}/machine_autoscaler.yaml
echo "Creating Machine Autoscaler"
oc create -f ${self.triggers.installer_workspace}/machine_autoscaler.yaml --kubeconfig ${self.triggers.installer_workspace}/auth/kubeconfig
echo "Creating Machine Health Check"
sed -i -e s/CLUSTERID/$CLUSTERID/g ${self.triggers.installer_workspace}/machine_health_check.yaml
oc create -f ${self.triggers.installer_workspace}/machine_health_check.yaml --kubeconfig ${self.triggers.installer_workspace}/auth/kubeconfig
EOF
  }

  /* provisioner "local-exec" {
    when = destroy
    command = <<EOF
echo "Deleting Machine Health Check"
oc delete -f ${self.triggers.installer_workspace}/machine_health_check.yaml --kubeconfig ${self.triggers.installer_workspace}/auth/kubeconfig
echo "Deleting Machine Autoscaler"
oc delete -f ${self.triggers.installer_workspace}/machine_autoscaler.yaml --kubeconfig ${self.triggers.installer_workspace}/auth/kubeconfig
echo "Deleting Cluster Autoscaler"
oc delete -f ${self.triggers.installer_workspace}/cluster_autoscaler.yaml --kubeconfig ${self.triggers.installer_workspace}/auth/kubeconfig
EOF
  } */
  depends_on = [
    local_file.cluster_autoscaler_yaml,
    local_file.machine_autoscaler_yaml,
    local_file.machine_health_check_yaml,
    null_resource.download_binaries,
    null_resource.install_openshift,
    null_resource.change_clb_to_nlb,
  ]
}

resource "null_resource" "configure_image_registry" {
  triggers = {
    installer_workspace     = local.installer_workspace
  }
  provisioner "local-exec" {
    command =<<EOF
oc patch configs.imageregistry.operator.openshift.io/cluster --type merge -p '{"spec":{"defaultRoute":true,"replicas":3}}' -n openshift-image-registry --kubeconfig ${self.triggers.installer_workspace}/auth/kubeconfig
oc patch svc/image-registry -p '{"spec":{"sessionAffinity": "ClientIP"}}' -n openshift-image-registry --kubeconfig ${self.triggers.installer_workspace}/auth/kubeconfig
oc patch configs.imageregistry.operator.openshift.io/cluster --type merge -p '{"spec":{"managementState":"Unmanaged"}}' --kubeconfig ${self.triggers.installer_workspace}/auth/kubeconfig
echo 'Sleeping for 3m'
sleep 3m
oc annotate route default-route haproxy.router.openshift.io/timeout=600s -n openshift-image-registry --kubeconfig ${self.triggers.installer_workspace}/auth/kubeconfig
oc set env deployment/image-registry -n openshift-image-registry REGISTRY_STORAGE_S3_CHUNKSIZE=1048576000 --kubeconfig ${self.triggers.installer_workspace}/auth/kubeconfig

sleep 2m
bash ocp/scripts/update-elb-timeout.sh ${var.vpc_id} ${local.classic_lb_timeout}
EOF
  }
  depends_on = [
    null_resource.install_openshift,
    null_resource.change_clb_to_nlb,
  ]
}