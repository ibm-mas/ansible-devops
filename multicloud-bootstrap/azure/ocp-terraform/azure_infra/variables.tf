## Azure Auth
variable "azure-subscription-id" {

}

variable "azure-client-id" {

}

variable "azure-client-secret" {

}

variable "azure-tenant-id" {

}

variable "region" {
  default = "centralus"
}

variable "resource-group" {

}

variable "existing-resource-group" {
  default = "no"
}

variable "cluster-name" {

}

# Resource group the DNS group was created in
variable "dnszone-resource-group" {
}

# DNS Zone created in Step 1 of the Readme
variable "dnszone" {
}

variable "admin-username" {
  default = "core"
}

### Network Config
variable "new-or-existing" {
  default = "new"
}

variable "existing-vnet-resource-group" {
  default = "vnet-rg"
}

variable "virtual-network-name" {
  default = "ocpfourx-vnet"
}

variable "virtual-network-cidr" {
  default = "10.0.0.0/16"
}


variable "master-subnet-name" {
  default = "master-subnet"
}

variable "master-subnet-cidr" {
  default = "10.0.1.0/24"
}

variable "worker-subnet-name" {
  default = "worker-subnet"
}

variable "worker-subnet-cidr" {
  default = "10.0.2.0/24"
}

#Bastion host variable 
variable "bastion_cidr" {
  default = "10.0.3.224/27"
}
# Deploy OCP into single or multi-zone
variable "single-or-multi-zone" {
  default = "single"
}

# Applicable only if deploying in a single zone
variable "zone" {
  default = 1
}

variable "master-node-count" {
  default = 3
}

variable "worker-node-count" {
  default = 3
}


variable "master-instance-type" {
  default = "Standard_D8s_v3"
}

variable "worker-instance-type" {
  default = "Standard_D16s_v3"
}

variable "pull-secret-file-path" {
}

variable "fips" {
  default = false
}

variable "clusterAutoscaler" {
  default = "no"
}

variable "openshift-username" {
  default = "ocadmin"
}

variable "openshift-password" {
sensitive = true
}

variable "openshift_api" {
  type    = string
  default = ""
}

variable "ssh-public-key" {

}

# Internet facing endpoints
variable "private-or-public-cluster" {
  default = "public"
}
#For MAS keeping storage as ocs 
#Other options are portworx and nfs
variable "storage" {
  default = "ocs"
}

variable "portworx-spec-url" {
  default = ""
}

variable "portworx-encryption" {
  default = "no"
}

variable "portworx-encryption-key" {
  default = ""
}

variable "storage-disk-size" {
  default = 1024
}

variable "enableNFSBackup" {
  default = "no"
}

# Openshift namespace/project to deploy cloud pak into

variable "cpd-external-registry" {
  description = "URL to external registry for CPD install. Note: CPD images must already exist in the repo"
  default     = "cp.icr.io"
}

variable "cpd-external-username" {
  description = "URL to external username for CPD install. Note: CPD images must already exist in the repo"
  default     = "cp"
}
variable "ocp_version" {
  default = "4.8.11"
}


variable "openshift_installer_url_prefix" {
  type    = string
  default = "https://mirror.openshift.com/pub/openshift-v4/clients/ocp"
}

variable "cloudctl_version" {
  default = "v3.8.0"
}

# variable "apikey" {
# }

variable "accept-cpd-license" {
  description = "Read and accept license at https://ibm.biz/BdqSw4"
  default     = "reject"
}

##############################
### CPD4.0 variables
##############################

variable "cpd-namespace" {
  default = "zen"
}

variable "operator-namespace" {
  default = "ibm-common-services"
}

variable "cpd_storageclass" {
  type = map(any)

  default = {
    "portworx" = "portworx-shared-gp3"
    "ocs"      = "ocs-storagecluster-cephfs"
    "nfs"      = "nfs"
  }
}

variable "rwo_cpd_storageclass" {
  type = map(any)

  default = {
    "portworx" = "portworx-db2-rwo-sc"
    "ocs"      = "ocs-storagecluster-ceph-rbd"
    "nfs"      = "nfs"
  }
}
############################################
# CPD 4.0 service variables 
###########################################
variable "cpd_platform" {
  type = map(string)
  default = {
    enable  = "yes"
    version = "4.0.2"
    channel = "v2.0"
  }
}

variable "data_virtualization" {
  type = map(string)
  default = {
    enable  = "no"
    version = "1.7.2"
    channel = "v1.7"
  }
}

variable "analytics_engine" {
  type = map(string)
  default = {
    enable  = "no"
    version = "4.0.2"
    channel = "stable-v1"
  }
}

variable "watson_knowledge_catalog" {
  type = map(string)
  default = {
    enable  = "no"
    version = "4.0.2"
    channel = "v1.0"
  }
}

variable "watson_studio" {
  type = map(string)
  default = {
    enable  = "no"
    version = "4.0.2"
    channel = "v2.0"
  }
}

variable "watson_machine_learning" {
  type = map(string)
  default = {
    enable  = "no"
    version = "4.0.2"
    channel = "v1.1"
  }
}

variable "watson_ai_openscale" {
  type = map(string)
  default = {
    enable  = "no"
    version = "4.0.2"
    channel = "v1"
  }
}

variable "spss_modeler" {
  type = map(string)
  default = {
    enable  = "no"
    version = "4.0.2"
    channel = "v1.0"
  }
}

variable "cognos_dashboard_embedded" {
  type = map(string)
  default = {
    enable  = "no"
    version = "4.0.2"
    channel = "v1.0"
  }
}

variable "datastage" {
  type = map(string)
  default = {
    enable  = "no"
    version = "4.0.2"
    channel = "v1.0"
  }
}

variable "db2_warehouse" {
  type = map(string)
  default = {
    enable  = "no"
    version = "4.0.2"
    channel = "v1.0"
  }
}

variable "db2_oltp" {
  type = map(string)
  default = {
    enable  = "no"
    version = "4.0.2"
    channel = "v1.0"
  }
}

variable "cognos_analytics" {
  type = map(string)
  default = {
    enable  = "no"
    version = "4.0.2"
    channel = "v4.0"
  }
}

variable "data_management_console" {
  type = map(string)
  default = {
    enable  = "no"
    version = "4.0.2"
    channel = "v1.0"
  }
}

variable "master_data_management" {
  type = map(string)
  default = {
    enable  = "no"
    version = "4.0.2"
    channel = "v1.1"
  }
}

variable "db2_aaservice" {
  type = map(string)
  default = {
    enable  = "no"
    version = "4.0.2"
    channel = "v1.0"
  }
}

variable "decision_optimization" {
  type = map(string)
  default = {
    enable  = "no"
    version = "4.0.2"
    channel = "v4.0"
  }
}

variable "bigsql" {
  type        = map(string)
  default = {
    enable   = "no"
    version  = "7.2.2"
    channel  = "v7.2"
  }
}
