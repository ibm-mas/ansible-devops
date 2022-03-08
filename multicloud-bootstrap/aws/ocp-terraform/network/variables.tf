###############################################################################
# 1. Leave it as it is if you don't want to provide Availability zone values, #
#    in that case it will be automatically selected based on the region.      #
# 2. For single_zone installation, provide only availability-zone1 value.     #
###############################################################################

variable "availability_zone1" {
  description = "example eu-west-2a"
  default     = ""
}

variable "availability_zone2" {
  description = "example eu-west-2b"
  default     = ""
}

variable "availability_zone3" {
  description = "example eu-west-2c"
  default     = ""
}
################################################################################

variable "vpc_cidr" {
  description = "The CIDR block for the VPC, e.g: 10.0.0.0/16"
  default     = "10.0.0.0/16"
}

variable "master_subnet_cidr1" {
  default = "10.0.0.0/20"
}

variable "master_subnet_cidr2" {
  default = "10.0.16.0/20"
}

variable "master_subnet_cidr3" {
  default = "10.0.32.0/20"
}

variable "worker_subnet_cidr1" {
  default = "10.0.128.0/20"
}

variable "worker_subnet_cidr2" {
  default = "10.0.144.0/20"
}

variable "worker_subnet_cidr3" {
  default = "10.0.160.0/20"
}

variable "network_tag_prefix" {
  type        = string
  description = "Network tag prefix to identify VPC. Tag will then become 'tag-vpc' "
}

variable "tenancy" {
  type        = string
  description = "Amazon EC2 instances tenancy type, default/dedicated"
  default     = "default"
}

# Enter the number of availability zones the cluster is to be deployed, default is multi zone deployment.
variable "az" {
  description = "single_zone / multi_zone"
  default     = "multi_zone"
}
