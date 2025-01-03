#!/bin/bash

# Install IBM CLoud CLI with container-service plugin
set -e

CLI_VERSION=2.26.1
wget -q https://download.clis.cloud.ibm.com/ibm-cloud-cli/${CLI_VERSION}/IBM_Cloud_CLI_${CLI_VERSION}_amd64.tar.gz
tar --no-same-owner -xzf IBM_Cloud_CLI_${CLI_VERSION}_amd64.tar.gz
mv Bluemix_CLI/bin/ibmcloud /usr/local/bin/
rm -rf Bluemix_CLI IBM_Cloud_CLI_${CLI_VERSION}_amd64.tar.gz
ibmcloud plugin repo-plugins -r 'IBM Cloud'
ibmcloud plugin install container-service
ibmcloud plugin install container-registry

# We don't want remove the plugins (in .bluemix/plugins) only the configuration file generated by the above actions
rm /home/runner/.bluemix/config.json

# Fix up permissions so that the group has the same permissions as the (root) user
chmod -R g=u /home/runner/.bluemix
