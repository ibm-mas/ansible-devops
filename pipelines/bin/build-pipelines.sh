#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ "$DEV_MODE" != "true" ]; then
  source ${TRAVIS_BUILD_DIR}/build/bin/.env.sh
  source ${TRAVIS_BUILD_DIR}/build/bin/.functions.sh

  FILES=$TRAVIS_BUILD_DIR/pipelines/tasks/**/*.yaml
  TARGET_FILE=$TRAVIS_BUILD_DIR/pipelines/ibm-mas_devops-clustertasks-$VERSION.yaml
else
  FILES=$DIR/../tasks/**/*.yaml
  TARGET_FILE=$DIR/../ibm-mas_devops-clustertasks-$VERSION.yaml
fi

echo "" > $TARGET_FILE

echo "Creating pipelines installer ($TARGET_FILE)"
for FILE in $FILES; do
  echo " - Adding $FILE"
  echo "# --------------------------------------------------------------------------------" >> $TARGET_FILE
  echo "# $FILE" >> $TARGET_FILE
  echo "# --------------------------------------------------------------------------------" >> $TARGET_FILE
  cat $FILE >> $TARGET_FILE
done

sed -i "s#quay.io/ibmmas/ansible-devops:latest#quay.io/ibmmas/ansible-devops:$VERSION#g" $TARGET_FILE


# Extra debug for Travis builds
if [ "$DEV_MODE" != "true" ]; then
  cat $TARGET_FILE
fi
