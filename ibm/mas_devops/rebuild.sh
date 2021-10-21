#!/bin/bash

VERSION=$(cat galaxy.yml | yq -r '.version')

ansible-galaxy collection build
ansible-galaxy collection install ibm-mas_devops-${VERSION}.tar.gz --ignore-certs --force
rm ibm-mas_devops-${VERSION}.tar.gz
echo "Done"
