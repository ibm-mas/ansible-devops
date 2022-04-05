#!/bin/bash

# Export required env variables
export ARM_SUBSCRIPTION_ID=$AZURE_SUBSC_ID
export ARM_CLIENT_ID=$AZURE_SP_CLIENT_ID
export ARM_CLIENT_SECRET=$AZURE_SP_CLIENT_PWD
export ARM_TENANT_ID=$AZURE_TENANT_ID
cd $GIT_REPO_HOME/azure/ocp-bastion-host
rm -rf terraform.tfvars
# Create tfvars file
cat <<EOT >> terraform.tfvars
rg_name                 = "$RG_NAME"
rand_str                = "$RANDOM_STR"
location                = "$DEPLOY_REGION"
ssh_key                 = "$SSH_KEY_NAME"
seller_subscription_id  = "$SELLER_SUBSCRIPTION_ID"
seller_resource_group   = "$SELLER_RESOURCE_GROUP"
seller_compute_gallery  = "$SELLER_COMPUTE_GALLERY"
seller_image_version    = "$SELLER_IMAGE_VERSION"
EOT
log "==== Bastion host creation started ===="
terraform init -input=false
terraform plan -input=false -out=tfplan
terraform apply -input=false -auto-approve
log "==== Bastion host creation completed ===="