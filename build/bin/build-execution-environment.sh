#!/bin/bash
set -e

if [ "$DEV_MODE" != "true" ]; then
  source ${GITHUB_WORKSPACE}/build/bin/.env.sh
  source ${GITHUB_WORKSPACE}/build/bin/.functions.sh
  install_yq_farah
  install_ansible_builder
else
  source build/bin/.functions.sh
  export GITHUB_WORKSPACE=$(pwd)
  export VERSION="100.0.0"
fi

echo_h1 "Ansible Execution Environment Build"

TARGET=$GITHUB_WORKSPACE/target
mkdir -p $TARGET/ee
cp -r $GITHUB_WORKSPACE/build/ee $TARGET

yq "(.collections.[] | select(.name == \"ibm.mas_devops\") | .version)=\"${VERSION}\"" $GITHUB_WORKSPACE/build/ee/requirements.yml > $TARGET/ee/requirements.yml
if [ "${GITHUB_REF_TYPE}" != "tag" ]; then
  yq -i "(.collections.[] | select(.name == \"ibm.mas_devops\") | .type)=\"file\"" $TARGET/ee/requirements.yml
  yq -i "(.collections.[] | select(.name == \"ibm.mas_devops\") | .name)=\"/tmp/mas_devops/ibm-mas_devops.tar.gz\"" $TARGET/ee/requirements.yml
fi

yq "(.options.tags.[] |= sub(\"VERSION\"; env(VERSION)))" $GITHUB_WORKSPACE/build/ee/execution-environment.yml > $TARGET/ee/execution-environment.yml

if [ "${GITHUB_REF_NAME}" == "master" ]; then
  yq -i '(.options.tags += ["ibmmas/ansible-devops-ee:master"])' $TARGET/ee/execution-environment.yml
fi

if [ "${GITHUB_REF_TYPE}" == "tag" ]; then
  yq -i '(.options.tags += ["ibmmas/ansible-devops-ee:latest"])' $TARGET/ee/execution-environment.yml
fi

echo_h2 "requirements.yml:"
cat $TARGET/ee/requirements.yml
echo 
echo_h2 "execution-environment.yml:"
cat $TARGET/ee/execution-environment.yml

echo_h2 "Building execution environment:"
ansible-builder --version
ansible-builder build --file $TARGET/ee/execution-environment.yml -v3
