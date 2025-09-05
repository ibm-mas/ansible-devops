#!/usr/bin/env python3

import logging
import urllib3
from ansible_collections.kubernetes.core.plugins.module_utils.k8s.client import get_api_client
from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase

from mas.devops.ocp import createNamespace
from mas.devops.mas import updateIBMEntitlementKey

urllib3.disable_warnings()  # Disabling warnings will prevent InsecureRequestWarnings from dynClient
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class ActionModule(ActionBase):
    """
    Usage Example
    -------------
    tasks:
      - name: "Update IBM Entitlement Key"
        ibm.mas_devops.update_ibm_entitlement:
          namespace: "{{ mas_namespace }}"
          icr_username: "{{ icr_username }}"
          icr_password: "{{ icr_password }}"
          artifactory_username: "{{ artifactory_username }}"
          artifactory_password: "{{ artifactory_token }}"
          namespace_kyverno_label: "audit"
        register: secret
    """
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        namespace = self._task.args.get('namespace', None)
        icrUsername = self._task.args.get('icr_username', None)
        icrPassword = self._task.args.get('icr_password', None)
        artifactoryUsername = self._task.args.get('artifactory_username', None)
        artifactoryPassword = self._task.args.get('artifactory_password', None)
        secretName = self._task.args.get('secret_name', None)
        namespaceKyvernoLabel = self._task.args.get('namespace_kyverno_label', None)

        if namespace is None:
            raise AnsibleError(f"Error: namespace argument was not provided")

        # Initialize DynamicClient, ensure the namespace exists, and create/update the entitlement secret
        host = self._task.args.get('host', None)
        api_key = self._task.args.get('api_key', None)

        dynClient = get_api_client(api_key=api_key, host=host)
        createNamespace(dynClient, namespace, namespaceKyvernoLabel)
        secret = updateIBMEntitlementKey(dynClient, namespace, icrUsername, icrPassword, artifactoryUsername, artifactoryPassword, secretName)

        return dict(
            message=f"Successfully updated IBM entitlement in {namespace}: {secret.metadata.name}",
            success=True,
            failed=False,
            changed=False,
            **secret.to_dict()
        )
