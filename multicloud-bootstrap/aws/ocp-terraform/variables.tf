##### AWS Configuration #####
variable "region" {
  description = "The region to deploy the cluster in, e.g: us-west-2."
  default     = "<REGION>"
}

variable "key_name" {
  description = "The name of the key to user for ssh access, e.g: consul-cluster"
  default     = "openshift-key"
}

variable "tenancy" {
  description = "Amazon EC2 instances tenancy type, default/dedicated"
  default     = "default"
}

variable "access_key_id" {
  type        = string
  description = "Access Key ID for the AWS account"
}

variable "secret_access_key" {
  type        = string
  description = "Secret Access Key for the AWS account"
  sensitive = true
}

variable "new_or_existing_vpc_subnet" {
  description = "For existing VPC and SUBNETS use 'exist' otherwise use 'new' to create new VPC and SUBNETS, default is 'new' "
  default     = "new"
}

##############################
# New Network
##############################
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

##############################
# Existing Network
##############################
variable "vpc_id" {
  default = ""
}
variable "master_subnet1_id" {
  default = ""
}

variable "master_subnet2_id" {
  default = ""
}

variable "master_subnet3_id" {
  default = ""
}

variable "worker_subnet1_id" {
  default = ""
}

variable "worker_subnet2_id" {
  default = ""
}

variable "worker_subnet3_id" {
  default = ""
}
#############################

variable "enable_permission_quota_check" {
  default = true
}

variable "cluster_name" {
  description = "Name of OCP cluster"
}


# Enter the number of availability zones the cluster is to be deployed, default is single zone deployment.
variable "az" {
  description = "single_zone / multi_zone"
  default     = "multi_zone"
}

variable "availability_zone1" {
  description = "Availability zone 1"
}

variable "availability_zone2" {
  description = "Availability zone 2"
}

variable "availability_zone3" {
  description = "Availability zone 3"
}

#######################################
# Existing Openshift Cluster Variables
#######################################
variable "existing_cluster" {
  type        = bool
  description = "Set true if you already have a running Openshift Cluster and you only want to install CPD."
  default     = false
}

variable "existing_openshift_api" {
  type    = string
  default = ""
}

variable "existing_openshift_username" {
  type    = string
  default = ""
}

variable "existing_openshift_password" {
  type    = string
  default = ""
  sensitive = true
}

variable "existing_openshift_token" {
  type    = string
  default = ""
  sensitive = true
}
##################################

##################################
# New Openshift Cluster Variables
##################################
variable "worker_instance_type" {
  type    = string
  default = "m5.4xlarge"
}

variable "worker_instance_volume_iops" {
  type    = number
  default = 2000
}

variable "worker_instance_volume_size" {
  type    = number
  default = 300
}

variable "worker_instance_volume_type" {
  type    = string
  default = "io1"
}

variable "worker_replica_count" {
  type    = number
  default = 3
}

variable "master_instance_type" {
  type    = string
  default = "m5.2xlarge"
}

variable "master_instance_volume_iops" {
  type    = number
  default = 4000
}

variable "master_instance_volume_size" {
  type    = number
  default = 300
}

variable "master_instance_volume_type" {
  type    = string
  default = "io1"
}

variable "master_replica_count" {
  type    = number
  default = 3
}

variable "cluster_network_cidr" {
  type    = string
  default = "10.128.0.0/14"
}

variable "cluster_network_host_prefix" {
  type    = number
  default = 23
}

variable "service_network_cidr" {
  type    = string
  default = "172.30.0.0/16"
}

variable "private_cluster" {
  type        = bool
  description = "Endpoints should resolve to Private IPs"
  default     = false
}

variable "openshift_pull_secret_file_path" {
  type = string
}

variable "public_ssh_key" {
  type = string
}

variable "enable_fips" {
  type    = bool
  default = false
}

variable "base_domain" {
  type = string
}

variable "openshift_username" {
  type = string
}

variable "openshift_password" {
  type = string
  sensitive = true
}

variable "enable_autoscaler" {
  type    = bool
  default = false
}

######################################
# Storage Options: Enable only one   #
######################################
variable "ocs" {
  type = map(string)
  default = {
    enable                       = true
    ami_id                       = ""
    dedicated_node_instance_type = "m5.4xlarge"
  }
}

variable "portworx_enterprise" {
  type        = map(string)
  description = "See PORTWORX.md on how to get the Cluster ID."
  default = {
    enable            = false
    cluster_id        = ""
    enable_encryption = true
  }
}

variable "portworx_essentials" {
  type        = map(string)
  description = "See PORTWORX-ESSENTIALS.md on how to get the Cluster ID, User ID and OSB Endpoint"
  default = {
    enable       = false
    cluster_id   = ""
    user_id      = ""
    osb_endpoint = ""
  }
}

