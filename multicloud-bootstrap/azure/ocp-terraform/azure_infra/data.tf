locals {
  cidr-prefix = split(".", var.virtual-network-cidr)[0]
}

data "template_file" "azurecreds" {
  template = file("../openshift_module/osServicePrincipal.tpl.json")
  vars = {
    subscription-id = var.azure-subscription-id
    client-id       = var.azure-client-id
    client-secret   = var.azure-client-secret
    tenant-id       = var.azure-tenant-id
  }
}

data "template_file" "installconfig" {
  template = file("../openshift_module/${local.install-config-file}")
  vars = {
    baseDomainResourceGroupName = var.dnszone-resource-group
    region                      = var.region
    pullSecret                  = file(var.pull-secret-file-path)
    sshKey                      = var.ssh-public-key
    baseDomain                  = var.dnszone
    worker-instance-type        = var.worker-instance-type
    master-instance-type        = var.master-instance-type
    clustername                 = var.cluster-name
    virtualNetwork              = var.virtual-network-name
    controlPlaneSubnet          = var.master-subnet-name
    computeSubnet               = var.worker-subnet-name
    networkResourceGroupName    = local.resource-group

    cluster-network-cidr = "${local.cidr-prefix}.128.0.0/14"
    host-prefix          = 23
    virtual-network-cidr = var.virtual-network-cidr
    service-network-cidr = "192.30.0.0/16"

    private-public = var.private-or-public-cluster == "public" ? "External" : "Internal"

    deploymentZone  = var.zone
    workerNodeCount = var.worker-node-count
    masterNodeCount = var.master-node-count

    fips = var.fips
  }
}

data "template_file" "clusterautoscaler" {
  template = file("../openshift_module/cluster-autoscaler.tpl.yaml")
  vars = {
    max-total-nodes     = 24
    pod-priority        = -10
    min-cores           = 47  # valid per cluster
    max-cores           = 128 # valid per cluster
    min-memory          = 64  # valid per node
    max-memory          = 256 # valid per node
    scaledown-enabled   = true
    delay-after-add     = "3m"
    delay-after-delete  = "2m"
    delay-after-failure = "30s"
    unneeded-time       = "60s"
  }
}

data "template_file" "machineautoscaler" {
  template = file("../openshift_module/${local.machine-autoscaler-file}")
  vars = {
    clusterid       = random_id.randomId.hex
    region          = var.region
    zone            = var.zone
    workerNodeCount = var.worker-node-count
  }
}

data "template_file" "machine-health-check" {
  template = file("../openshift_module/${local.machine-health-check-file}")
  vars = {
    clusterid = random_id.randomId.hex
    region    = var.region
    zone      = var.zone
  }
}

data "template_file" "htpasswd" {
  template = file("../openshift_module/auth.yaml")
}

# data "template_file" "nfs-template" {
#   count    = var.storage == "nfs" ? 1 : 0
#   template = file("../nfs_module/nfs-template.tpl.yaml")
#   vars = {
#     nfsserver = azurerm_network_interface.nfs[count.index].private_ip_address
#     nfspath   = "/exports/home"
#   }
# }

data "template_file" "registry-conf" {
  template = file("../openshift_module/registries.tpl.conf")
  vars = {
    registry-route = "default-route-openshift-image-registry.apps.${var.cluster-name}.${var.dnszone}"
  }
}

data "template_file" "registry-mc" {
  template = file("../openshift_module/insecure-registry-machineconfig.yaml")
  vars = {
    config-data = base64encode(data.template_file.registry-conf.rendered)
  }
}

data "template_file" "crio-mc" {
  template = file("../openshift_module/crio-machineconfig.yaml")
  vars = {
    crio-config-data = base64encode(file("../openshift_module/crio.conf"))
  }
}

data "template_file" "limits-mc" {
  template = file("../openshift_module/limits-machineconfig.yaml")
  vars = {
    limits-config-data = base64encode(file("../openshift_module/limits.conf"))
  }
}

data "template_file" "sysctl-mc" {
  template = file("../openshift_module/sysctl-machineconfig.yaml")
  vars = {
    sysctl-config-data = base64encode(file("../openshift_module/sysctl.conf"))
  }
}

data "template_file" "chrony-mc" {
  template = file("../openshift_module/chrony-machineconfig.yaml")
  vars = {
    chrony-config-data = base64encode(file("../openshift_module/chrony.conf"))
  }
}

data "template_file" "multipath-mc" {
  template = file("../openshift_module/multipath-machineconfig.yaml")
  vars = {
    multipath-config-data = base64encode(file("../openshift_module/multipath.conf"))
  }
}