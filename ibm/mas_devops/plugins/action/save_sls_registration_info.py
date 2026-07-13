#!/usr/bin/env python3

import logging
import yaml
import urllib3
from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client
from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase
import os

from mas.devops.sls import getSLSRegistrationDetails

urllib3.disable_warnings()  # Disabling warnings will prevent InsecureRequestWarnings from dynClient
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        slsNamespace = self._task.args.get('namespace', None)
        slsName = self._task.args.get('name', None)
        backupPath = self._task.args.get('sls_backup_path', None)

        if slsNamespace is None:
            raise AnsibleError(f"Error: slsNamespace argument was not provided")
        if slsName is None:
            raise AnsibleError(f"Error: slsName argument was not provided")
        if backupPath is None:
            raise AnsibleError(f"Error: sls_backup_dir argument was not provided")

        # Initialize DynamicClient, ensure the namespace exists, and create/update the entitlement secret
        host = self._task.args.get('host', None)
        api_key = self._task.args.get('api_key', None)

        dynClient = get_api_client(api_key=api_key, host=host)

        registrationDetails = getSLSRegistrationDetails(name=slsName, namespace=slsNamespace, dynClient=dynClient)

        if registrationDetails:
            with open(os.path.join(backupPath, 'sls-registration.yaml'), 'w') as outfile:
                yaml.dump(registrationDetails, outfile, default_flow_style=False)
                return dict(
                    msg=f"Successfully stored SLS registration details to {os.path.join(backupPath, 'sls-registration.yml')}",
                    failed=False,
                    success=True
                )
        else:
            return dict(
                msg=f"Couldn't get registration details from CR status of SLS {slsName} in namespace {slsNamespace}.",
                failed=True,
                success=False
            )
