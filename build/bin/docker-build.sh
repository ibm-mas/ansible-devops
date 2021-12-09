#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/.env.sh
source $DIR/.functions.sh

while [[ $# -gt 0 ]]
do
    key="$1"

    case $key in
        -n|--namespace)
        NAMESPACE="$2"
        ;;

        -i|--image)
        IMAGE="$2"
        ;;

        -b|--buildpath)
        BUILDPATH="$2"
        ;;

        -f|--file)
        DOCKERFILE="$2"
        ;;

        *)
        # unknown option, use as additional params directly to docker
        EXTRA_PARAMS="$EXTRA_PARAMS $key $2"
        ;;
    esac
    shift
    shift
done

BUILDPATH="${BUILDPATH:-image/$IMAGE}"
DOCKERFILE="${DOCKERFILE:-$BUILDPATH/Dockerfile}"

# Note: Travis will ******* out the sensitive information here, but it will prove that
# the value matches the value in the config if it does, which is the goal!
echo_h1 "Docker Build: $NAMESPACE/$IMAGE"
echo "BUILDPATH ...... $BUILDPATH"
echo "DOCKERFILE ..... $DOCKERFILE"
echo "EXTRA_PARAMS ... $EXTRA_PARAMS"
echo "VERSION_LABEL .. $DOCKER_TAG"
echo "RELEASE_LABEL .. $GITHUB_RUN_ID"
echo "VCS_REF ........ $GITHUB_SHA"
echo "VCS_URL ........ https://github.com/$GITHUB_REPOSITORY"

# ARM64 builds need a different setup
if [[ $EXTRA_PARAMS =~ "AARCH64" ]]; then
  docker run --privileged yen3/binfmt-register set aarch64
  docker build \
  --build-arg VERSION_LABEL=$DOCKER_TAG \
  --build-arg RELEASE_LABEL=$GITHUB_RUN_ID \
  --build-arg VCS_REF=$GITHUB_SHA \
  --build-arg VCS_URL=https://github.ibm.com/$GITHUB_REPOSITORY \
  -t $NAMESPACE/$IMAGE $EXTRA_PARAMS -f $DOCKERFILE $BUILDPATH
  docker run --privileged yen3/binfmt-register clear aarch64
else
  docker build \
    --build-arg VERSION_LABEL=$DOCKER_TAG \
    --build-arg RELEASE_LABEL=$GITHUB_RUN_ID \
    --build-arg VCS_REF=$GITHUB_SHA \
    --build-arg VCS_URL=https://github.com/$GITHUB_REPOSITORY \
    -t $NAMESPACE/$IMAGE $EXTRA_PARAMS -f $DOCKERFILE $BUILDPATH
fi
