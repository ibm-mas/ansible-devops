#!/bin/bash
set -e

if [ "$DEV_MODE" != "true" ]; then
  source ${GITHUB_WORKSPACE}/build/bin/.env.sh
  source ${GITHUB_WORKSPACE}/build/bin/.functions.sh
  install_yq
fi

yq -yi ".version=\"${VERSION}\"" $GITHUB_WORKSPACE/ibm/mas_devops/galaxy.yml

cat $GITHUB_WORKSPACE/ibm/mas_devops/galaxy.yml


# Update all the placeholders in the doc source
# Make sure not to commit these changes if you run this script locally
find ibm/mas_devops/playbooks -type f -name '*.yml' -exec sed -i \
  -e 's/@@MAS_PREVIOUS_CATALOG@@/v8-231228-amd64/g' \
  -e 's/@@MAS_LATEST_CATALOG@@/v8-240130-amd64/g' \
  {} \;

cd $GITHUB_WORKSPACE/ibm/mas_devops
ansible-galaxy collection build

cd $GITHUB_WORKSPACE
