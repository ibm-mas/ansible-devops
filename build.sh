#!/bin/bash

if [ "$DEV_MODE" != "true" ]; then
  source ${HOME}/build.common/bin/.env.sh || exit 1
  source ${HOME}/build.common/bin/.functions.sh  || exit 1

  install_yq || exit 1
fi

yq -yi ".version=\"${VERSION}\"" $TRAVIS_BUILD_DIR/mas/devops/galaxy.yml || exit 1

cat $TRAVIS_BUILD_DIR/mas/devops/galaxy.yml || exit 1

cd $TRAVIS_BUILD_DIR/mas/devops || exit 1
ansible-galaxy collection build || exit 1

# Remove the version identifier from the filename, the build system
# will add that automatically when it publishes to Artifactory
cp mas-devops-${VERSION}.tar.gz $TRAVIS_BUILD_DIR/mas-devops.tar.gz || exit 1
cd $TRAVIS_BUILD_DIR || exit 1
