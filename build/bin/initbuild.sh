#!/bin/bash

# Simplified port of a portion of the MAS common build system for public GitHub
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PATH=$PATH:$DIR

pip install --quiet pyyaml yamllint

# 1. Set up semantic versioning
# -----------------------------------------------------------------------------
VERSION_FILE=$TRAVIS_BUILD_DIR/.version
PREVIOUS_VERSION_FILE=${TRAVIS_BUILD_DIR}/.previous_version

SEMVER_XYZ="(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
SEMVER_PRE="(-(0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(\.(0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*)?"
SEMVER_BUILD="(\+[0-9a-zA-Z-]+(\.[0-9a-zA-Z-]+)*)?"
SEMVER_REGEXP="^${SEMVER_XYZ}${SEMVER_PRE}${SEMVER_BUILD}$"

RELEASE_BRANCH_REGEXP="^(master|(0|[1-9][0-9]*)\.x|(0|[1-9][0-9]*).(0|[1-9][0-9]*)\.x)$"
MAINTENANCE_BRANCH_REGEXP="^((0|[1-9][0-9]*)\.x|(0|[1-9][0-9]*).(0|[1-9][0-9]*)\.x)$"

if [[ "${TRAVIS_BRANCH}" =~ $SEMVER_REGEXP ]]; then
  echo "Need to add the correct exclusion rule into .travis.yml to prevent builds from tagged releases"
  exit 64
fi

# Finds the most recent tag that is reachable from a commit. If the tag points
# to the commit, then only the tag is shown. Otherwise, it suffixes the tag name with the number
# of additional commits on top of the tagged object and the abbreviated object name of the most
# recent commit.
echo "npm install of git-latest-semver-tag starting"
npm install -g git-latest-semver-tag@1.0.2
echo "- npm install complete"
SEMVER_LAST_TAG=$(git-latest-semver-tag 2>/dev/null)

echo "LAST TAG = ${SEMVER_LAST_TAG}"

if [ -z $SEMVER_LAST_TAG ]; then
  SEMVER_LAST_TAG="1.0.0"
  SEMVER_RELEASE_LEVEL="initial"
  echo "Creating $TRAVIS_BUILD_DIR/.changelog"
  # Obtain a list of commits since dawn of time
  git log --oneline -1 --pretty=%B > $TRAVIS_BUILD_DIR/.changelog
else
  echo "Creating $TRAVIS_BUILD_DIR/.changelog (${SEMVER_LAST_TAG}..HEAD)"
  # Obtain a list of commits since ${SEMVER_LAST_TAG}
  git log ${SEMVER_LAST_TAG}..HEAD --oneline --pretty=%B > $TRAVIS_BUILD_DIR/.changelog

  echo "Changelog START:##################################################################"
  cat $TRAVIS_BUILD_DIR/.changelog
  echo "Changelog DONE:###################################################################"

  # Work out what has changed
  MAJOR_COUNT=`grep -ciF '[major]' $TRAVIS_BUILD_DIR/.changelog`
  echo "Major commits : ${MAJOR_COUNT}"

  MINOR_COUNT=`grep -ciF '[minor]' $TRAVIS_BUILD_DIR/.changelog`
  echo "Minor commits : ${MINOR_COUNT}"

  PATCH_COUNT=`grep -ciF '[patch]' $TRAVIS_BUILD_DIR/.changelog`
  echo "Patch commits : ${PATCH_COUNT}"

  # Important: Keep in sync with .env.sh
  SEMVER_MIN_RELEASE_LEVEL="${SEMVER_MIN_RELEASE_LEVEL:-build}"
  SEMVER_MAX_RELEASE_LEVEL="${SEMVER_MAX_RELEASE_LEVEL:-major}"
  # Semver control overrides for maintenance branches
  # - On a maintenance branch minor and major commits are banned as it would take the branch out of scope
  if [[ "${TRAVIS_BRANCH}" =~ $MAINTENANCE_BRANCH_REGEXP ]]; then
    SEMVER_MAX_RELEASE_LEVEL=patch
  fi

  SHOULD_EXIT=false
  if [ "$MAJOR_COUNT" -gt "0" ]; then
    SEMVER_RELEASE_LEVEL="major"
    if [ "$SEMVER_MAX_RELEASE_LEVEL" != "major" ]; then
        SHOULD_EXIT=true
    fi
  elif [ "$MINOR_COUNT" -gt "0" ]; then
    SEMVER_RELEASE_LEVEL="minor"
    if [ "$SEMVER_MAX_RELEASE_LEVEL" = "patch" ] || [ "$SEMVER_MIN_RELEASE_LEVEL" = "major" ]; then
        SHOULD_EXIT=true
    fi
  elif [ "$PATCH_COUNT" -gt "0" ]; then
    SEMVER_RELEASE_LEVEL="patch"
    if [ "$SEMVER_MIN_RELEASE_LEVEL" = "major" ] || [ "$SEMVER_MIN_RELEASE_LEVEL" = "minor" ]; then
        SHOULD_EXIT=true
    fi
  else
    # For a build release as long as SEMVER_MIN_RELEASE_LEVEL equals "build" then we are okay
    SEMVER_RELEASE_LEVEL="build"
    if [ "$SEMVER_MIN_RELEASE_LEVEL" != "build" ]; then
        SHOULD_EXIT=true
    fi
  fi

  if [ "$SHOULD_EXIT" = true ]; then
    echo "Minimum release level is '${SEMVER_MIN_RELEASE_LEVEL}' & maximum is '${SEMVER_MAX_RELEASE_LEVEL}', but release level is set to '${SEMVER_RELEASE_LEVEL}'. Exiting build."
    exit 1
  fi
