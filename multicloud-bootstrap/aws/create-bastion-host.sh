#!/bin/bash

# Get the first public subnet in the VPC created for OCP cluster
BACKUP_FILE_NAME=terraform-backup-${CLUSTER_NAME}.zip
NEW_VPC_ID=$(cat $GIT_REPO_HOME/aws/ocp-terraform/terraform.tfstate | jq '.resources[] | select((.type | contains("aws_subnet")) and (.name | contains("master1")))' | jq '.instances[0].attributes.vpc_id' | tr -d '"')
NEW_VPC_PUBLIC_SUBNET_ID=$(cat $GIT_REPO_HOME/aws/ocp-terraform/terraform.tfstate | jq '.resources[] | select((.type | contains("aws_subnet")) and (.name | contains("master1")))' | jq '.instances[0].attributes.id' | tr -d '"')
log " NEW_VPC_PUBLIC_SUBNET_ID=$NEW_VPC_PUBLIC_SUBNET_ID"
log " BACKUP_FILE_NAME=$BACKUP_FILE_NAME"
cd $GIT_REPO_HOME/aws/ocp-bastion-host
rm -rf terraform.tfvars
# Create tfvars file
cat <<EOT >> terraform.tfvars
region                          = "$DEPLOY_REGION"
access_key_id                   = "$AWS_ACCESS_KEY_ID"
secret_access_key               = "$AWS_SECRET_ACCESS_KEY"
key_name                        = "$SSH_KEY_NAME"
vpc_id                          = "$NEW_VPC_ID"
subnet_id                       = "$NEW_VPC_PUBLIC_SUBNET_ID"
unique_str                      = "$RANDOM_STR"
iam_instance_profile            = "masocp-deploy-instance-profile-$RANDOM_STR"
user_data = <<EOF
#! /bin/bash
shutdown -P "+1"
EOF
EOT
sed -i "s/<REGION>/$DEPLOY_REGION/g" variables.tf
log "==== Bastion host creation started ===="
terraform init -input=false
terraform plan -input=false -out=tfplan
terraform apply -input=false -auto-approve
log "==== Bastion host creation completed ===="