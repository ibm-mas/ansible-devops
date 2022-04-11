##### AWS Configuration #####
variable "region" {
  description = "The region to deploy the cluster in, e.g: us-west-2."
  default     = "<REGION>"
}

variable "vpc_id" {
  type        = string
  description = "VPC Id"
}

variable "subnet_id" {
  type        = string
  description = "Subnet Id"
}

variable "unique_str" {
  type        = string
  description = "Cluster unique string"
}

variable "key_name" {
  description = "The name of the key to user for ssh access, e.g: consul-cluster"
  default     = "openshift-key"
}

variable "access_key_id" {
  type        = string
  description = "Access Key ID for the AWS account"
}

variable "secret_access_key" {
  type        = string
  description = "Secret Access Key for the AWS account"
}

variable "iam_instance_profile" {
  type        = string
  description = "IAM instance profile to be associated with this instance"
}

variable "user_data" {
  type        = string
  description = "User data"
}
