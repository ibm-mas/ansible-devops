/*
Reusable and configurable Provider module for AWS Cloud
*/

variable "region" {
  type = string
  description = "Region for deployment"
}

# Terraform Provider configurations
# Note: variables are not allowed in this configuration block
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "4.9.0"
    }
  }
}

provider "aws" {
  region = var.region
}
