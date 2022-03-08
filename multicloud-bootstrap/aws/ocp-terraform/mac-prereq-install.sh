#!/bin/bash

## Install wget, htpasswd, python3 and aws CLIs

brew install wget
brew install python3
ln -s /usr/local/bin/python3 /usr/local/bin/python
ln -s /usr/local/bin/pip3 /usr/local/bin/pip
pip install awscli --upgrade --user
pip install pyyaml
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

## Install jq

wget "https://github.com/stedolan/jq/releases/download/jq-1.6/jq-osx-amd64"
mv jq-osx-amd64 jq
chmod +x jq
mv jq /usr/local/bin

## Download Openshift CLI and move to /usr/local/bin

wget "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/4.8.11/openshift-client-mac-4.8.11.tar.gz"
tar -xvf openshift-client-mac-4.8.11.tar.gz
chmod u+x oc kubectl
sudo mv oc /usr/local/bin
sudo mv kubectl /usr/local/bin
oc version

## Install terraform

brew tap hashicorp/tap
brew install hashicorp/tap/terraform
terraform -help
