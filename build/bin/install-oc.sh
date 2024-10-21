#!/bin/bash

set -e

# Install OpenShift CLI (latest stable version)
wget -q https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/stable/openshift-client-linux.tar.gz
tar -zxf openshift-client-linux.tar.gz
mv oc /usr/local/bin/
mv kubectl /usr/local/bin/
rm -f openshift-client-linux.tar.gz

# Install oc mirror plugin (latest stable version)
wget -q https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/stable/oc-mirror.tar.gz
tar -zxf oc-mirror.tar.gz
mv oc-mirror /usr/local/bin/
chmod +x /usr/local/bin/oc-mirror
rm -f oc-mirror.tar.gz
