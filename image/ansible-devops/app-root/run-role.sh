#!/bin/bash

if [ -e "/workspace/additional-configs" ]; then
  cp /workspace/additional-configs/* /workspace/configs/
fi

source /opt/app-root/src/env.sh
export ROLE_NAME=$1
ansible-playbook ibm.mas_devops.run_role
rc=$?
python3 /opt/app-root/src/save-junit-to-mongo.py
exit $rc
