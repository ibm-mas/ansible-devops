##### Azure configuration #####
variable "rg_name" {
  description = "Resource group of the OCP cluster."
}
variable "rand_str" {
  description = "Random string unique to the cluster."
}
variable "location" {
  description = "Location of the cluster."
}
variable "ssh_key" {
  description = "SSH key."
}
variable "seller_subscription_id" {
  description = "Seller subscription ID."
}
variable "seller_resource_group" {
  description = "Seller resource group."
}
variable "seller_compute_gallery" {
  description = "Seller compute gallery."
}
variable "seller_image_version" {
  description = "Seller image version."
}