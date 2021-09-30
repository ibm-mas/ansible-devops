#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $DIR/.env.sh
source $DIR/.functions.sh

docker login quay.io --username $QUAYIO_USERNAME --password $QUAYIO_PASSWORD
docker tag ibmmas/ansible-devops quay.io/ibmmas/ansible-devops:$DOCKER_TAG
docker push quay.io/ibmmas/ansible-devops:$DOCKER_TAG
