
output "openshift_console_url" {
  description = "URL for OpenShift web console"
  value       = "https://console-openshift-console.apps.${var.cluster-name}.${var.dnszone}"
}

output "openshift_api" {
  description = "API endpoint"
  value       = "https://api.${var.cluster-name}.${var.dnszone}:6443"
}

output "openshift_console_username" {
  description = "Username for OpenShift web console"
  value       = var.openshift-username
}

output "openshift_console_password" {
  description = "Password for OpenShift web console"
  value       = var.openshift-password
  sensitive = true
}

# output "cpd_url" {
#   description = "URL for cpd web console"
#   value       = "https://${var.cpd-namespace}-cpd-${var.cpd-namespace}.apps.${var.cluster-name}.${var.dnszone}"
# }

# output "cpd_url_username" {
#   description = "Username for CPD Web console"
#   value       = "admin"
# }

# output "cpd_url_password" {
#   description = "URL for cpd web console"
#   value       = "$(oc extract secret/admin-user-details --keys=initial_admin_password --to=-)"
# }