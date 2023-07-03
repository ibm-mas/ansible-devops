#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/.env.sh
source $DIR/.functions.sh

# See: https://unix.stackexchange.com/questions/1571/grabbing-the-extension-in-a-file-name
FILE_PATH=$1
FILE_NAME=$(basename $FILE_PATH)
FILE_EXT=
while [[ $FILE_NAME = ?*.@(bz2|gz|lzma) ]]; do
  FILE_EXT=${FILE_NAME##*.}.$FILE_EXT
  FILE_NAME=${FILE_NAME%.*}
done
if [[ $FILE_NAME = ?*.* ]]; then
  FILE_EXT=${FILE_NAME##*.}.$FILE_EXT
  FILE_NAME=${FILE_NAME%.*}
fi
FILE_EXT=${FILE_EXT%.}

echo_h1 "Artifactory Release: $FILE_PATH"
echo "FILE_PATH .. $FILE_PATH"
echo "FILE_NAME .. $FILE_NAME"
echo "FILE_EXT ... $FILE_EXT"
echo "VERSION .... $VERSION"

which md5sum || exit $?
which sha1sum || exit $?

if [ ! -e $FILE_PATH ]; then
  echo_warning "Artifactory release failed - $FILE_PATH does not exist"
  exit 1
fi

TARGET_URL="${ARTIFACTORY_GENERIC_RELEASE_URL}/${GITHUB_REPOSITORY}/${VERSION}/${FILE_NAME}-${VERSION}.${FILE_EXT}"
artifactory_upload $FILE_PATH $TARGET_URL

# Update latest when we publish release, and when we update master branch .. latest build is used internally in development
if [ "${GITHUB_REF_NAME}" == "master" ] || [ "${GITHUB_REF_TYPE}" == "tag" ]; then
  LATEST_URL="${ARTIFACTORY_GENERIC_RELEASE_URL}/${GITHUB_REPOSITORY}/latest/${FILE_NAME}-latest.${FILE_EXT}"
  artifactory_upload $FILE_PATH $LATEST_URL
fi

exit 0
