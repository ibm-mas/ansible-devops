#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/.env.sh
source $DIR/.functions.sh


# 1. Check whether this is a pull request
# -----------------------------------------------------------------------------
if [[ ! -z "${GITHUB_HEAD_REF}" ]]; then
  echo "Build is for a pull request so skip asset release"
  exit 0
fi


# 2. Create the release
# -----------------------------------------------------------------------------
if [[ "${GITHUB_REF_NAME}" =~ $RELEASE_BRANCH_REGEXP ]]; then

  # Check whether the level of the release is supported
  if [ "$SEMVER_RELEASE_LEVEL" = "major" ] && [ "$SEMVER_MAX_RELEASE_LEVEL" != "major" ]; then
    echo "Aborting release because major release is prohibited on this branch"
    exit 0
  elif [ "$SEMVER_RELEASE_LEVEL" = "minor" ]; then
    if [ "$SEMVER_MAX_RELEASE_LEVEL" = "patch" ] || [ "$SEMVER_MIN_RELEASE_LEVEL" = "major" ]; then
      echo "Aborting release because minor release is prohibited on this branch"
      exit 0
    fi
  elif [ "$SEMVER_RELEASE_LEVEL" = "patch" ]; then
    if [ "$SEMVER_MIN_RELEASE_LEVEL" = "major" ] || [ "$SEMVER_MIN_RELEASE_LEVEL" = "minor" ]; then
      echo "Aborting release because patch release is prohibited on this branch"
      exit 0
    fi
  else
    if [ "$SEMVER_MIN_RELEASE_LEVEL" != "build" ]; then
      echo "Aborting release because build release is prohibited on this branch"
      exit 0
    fi
  fi

  # Publish the release
  echo "Publishing new release $VERSION to GitHub"
  git tag $VERSION
  git push origin --tags

  # After we have created the tag we still need to create the release from that tag
  GREN=$GITHUB_WORKSPACE/build/github-release-notes/bin/gren.js
  REPO=${GITHUB_REPOSITORY#*/}
  USER=${GITHUB_REPOSITORY%/*}

  echo "Installing GitHub Release Notes"
  # Install GitHub Release Notes
  source ~/.nvm/nvm.sh
  cd $GITHUB_WORKSPACE/build
  git clone https://github.com/durera/github-release-notes.git
  cd $GITHUB_WORKSPACE/build/github-release-notes
  nvm exec 7 npm install &>/dev/null
  cd $GITHUB_WORKSPACE

  echo "Generating Release for $USER/$REPO"
  # See https://github-tools.github.io/github-release-notes/options
  source ~/.nvm/nvm.sh
  nvm exec 7 node $GREN \
    --username=$USER \
    --repo=$REPO \
    --token=$GITHUB_TOKEN \
    --action=release \
    --tags=${VERSION}..${PREVIOUS_VERSION} \
    --data-source=prs
    --include-messages=commits

  # Add release assets
  for $asset in "$@"; do
    $DIR/git-upload-asset.sh $asset
  done

else
  echo "Non release branch (${GITHUB_REF_NAME}) - skip git release publish"
fi

exit 0