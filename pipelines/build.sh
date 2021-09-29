#!/bin/bash

VERSION=1.0.0
TARGET_FILE=ibm.mas_devops.pipelines-$VERSION.yaml

echo "" > $TARGET_FILE

for FILE in "tasks/**/*.yaml"; do
  echo "Adding $FILE to pipelines installer"
  echo "# $FILE" >> $TARGET_FILE
  echo "# --------------------------------------------------------------------------------" >> $TARGET_FILE
  cat $FILE >> $TARGET_FILE
done