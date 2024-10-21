#!/bin/bash

# Install yq CLI
set -e

curl -L  "https://github.com/mikefarah/yq/releases/download/v4.35.1/yq_linux_amd64"  > /usr/bin/yq
chmod 755 /usr/bin/yq

yq --version || exit 1
