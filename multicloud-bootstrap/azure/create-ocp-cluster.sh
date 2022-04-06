#!/bin/bash

# Export required env variables
export ARM_SUBSCRIPTION_ID=$AZURE_SUBSC_ID
export ARM_CLIENT_ID=$AZURE_SP_CLIENT_ID
export ARM_CLIENT_SECRET=$AZURE_SP_CLIENT_PWD
export ARM_TENANT_ID=$AZURE_TENANT_ID
cd $GIT_REPO_HOME/azure/ocp-terraform/azure_infra
rm -rf terraform.tfvars
# Create tfvars file
cat <<EOT >> terraform.tfvars
azure-client-id="$AZURE_SP_CLIENT_ID"
azure-client-secret="$AZURE_SP_CLIENT_PWD"
azure-subscription-id="$AZURE_SUBSC_ID"
azure-tenant-id="$AZURE_TENANT_ID"
resource-group          = "$RG_NAME"
existing-resource-group = "yes"
single-or-multi-zone    = "multi"
cluster-name            = "masocp-$RANDOM_STR"
region                  = "$DEPLOY_REGION"
ssh-public-key          = "$SSH_KEY_NAME"
dnszone                 = "$BASE_DOMAIN"
dnszone-resource-group  = "$BASE_DOMAIN_RG_NAME"
pull-secret-file-path   = "$OPENSHIFT_PULL_SECRET_FILE_PATH"
openshift-username      = "$OPENSHIFT_USER"
openshift-password      = "$OPENSHIFT_PASSWORD"
master-node-count       = "$MASTER_NODE_COUNT"
worker-node-count       = "$WORKER_NODE_COUNT"
EOT
log "==== OCP cluster creation started ===="
terraform init -input=false
terraform plan -input=false -out=tfplan
terraform apply -input=false -auto-approve
log "==== OCP cluster creation completed ===="