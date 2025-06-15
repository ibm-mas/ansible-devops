#!/bin/bash
# Install ROSA Cli
set -e

wget -q https://mirror.openshift.com/pub/openshift-v4/clients/rosa/latest/rosa-linux.tar.gz
tar --no-same-owner -xzf rosa-linux.tar.gz
mv rosa /usr/local/bin/
chmod +x /usr/local/bin/rosa
rosa version
rm -rf rosa-linux.tar.gz