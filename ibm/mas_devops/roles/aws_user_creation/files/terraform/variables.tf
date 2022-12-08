/*
Input variables used to configure the S3 bucket
*/

variable "user_name" {
  type = string
  description = "AWS user name."
}

variable "perm_action" {
  type = list(string)
  description = "List of the  AWS actions that you what assign to a user."
}

variable "perm_resources" {
  type = list(string)
  description = "List of the AWS resources that the user can access."
}
