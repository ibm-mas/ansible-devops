/*
Input variables used to configure the cos bucket
*/

variable "bucket_name" {
  type = string
  description = "Name of the bucket"
}

variable "user_arn" {
  type = string
  description = "ARN of AWS user for client to access the bucket."
}

variable "perm_action" {
  type = list(string)
  description = "List of the  AWS actions that you what assign to a user."
}

variable "access_point_name" {
  type = string
  description = "Access Point Name for a Bucket."
  default = "access-point-c1"
}
