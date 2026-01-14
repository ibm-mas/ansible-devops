#!/usr/bin/env python3

import logging
import urllib3
from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError

from mas.devops.mas import getMasPublicClusterIssuer

urllib3.disable_warnings()  # Disabling warnings will prevent InsecureRequestWarnings from dynClient
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class ActionModule(ActionBase):
    """
    Retrieve the Public Cluster Issuer for a MAS instance.
    
    This action plugin queries the Suite custom resource and retrieves the
    certificate issuer name from spec.certificateIssuer.name. If not specified,
    it returns the default issuer name.
    
    Usage Example
    -------------
    tasks:
      - name: "Get MAS Cluster Issuer"
        ibm.mas_devops.get_mas_cluster_issuer:
          instance_id: "{{ mas_instance_id }}"
        register: cluster_issuer
    """
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        # Initialize DynamicClient and grab the task args
        host = self._task.args.get('host', None)
        api_key = self._task.args.get('api_key', None)

        dynClient = get_api_client(api_key=api_key, host=host)

        instanceId = self._task.args.get('instance_id', None)

        if instanceId is None:
            raise AnsibleError(f"Error: instance_id argument was not provided")
        if not isinstance(instanceId, str):
            raise AnsibleError(f"Error: instance_id argument is not a string")

        # Get the cluster issuer name
        issuerName = getMasPublicClusterIssuer(dynClient, instanceId)

        if issuerName is None:
            return dict(
                message=f"Failed to retrieve cluster issuer for MAS instance '{instanceId}'",
                success=False,
                failed=True,
                changed=False,
                instance_id=instanceId
            )

        return dict(
            message=f"Successfully retrieved cluster issuer for MAS instance '{instanceId}'",
            success=True,
            failed=False,
            changed=False,
            instance_id=instanceId,
            issuer_name=issuerName
        )

