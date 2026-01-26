#!/usr/bin/env python3

import logging
import urllib3

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.utils.display import Display
from kubernetes import client, config
from kubernetes.dynamic import DynamicClient

from mas.devops.backup import backupResources 

urllib3.disable_warnings()  # Disabling warnings will prevent InsecureRequestWarnings from dynClient
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

display = Display()


class ActionModule(ActionBase):
    """
    Backup Kubernetes resources based on a list of resource definitions
    
    Usage Example
    -------------
    tasks:
      - name: "Backup MAS Suite resources"
        ibm.mas_devops.backup_resource:
          backup_resources:
            - namespace: "mas-inst1-core"
              resources:
                - kind: Subscription
                  api_version: operators.coreos.com/v1alpha1
                  name: ibm-mas-operator
                - kind: Suite
                  api_version: core.mas.ibm.com/v1
                - kind: Workspace
                  api_version: core.mas.ibm.com/v1
          backup_path: "/backup/mas-suite"
    """
    def run(self, tmp=None, task_vars=None):
        super(ActionModule, self).run(tmp, task_vars)

        # Initialize DynamicClient and grab the task args
        host = self._task.args.get('host', None)
        api_key = self._task.args.get('api_key', None)

        # Load kubernetes configuration
        try:
            if host and api_key:
                # Use provided host and api_key
                configuration = client.Configuration()
                configuration.host = host
                configuration.api_key = {'authorization': f'Bearer {api_key}'}
                configuration.verify_ssl = False
                api_client = client.ApiClient(configuration)
            else:
                # Load from kubeconfig
                config.load_kube_config()
                api_client = client.ApiClient()
        except Exception as e:
            raise AnsibleError(f"Failed to initialize Kubernetes client: {e}")
        
        dynClient = DynamicClient(api_client)

        backup_resources = self._task.args.get('backup_resources')
        backup_path = self._task.args.get('backup_path')

        if backup_resources is None or not isinstance(backup_resources, list):
            raise AnsibleError(f"Error: backup_resources argument must be provided as a list")
        if backup_path is None or backup_path == "":
            raise AnsibleError(f"Error: backup_path argument was not provided")
        
        display.v(f"Starting backup of MAS Suite resources to '{backup_path}'")

        total_backed_up = 0
        total_failed = 0
        total_not_found = 0
        all_discovered_secrets = set()
        secrets_by_namespace = {}  # Track secrets per namespace
        failed_resources = []  # Track failed resources with details

        # Process each namespace and its resources
        for namespace_config in backup_resources:
            namespace = namespace_config.get('namespace')
            resources = namespace_config.get('resources', [])
            
            # Namespace can be blank for cluster-scoped resources
            if namespace:
                display.v(f"Processing namespace: {namespace}")
            else:
                display.v(f"Processing cluster-scoped resources")
            
            # Process each resource in the namespace (or cluster-scoped)
            for resource_def in resources:
                kind = resource_def.get('kind')
                api_version = resource_def.get('api_version')
                name = resource_def.get('name')
                labels = resource_def.get('labels', [])
                
                if not kind:
                    display.v(f"Warning: Skipping resource without kind defined")
                    continue
                
                if not api_version:
                    raise AnsibleError(f"Error: api_version is required for resource kind '{kind}'")
                
                # Backup resources (either specific or all of that kind)
                # Pass namespace, name, and labels as named optional arguments
                backed_up, not_found, failed, discovered_secrets = backupResources(
                    dynClient, kind, api_version, backup_path,
                    namespace=namespace, name=name, labels=labels
                )
                total_backed_up += backed_up
                total_not_found += not_found
                total_failed += failed
                
                # Track failed resources with details
                if failed > 0:
                    scope = namespace if namespace else 'cluster-scoped'
                    resource_desc = f"{kind}/{name}" if name else f"{kind} (all)"
                    if labels:
                        resource_desc += f" with labels {labels}"
                    failed_resources.append({
                        'scope': scope,
                        'kind': kind,
                        'name': name if name else 'all',
                        'api_version': api_version,
                        'description': resource_desc
                    })
                
                # Track discovered secrets by namespace (only if namespace is provided)
                if discovered_secrets and namespace:
                    if namespace not in secrets_by_namespace:
                        secrets_by_namespace[namespace] = set()
                    secrets_by_namespace[namespace].update(discovered_secrets)
                    all_discovered_secrets.update(discovered_secrets)
            
            display.v(f"Backup complete for named resources: {total_backed_up} resources backed up, {total_not_found} not found, {total_failed} failed")

        # Now backup all discovered secrets per namespace
        for ns, secret_names in secrets_by_namespace.items():
            if secret_names:
                display.v(f"Backing up {len(secret_names)} discovered secret(s) in namespace '{ns}': {', '.join(sorted(secret_names))}")

                for secret_name in sorted(secret_names):
                    display.v(f"Backing up discovered secret: {secret_name}")
                    backed_up, not_found, failed, _ = backupResources(
                        dynClient, 'Secret', 'v1', backup_path,
                        namespace=ns, name=secret_name
                    )
                    total_backed_up += backed_up
                    total_not_found += not_found
                    total_failed += failed
                    
                    # Track failed secret backups
                    if failed > 0:
                        failed_resources.append({
                            'scope': ns,
                            'kind': 'Secret',
                            'name': secret_name,
                            'api_version': 'v1',
                            'description': f"Secret/{secret_name} (auto-discovered)"
                        })
                    
                    if not_found:
                        display.v(f"Warning: Referenced secret '{secret_name}' not found in namespace '{ns}'")

        display.v(f"Backup complete for all: {total_backed_up} resources backed up, {total_not_found} not found, {total_failed} failed")

        # Determine if the backup was successful
        has_failures = total_failed > 0
        
        return dict(
            message=f"Backed up {total_backed_up} MAS Suite resources" + (f" with {total_failed} failures" if has_failures else ""),
            failed=has_failures,
            changed=False,
            success=not has_failures,
            backed_up_count=total_backed_up,
            not_found_count=total_not_found,
            failed_count=total_failed,
            discovered_secrets_count=len(all_discovered_secrets),
            discovered_secrets=sorted(list(all_discovered_secrets)),
            failed_resources=failed_resources
        )

