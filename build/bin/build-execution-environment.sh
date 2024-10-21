#!/bin/bash
set -e

echo_h1 "Ansible Execution Environment Build"

if [ "$DEV_MODE" != "true" ]; then
  source ${GITHUB_WORKSPACE}/build/bin/.env.sh
  source ${GITHUB_WORKSPACE}/build/bin/.functions.sh
  install_yq_farah
  install_ansible_builder
fi

yq -i "(.collections.[] | select(.name == \"ibm.mas_devops\") | .version)=\"${VERSION}\"" $GITHUB_WORKSPACE/build/ee/requirements.yml
yq -i "(.options.tags.[] |= sub(\"VERSION\"; env(VERSION)))" $GITHUB_WORKSPACE/build/ee/execution-environment.yml

if [ "${GITHUB_REF_NAME}" == "master" ]; then
  yq '(.options.tags += ["ibmmas/ansible-devops-ee:master"])'
fi

if [ "${GITHUB_REF_TYPE}" == "tag" ]; then
  yq '(.options.tags += ["ibmmas/ansible-devops-ee:latest"])'
fi

echo_h2 "requirements.yml:"
cat $GITHUB_WORKSPACE/build/ee/requirements.yml
echo 
echo_h2 "execution-environment.yml:"
cat $GITHUB_WORKSPACE/build/ee/execution-environment.yml

ansible-build build --file build/ee/execution-environment.yml
