variable "openshift_api" {
  type = string
}

variable "openshift_username" {
  type = string
}

variable "openshift_password" {
  type = string
}

variable "openshift_token" {
  type        = string
  description = "For cases where you don't have the password but a token can be generated (e.g SSO is being used)"
}

variable "installer_workspace" {
  type        = string
  description = "Folder to store/find the installation files"
}

variable "region" {
  type = string
  description = "AWS Region the cluster is deployed in"
}


variable "portworx_enterprise" {
  type = map(string)
  description = "See PORTWORX.md on how to get the Cluster ID."
  default = {
    enable = false
    cluster_id = ""
    enable_encryption = true
  }
}

variable "portworx_essentials" {
  type = map(string)
  description = "See PORTWORX-ESSENTIALS.md on how to get the Cluster ID, User ID and OSB Endpoint"
  default = {
    enable = false
    cluster_id = ""
    user_id = ""
    osb_endpoint = ""
  }
}

variable "portworx_ibm" {
  type = map(string)
  description = "Currently only works on a RHEL machine! This is the IBM freemium version of Portworx. It is limited to 5TB and 5Nodes"
  default = {
    enable = false
    ibm_px_package_path = "" # absolute file path to the folder containing the cpd*-portworx*.tgz package
  }
}

variable "disk_size" {
  description = "Disk size for each Portworx volume"
  default = 1000
}

variable "kvdb_disk_size" {
  default = 450
}

variable "px_enable_monitoring" {
  type = bool
  default = true
  description = "Enable monitoring on PX"
}

variable "px_enable_csi" {
  type = bool
  default = true
  description = "Enable CSI on PX"
}

variable "aws_access_key_id" {
  type = string
}

variable "aws_secret_access_key" {
  type = string
}