#!/bin/bash

# This script should be executed on the Red Hat 8 instance before creating AMI from it.
# The created AMI will be used to create Bootnode instance for MAS provisioning.

# Update all packages to latest
yum update -y

## Install pre-reqs
yum install git httpd-tools java python36 unzip wget zip -y
ln -s /usr/bin/python3 /usr/bin/python
ln -s /usr/bin/pip3 /usr/bin/pip
pip install pyyaml
pip install jaydebeapi

# Install Azure cli
rpm --import https://packages.microsoft.com/keys/microsoft.asc
echo -e "[azure-cli]
name=Azure CLI
baseurl=https://packages.microsoft.com/yumrepos/azure-cli
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc" | tee /etc/yum.repos.d/azure-cli.repo
dnf install azure-cli -y

# Install AzureCopy cli 
wget https://aka.ms/downloadazcopy-v10-linux -O azcopy_linux_amd64.tar.gz
tar -xzvf azcopy_linux_amd64.tar.gz
mv -f azcopy_linux_amd64_*/azcopy /usr/sbin
rm -rf azcopy_linux_amd64*

## Install jq
wget "https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64"
mv jq-linux64 jq
chmod +x jq
mv jq /usr/local/bin

# Install podman
yum module install -y container-tools

## Download Openshift CLI and move to /usr/local/bin
wget "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/4.8.11/openshift-client-linux-4.8.11.tar.gz"
tar -xvf openshift-client-linux-4.8.11.tar.gz
chmod u+x oc kubectl
mv oc /usr/local/bin
mv kubectl /usr/local/bin
oc version
rm -rf openshift-client-linux-4.8.11.tar.gz

## Install terraform
TERRAFORM_VER=`curl -s https://api.github.com/repos/hashicorp/terraform/releases/latest |  grep tag_name | cut -d: -f2 | tr -d \"\,\v | awk '{$1=$1};1'`
echo $TERRAFORM_VER
wget https://releases.hashicorp.com/terraform/${TERRAFORM_VER}/terraform_${TERRAFORM_VER}_linux_amd64.zip
unzip terraform_${TERRAFORM_VER}_linux_amd64.zip
mv terraform /usr/local/bin/
terraform version
rm -rf terraform_${TERRAFORM_VER}_linux_amd64.zip

## Install Ansible
pip3 install ansible==4.9.0
pip3 install openshift
ansible-galaxy collection install community.kubernetes

# Remove the SSH keys
rm -rf /home/ec2-user/.ssh/authorized_keys /root/.ssh/authorized_keys

echo "Bootnode preparation completed"
