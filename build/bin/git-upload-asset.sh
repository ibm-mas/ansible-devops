#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/.env.sh
source $DIR/.functions.sh

ASSET_PATH=$1

if [ -f ${ASSET_PATH} ]; then
  echo "Uploading ${ASSET_PATH} ..."
else
  echo "No file to upload: ${ASSET_PATH}"
  exit 64
fi

# The pull request number if the current job is a pull request, "false" if it's not a pull request.
if [[ "${TRAVIS_PULL_REQUEST}" != "false" ]]; then
  echo "Build is for a pull request so skip asset release"
  exit 0
fi


ASSET_NAME=$(basename $ASSET_PATH)
ASSET_TYPE=$(file -b --mime-type ${ASSET_PATH})
TAG=$VERSION

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PATH=$PATH:$DIR

# See:
# - http://stackoverflow.com/questions/40733692/github-upload-release-assets-with-bash
# - https://developer.github.com/v3/repos/releases/#get-a-release-by-tag-name

url="https://uploads.github.com/repos/${TRAVIS_REPO_SLUG}/releases/tags/${TAG}"
echo "Looking up release by tag: ${url}"
succ=$(curl -H "Authorization: token ${GITHUB_TOKEN}" $url)

## In case of success, we upload a file
upload=$(echo $succ | sed -n 's/.*"\(upload_url\)"\(: "\)\([^"]*\)\(.*\)/\3/p')
if [[ $? -eq 0 ]]; then
  echo Release found
else
  echo Error finding release!
  exit 65
fi

upload=$(echo $upload | sed -n "s#{?name,label}#?name=${ASSET_NAME}#p")

echo "Uploading ${ASSET_PATH} (${ASSET_TYPE}) -- ${upload}"
succ=$(curl \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Content-Type: ${ASSET_TYPE})" \
  --data-binary @${ASSET_PATH} \
  ${upload} \
)

download=$(echo ${succ} | egrep -o "browser_download_url.+?")
if [[ $? -eq 0 ]]; then
  LOCATION=$(echo ${download} | cut -d: -f2,3 | cut -d\" -f2)
  echo "Asset available: ${LOCATION}"
else
  echo Upload error!
  exit 66
fi
