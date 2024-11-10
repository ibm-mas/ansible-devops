#!/bin/bash
set -e

if [ "$DEV_MODE" != "true" ]; then
  source ${GITHUB_WORKSPACE}/build/bin/.env.sh
  source ${GITHUB_WORKSPACE}/build/bin/.functions.sh
  install_yq_farah
fi

yq -i ".version=\"${VERSION}\"" $GITHUB_WORKSPACE/ibm/mas_devops/galaxy.yml

cat $GITHUB_WORKSPACE/ibm/mas_devops/galaxy.yml


# Update this when we have new catalog
MAS_PREVIOUS_CATALOG='v9-241107-amd64'
MAS_LATEST_CATALOG='v9-241205-amd64'


# Update all the placeholders in the playbooks
find ibm/mas_devops/playbooks -type f -name '*.yml' -exec sed -i \
  -e "s/@@MAS_PREVIOUS_CATALOG@@/$MAS_PREVIOUS_CATALOG/g" \
  -e "s/@@MAS_LATEST_CATALOG@@/$MAS_LATEST_CATALOG/g" \
  {} \;

# Update all the placeholders in the docs
find docs/playbooks -type f -name '*.md' -exec sed -i \
  -e "s/@@MAS_PREVIOUS_CATALOG@@/$MAS_PREVIOUS_CATALOG/g" \
  -e "s/@@MAS_LATEST_CATALOG@@/$MAS_LATEST_CATALOG/g" \
  {} \;

# Update defaults in ibm_catalog role
find ibm/mas_devops/roles/ibm_catalogs/defaults -type f -name 'main.yml' -exec sed -i \
  -e "s/@@MAS_LATEST_CATALOG@@/$MAS_LATEST_CATALOG/g" \
  {} \;
# update ibm_catalog role README
find ibm/mas_devops/roles/ibm_catalogs -type f -name 'README.md' -exec sed -i \
  -e "s/@@MAS_LATEST_CATALOG@@/$MAS_LATEST_CATALOG/g" \
  {} \;

cd $GITHUB_WORKSPACE/ibm/mas_devops
ansible-galaxy collection build

cd $GITHUB_WORKSPACE
