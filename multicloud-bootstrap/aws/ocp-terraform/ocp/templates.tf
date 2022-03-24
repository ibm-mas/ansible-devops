data "template_file" "install_config_yaml" {
  template = <<EOF
apiVersion: v1
baseDomain: ${var.base_domain}
credentialsMode: Mint
compute:
- hyperthreading: Enabled
  name: worker
  platform:
    aws:
      zones:
      - ${var.availability_zone1}%{if var.multi_zone}${indent(6, "\n- ${var.availability_zone2}\n- ${var.availability_zone3}")}%{endif}
      type: ${var.worker_instance_type}
      rootVolume:
        iops: ${var.worker_instance_volume_iops}
        size: ${var.worker_instance_volume_size}
        type: ${var.worker_instance_volume_type}
  replicas: ${var.worker_replica_count}
controlPlane:
  hyperthreading: Enabled
  name: master
  platform:
    aws:
      zones:
      - ${var.availability_zone1}%{if var.multi_zone}${indent(6, "\n- ${var.availability_zone2}\n- ${var.availability_zone3}")}%{endif}
      type: ${var.master_instance_type}
      rootVolume:
        iops: ${var.master_instance_volume_iops}
        size: ${var.master_instance_volume_size}
        type: ${var.master_instance_volume_type}
  replicas: ${var.master_replica_count}
metadata:
  name: ${var.cluster_name}
networking:
  clusterNetwork:
  - cidr: ${var.cluster_network_cidr}
    hostPrefix: ${var.cluster_network_host_prefix}
  machineNetwork:
  - cidr: ${var.machine_network_cidr}
  networkType: OpenShiftSDN
  serviceNetwork:
  - ${var.service_network_cidr}
platform:
  aws:
    region: ${var.region}
    subnets:
    - ${var.master_subnet1_id}%{if var.multi_zone}${indent(4, "\n- ${var.master_subnet2_id}\n- ${var.master_subnet3_id}")}%{endif}
    - ${var.worker_subnet1_id}%{if var.multi_zone}${indent(4, "\n- ${var.worker_subnet2_id}\n- ${var.worker_subnet3_id}")}%{endif}
publish: ${var.private_cluster ? "Internal" : "External"}
pullSecret: '${chomp(file(var.openshift_pull_secret_file_path))}'
sshKey: '${var.public_ssh_key}'
fips: ${var.enable_fips}
EOF
}

data "template_file" "htpasswd" {
  template = <<EOF
apiVersion: config.openshift.io/v1
kind: OAuth
metadata:
  name: cluster
spec:
  tokenConfig:
    accessTokenMaxAgeSeconds: 172800
  identityProviders:
  - name: htpasswdProvider 
    challenge: true 
    login: true 
    mappingMethod: claim 
    type: HTPasswd
    htpasswd:
      fileData:
        name: htpass-secret
EOF
}

resource "local_file" "install_config_yaml" {
  content  = data.template_file.install_config_yaml.rendered
  filename = "${local.installer_workspace}/install-config.yaml"
  depends_on = [
    null_resource.download_binaries,
  ]
}

resource "local_file" "htpasswd_yaml" {
  content  = data.template_file.htpasswd.rendered
  filename = "${local.installer_workspace}/htpasswd.yaml"
}

data "template_file" "cluster_autoscaler" {
  template =<<EOF
apiVersion: "autoscaling.openshift.io/v1"
kind: "ClusterAutoscaler"
metadata:
  name: "default"
spec:
  podPriorityThreshold: -10
  resourceLimits:
    maxNodesTotal: 24
    cores:
      min: 48
      max: 128
    memory:
      min: 128
      max: 512
  scaleDown:
    enabled: true
    delayAfterAdd: "3m"
    delayAfterDelete: "2m"
    delayAfterFailure: "3m"
    unneededTime: "300m"
EOF
}