fi
echo "RELEASE LEVEL = ${SEMVER_RELEASE_LEVEL}"
echo "${SEMVER_RELEASE_LEVEL}" > $TRAVIS_BUILD_DIR/.releaselevel

# See: https://github.com/fsaintjacques/semver-tool/blob/1.2.1/src/semver
semver init ${SEMVER_LAST_TAG} &>/dev/null
echo "Semantic versioning system initialized: $(semver)"

if [ "${SEMVER_RELEASE_LEVEL}" == "initial" ]; then
  echo "initial release of $(semver)"
elif [[ "${SEMVER_RELEASE_LEVEL}" =~ ^(major|minor|patch)$ ]]; then
  semver bump $SEMVER_RELEASE_LEVEL &>/dev/null
  echo "${SEMVER_RELEASE_LEVEL} bump from ${SEMVER_LAST_TAG} to $(semver)"
else
  semver bump build build.$TRAVIS_BUILD_NUMBER &>/dev/null
  echo "build bump from ${SEMVER_LAST_TAG} to $(semver)"
fi


# 2. Tweak version string for pre-release builds
# -----------------------------------------------------------------------------
if [[ "${TRAVIS_BRANCH}" =~ $RELEASE_BRANCH_REGEXP ]]; then
  # Release mode
  VERSION=$(semver)
else
  # Pre-release mode
  if [ -f ${TRAVIS_BUILD_DIR}/setup.py ]; then
    # For python PEP compatability we need to version python modules differently
    VERSION=$(semver).dev${TRAVIS_BUILD_NUMBER}
  else
    VERSION=$(semver)-pre.$TRAVIS_BRANCH
  fi
fi

echo "Setting ${VERSION_FILE} to ${VERSION}"
echo -n $VERSION > $VERSION_FILE

echo "Setting ${PREVIOUS_VERSION_FILE} to ${SEMVER_LAST_TAG}"
echo -n $SEMVER_LAST_TAG > $PREVIOUS_VERSION_FILE


# 3. Version python modules (if they exist)
# -----------------------------------------------------------------------------
if [ -f ${TRAVIS_BUILD_DIR}/setup.py ]; then
  sed -i "s/version='1.0.0'/version='${VERSION}'/" setup.py
fi


# 4. Configure git
# -----------------------------------------------------------------------------
git config --global user.email "iotf@uk.ibm.com"
git config --global user.name "Travis CI"
git config --global push.default simple

exit 0