variable "portworx_ibm" {
  type        = map(string)
  description = "This is the IBM freemium version of Portworx. It is limited to 5TB and 5Nodes"
  default = {
    enable              = false
    ibm_px_package_path = "" # absolute file path to the folder containing the cpd*-portworx*.tgz package
  }
}

##################################################

variable "accept_cpd_license" {
  description = "Read and accept license at https://www14.software.ibm.com/cgi-bin/weblap/lap.pl?li_formnum=L-DNAA-BZTPEW, (accept / reject)"
  default     = "reject"
}

variable "cpd_external_registry" {
  description = "URL to external registry for CPD install. Note: CPD images must already exist in the repo"
  default     = "cp.icr.io"
}

variable "cpd_external_username" {
  description = "URL to external username for CPD install. Note: CPD images must already exist in the repo"
  default     = "cp"
}

variable "cpd_api_key" {
  description = "Repository APIKey or Registry password"
}

variable "cpd_namespace" {
  description = "Openshift Namespace to deploy CPD into"
  default     = "zen"
}

variable "cloudctl_version" {
  default = "v3.7.1"
}

variable "openshift_version" {
  description = "OCP Version"
  default     = "4.8.24"
}

variable "cpd_platform" {
  type        = map(string)
  default = {
    enable   = "yes"
    version  = "4.0.2"
    channel  = "v2.0"
  }
}

variable "data_virtualization" {
  type        = map(string)
  default = {
    enable   = "no"
    version  = "1.7.2"
    channel  = "v1.7"
  }
}

variable "analytics_engine" {
  type        = map(string)
  default = {
    enable   = "no"
    version  = "4.0.2"
    channel  = "stable-v1"
  }
}

variable "watson_knowledge_catalog" {
  type        = map(string)
  default = {
    enable   = "no"
    version  = "4.0.2"
    channel  = "v1.0"
  }
}

variable "watson_studio" {
  type        = map(string)
  default = {
    enable   = "no"
    version  = "4.0.2"
    channel  = "v2.0"
  }
}

variable "watson_machine_learning" {
  type        = map(string)
  default = {
    enable   = "no"
    version  = "4.0.2"
    channel  = "v1.1"
  }
}

variable "watson_ai_openscale" {
  type        = map(string)
  default = {
    enable   = "no"
    version  = "4.0.2"
    channel  = "v1"
  }
}

variable "spss_modeler" {
  type        = map(string)
  default = {
    enable   = "no"
    version  = "4.0.2"
    channel  = "v1.0"
  }
}

variable "cognos_dashboard_embedded" {
  type        = map(string)
  default = {
    enable   = "no"
    version  = "4.0.2"
    channel  = "v1.0"
  }
}

variable "datastage" {
  type        = map(string)
  default = {
    enable   = "no"
    version  = "4.0.2"
    channel  = "v1.0"
  }
}

variable "db2_warehouse" {
  type        = map(string)
  default = {
    enable   = "no"
    version  = "4.0.2"
    channel  = "v1.0"
  }
}

variable "db2_oltp" {
  type        = map(string)
  default = {
    enable   = "no"
    version  = "4.0.2"
    channel  = "v1.0"
  }
}

variable "cognos_analytics" {
  type        = map(string)
  default = {
    enable   = "no"
    version  = "4.0.2"
    channel  = "v4.0"
  }
}

variable "data_management_console" {
  type        = map(string)
  default = {
    enable   = "no"
    version  = "4.0.2"
    channel  = "v1.0"
  }
}

variable "master_data_management" {
  type        = map(string)
  default = {
    enable   = "no"
    version  = "4.0.2"
    channel  = "v1.1"
  }
}

variable "db2_aaservice" {
  type        = map(string)
  default = {
    enable   = "no"
    version  = "4.0.2"
    channel  = "v1.0"
  }
}

variable "decision_optimization" {
  type        = map(string)
  default = {
    enable   = "no"
    version  = "4.0.2"
    channel  = "v4.0"
  }
}

variable "planning_analytics" {
  type        = map(string)
  default = {
    enable   = "no"
    version  = "4.0.2"
    channel  = "v4.0"
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

variable "watson_assistant" {
  type        = map(string)
  default = {
    enable   = "no"
    version  = "4.0.2"
    channel  = "v4.0"
  }
}

variable "watson_discovery" {
  type        = map(string)
  default = {
    enable   = "no"
    version  = "4.0.2"
    channel  = "v4.0"
  }
}

variable "openpages" {
  type        = map(string)
  default = {
    enable   = "no"
    version  = "8.203.2"
    channel  = "v1.0"
  }
}