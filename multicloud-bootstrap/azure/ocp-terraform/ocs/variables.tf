variable "region" {
  type        = string
  description = "Azure Region the cluster is deployed in"
}

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

variable "storage" {

}

variable "single-or-multi-zone" {

}

variable "master-subnet-name" {
}

variable "worker-subnet-name" {
}

variable "virtual-network-name" {
}

variable "resource-group" {

}