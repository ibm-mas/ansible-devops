resource "random_id" "randomId" {
  keepers = {
    # Generate a new ID only when a new resource group is defined
    resource_group = local.resource-group
  }
  byte_length = 8
}

resource "azurerm_storage_account" "allnodes" {
  name                     = "diag${random_id.randomId.hex}"
  resource_group_name      = var.resource-group
  location                 = var.region
  account_replication_type = "LRS"
  account_tier             = "Standard"
  depends_on = [
    azurerm_resource_group.cpdrg,
  ]
}

resource "azurerm_template_deployment" "pid" {
  name                = "atrribute_tracking"
  resource_group_name = var.resource-group
  depends_on = [
    azurerm_resource_group.cpdrg,
  ]
  template_body   = <<DEPLOY
{
    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {},
    "variables": {},
    "resources": [
        {
            "apiVersion": "2019-05-01",
            "name": "pid-06f07fff-296b-5beb-9092-deab0c6bb8ea",
            "type": "Microsoft.Resources/deployments",
            "properties": {
                "mode": "Incremental",
                "template": {
                    "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
                    "contentVersion": "1.0.0.0",
                    "resources": [
                    ]
                }
            }
        }
    ]
}
DEPLOY
  deployment_mode = "Incremental"
}