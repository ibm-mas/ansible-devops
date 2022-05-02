#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ "$DEV_MODE" != "true" ]; then
  source ${GITHUB_WORKSPACE}/build/bin/.env.sh
  source ${GITHUB_WORKSPACE}/build/bin/.functions.sh

  FILES=$GITHUB_WORKSPACE/pipelines/tasks/*.yaml
  TARGET_FILE=$GITHUB_WORKSPACE/pipelines/ibm-mas_devops-clustertasks-$VERSION.yaml
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

sed "s/:latest/:$VERSION/g" $TARGET_FILE > $TARGET_FILE.txt

rm $TARGET_FILE
mv $TARGET_FILE.txt $TARGET_FILE

# Extra debug for Travis builds
if [ "$DEV_MODE" != "true" ]; then
  cat $TARGET_FILE
fi
