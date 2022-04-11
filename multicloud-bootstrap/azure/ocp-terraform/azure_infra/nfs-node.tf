# locals {
#   nfs-instance-type = "Standard_D8s_v3"
#   devfolder         = "nfs"
# }

# resource "azurerm_virtual_machine" "nfs" {
#   count                 = var.storage == "nfs" ? 1 : 0
#   name                  = "${var.cluster-name}-nfs"
#   location              = var.region
#   resource_group_name   = var.resource-group
#   network_interface_ids = [azurerm_network_interface.nfs[count.index].id]
#   vm_size               = local.nfs-instance-type

#   storage_os_disk {
#     name              = "${var.cluster-name}-nfs-OsDisk"
#     caching           = "ReadWrite"
#     create_option     = "FromImage"
#     managed_disk_type = "Premium_LRS"
#   }

#   storage_data_disk {
#     name              = "${var.cluster-name}-nfs-DataDisk"
#     lun               = "0"
#     caching           = "ReadWrite"
#     disk_size_gb      = var.storage-disk-size
#     create_option     = "Empty"
#     managed_disk_type = "Premium_LRS"
#   }

#   storage_image_reference {
#     publisher = "RedHat"
#     offer     = "RHEL"
#     sku       = "7-RAW"
#     version   = "latest"
#   }

#   os_profile {
#     computer_name  = "nfsnode"
#     admin_username = var.admin-username
#   }

#   os_profile_linux_config {
#     disable_password_authentication = true
#     ssh_keys {
#       path     = "/home/${var.admin-username}/.ssh/authorized_keys"
#       key_data = var.ssh-public-key
#     }
#   }

#   boot_diagnostics {
#     enabled     = "true"
#     storage_uri = azurerm_storage_account.allnodes.primary_blob_endpoint
#   }
#   depends_on = [
#     azurerm_resource_group.cpdrg,
#   ]
# }

# resource "azurerm_virtual_machine_extension" "nfsext" {
#   count                = var.storage == "nfs" ? 1 : 0
#   name                 = "${var.cluster-name}-nfsext"
#   virtual_machine_id   = azurerm_virtual_machine.nfs[count.index].id
#   publisher            = "Microsoft.Azure.Extensions"
#   type                 = "CustomScript"
#   type_handler_version = "2.0"

#   protected_settings = <<PROT
#     {
#         "script": "${base64encode(file("../nfs_module/setup-nfs.sh"))}"
#     }
#     PROT
# }

# resource "azurerm_recovery_services_vault" "cpd_vault" {
#   count               = var.enableNFSBackup == "yes" ? 1 : 0
#   name                = "cpd-vault"
#   resource_group_name = var.resource-group
#   location            = var.region
#   sku                 = "Standard"
#   depends_on = [
#     azurerm_resource_group.cpdrg,
#   ]
# }

# resource "azurerm_backup_policy_vm" "backup_policy" {
#   count               = var.enableNFSBackup == "yes" ? 1 : 0
#   name                = "cpd-backup-policy"
#   resource_group_name = var.resource-group
#   recovery_vault_name = azurerm_recovery_services_vault.cpd_vault[count.index].name

#   timezone = "UTC"

#   backup {
#     frequency = "Daily"
#     time      = "23:30"
#   }

#   retention_daily {
#     count = 10
#   }
#   depends_on = [
#     azurerm_resource_group.cpdrg,
#     azurerm_recovery_services_vault.cpd_vault,
#   ]
# }

# resource "azurerm_backup_protected_vm" "nfs_backup" {
#   count               = var.storage == "nfs" && var.enableNFSBackup == "yes" ? 1 : 0
#   resource_group_name = var.resource-group
#   recovery_vault_name = azurerm_recovery_services_vault.cpd_vault[count.index].name
#   source_vm_id        = azurerm_virtual_machine.nfs[count.index].id
#   backup_policy_id    = azurerm_backup_policy_vm.backup_policy[count.index].id
#   depends_on = [
#     azurerm_resource_group.cpdrg,
#     azurerm_recovery_services_vault.cpd_vault,
#     azurerm_backup_policy_vm.backup_policy,
#   ]
# }