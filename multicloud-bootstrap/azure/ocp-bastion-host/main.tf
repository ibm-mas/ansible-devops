# Configure the Microsoft Azure Provider
terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      version = "~>2.0"
    }
  }
}
provider "azurerm" {
  features {}
}

# Create subnet
resource "azurerm_subnet" "bastion-host-subnet" {
    name                 = "masocp-${var.rand_str}-bh-subnet-1"
    resource_group_name  = var.rg_name
    virtual_network_name = "ocpfourx-vnet"
    address_prefixes       = ["10.0.11.0/24"]
}

# Create public IPs
resource "azurerm_public_ip" "bastion-host-public-ip" {
    name                         = "masocp-${var.rand_str}-bh-public-ip"
    location                     = var.location
    resource_group_name          = var.rg_name
    allocation_method            = "Dynamic"
}

# Create Network Security Group and rule
resource "azurerm_network_security_group" "bastion-host-nsg" {
    name                = "masocp-${var.rand_str}-bh-nsg"
    location            = var.location
    resource_group_name = var.rg_name
    security_rule {
        name                       = "SSH"
        priority                   = 1001
        direction                  = "Inbound"
        access                     = "Allow"
        protocol                   = "Tcp"
        source_port_range          = "*"
        destination_port_range     = "22"
        source_address_prefix      = "*"
        destination_address_prefix = "*"
    }
}

# Create network interface
resource "azurerm_network_interface" "bastion-host-nic" {
    name                      = "masocp-${var.rand_str}-bh-nic"
    location                  = var.location
    resource_group_name       = var.rg_name
    ip_configuration {
        name                          = "masocp-${var.rand_str}-bh-nic-config"
        subnet_id                     = azurerm_subnet.bastion-host-subnet.id
        private_ip_address_allocation = "Dynamic"
        public_ip_address_id          = azurerm_public_ip.bastion-host-public-ip.id
    }
}

# Connect the security group to the network interface
resource "azurerm_network_interface_security_group_association" "bastion-host-nic-nsg-assoc" {
    network_interface_id      = azurerm_network_interface.bastion-host-nic.id
    network_security_group_id = azurerm_network_security_group.bastion-host-nsg.id
}

# Create virtual machine
resource "azurerm_virtual_machine" "bastion-host-vm" {
    name                  = "masocp-${var.rand_str}-bastion-host"
    location              = var.location
    resource_group_name   = var.rg_name
    network_interface_ids = [azurerm_network_interface.bastion-host-nic.id]
    vm_size                  = "Standard_DS1_v2"

    storage_image_reference {
        id = "/subscriptions/${var.seller_subscription_id}/resourceGroups/${var.seller_resource_group}/providers/Microsoft.Compute/galleries/${var.seller_compute_gallery}/images/${var.seller_image_version}"
    }
    storage_os_disk {
        name              = "masocp-${var.rand_str}-bastion-os-disk"
        create_option     = "FromImage"
        managed_disk_type = "Premium_LRS"
    }
    os_profile {
        computer_name  = "masocp-${var.rand_str}-bastion-vm-azure"
        admin_username = "azureuser"
    }
    os_profile_linux_config {
        disable_password_authentication = true
        ssh_keys {
            path     = "/home/azureuser/.ssh/authorized_keys"
            key_data = var.ssh_key
        }
    }
}