resource "local_file" "cluster_autoscaler_yaml" {
  content  = data.template_file.cluster_autoscaler.rendered
  filename = "${local.installer_workspace}/cluster_autoscaler.yaml"
}
locals {
  machine_autoscaler_min_replica = var.multi_zone ? 1 : var.worker_replica_count
}
data "template_file" "machine_autoscaler" {
  template =<<EOF
---
kind: MachineAutoscaler
apiVersion: "autoscaling.openshift.io/v1beta1"
metadata:
  name: "CLUSTERID-worker-${var.availability_zone1}"
  namespace: "openshift-machine-api"
spec:
  minReplicas: ${local.machine_autoscaler_min_replica}
  maxReplicas: 12
  scaleTargetRef:
    apiVersion: machine.openshift.io/v1beta1
    kind: MachineSet
    name: "CLUSTERID-worker-${var.availability_zone1}"
%{if var.multi_zone}
---
kind: MachineAutoscaler
apiVersion: "autoscaling.openshift.io/v1beta1"
metadata:
  name: "CLUSTERID-worker-${var.availability_zone2}"
  namespace: "openshift-machine-api"
spec:
  minReplicas: 1
  maxReplicas: 12
  scaleTargetRef:
    apiVersion: machine.openshift.io/v1beta1
    kind: MachineSet
    name: "CLUSTERID-worker-${var.availability_zone2}"
---
kind: MachineAutoscaler
apiVersion: "autoscaling.openshift.io/v1beta1"
metadata:
  name: "CLUSTERID-worker-${var.availability_zone3}"
  namespace: "openshift-machine-api"
spec:
  minReplicas: 1
  maxReplicas: 12
  scaleTargetRef:
    apiVersion: machine.openshift.io/v1beta1
    kind: MachineSet
    name: "CLUSTERID-worker-${var.availability_zone3}"
%{endif}
EOF
}

resource "local_file" "machine_autoscaler_yaml" {
  content  = data.template_file.machine_autoscaler.rendered
  filename = "${local.installer_workspace}/machine_autoscaler.yaml"
}

data "template_file" "machine_health_check" {
  template = <<EOF
---
apiVersion: machine.openshift.io/v1beta1
kind: MachineHealthCheck
metadata:
  name: machine-health-check-worker1-${var.availability_zone1}
  namespace: openshift-machine-api
spec:
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-machine-role: worker
      machine.openshift.io/cluster-api-machine-type: worker
      machine.openshift.io/cluster-api-machineset: CLUSTERID-worker-${var.availability_zone1}
  unhealthyConditions:
  - type:    "Ready"
    timeout: "300s"
    status: "False"
  - type:    "Ready"
    timeout: "300s"
    status: "Unknown"
  maxUnhealthy: "40%"
%{if var.multi_zone}
---
apiVersion: machine.openshift.io/v1beta1
kind: MachineHealthCheck
metadata:
  name: machine-health-check-worker2-${var.availability_zone2}
  namespace: openshift-machine-api
spec:
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-machine-role: worker
      machine.openshift.io/cluster-api-machine-type: worker
      machine.openshift.io/cluster-api-machineset: CLUSTERID-worker-${var.availability_zone2}
  unhealthyConditions:
  - type:    "Ready"
    timeout: "300s"
    status: "False"
  - type:    "Ready"
    timeout: "300s"
    status: "Unknown"
  maxUnhealthy: "40%"
---
apiVersion: machine.openshift.io/v1beta1
kind: MachineHealthCheck
metadata:
  name: machine-health-check-worker3-${var.availability_zone3}
  namespace: openshift-machine-api
spec:
  selector:
    matchLabels:
      machine.openshift.io/cluster-api-machine-role: worker
      machine.openshift.io/cluster-api-machine-type: worker
      machine.openshift.io/cluster-api-machineset: CLUSTERID-worker-${var.availability_zone3}
  unhealthyConditions:
  - type:    "Ready"
    timeout: "300s"
    status: "False"
  - type:    "Ready"
    timeout: "300s"
    status: "Unknown"
  maxUnhealthy: "40%"
%{endif}
EOF
}

resource "local_file" "machine_health_check_yaml" {
  content  = data.template_file.machine_health_check.rendered
  filename = "${local.installer_workspace}/machine_health_check.yaml"
}

data "template_file" "aws_nlb" {
  template =<<EOF
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  name: default
  namespace: openshift-ingress-operator
spec:
  endpointPublishingStrategy:
    type: LoadBalancerService
    loadBalancer:
      scope: ${var.private_cluster ? "Internal" : "External"}
      providerParameters:
        type: AWS
        aws:
          type: NLB
EOF
}