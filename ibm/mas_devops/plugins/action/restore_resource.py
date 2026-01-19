#!/usr/bin/env python3

import logging
import os
import yaml
import urllib3

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.utils.display import Display
from kubernetes import client, config
from kubernetes.dynamic import DynamicClient

from mas.devops.restore import loadYamlFile, restoreResource

urllib3.disable_warnings()  # Disabling warnings will prevent InsecureRequestWarnings from dynClient

display = Display()


# Custom logging handler to forward Python logs to Ansible display
class AnsibleDisplayHandler(logging.Handler):
    """Custom logging handler that forwards log messages to Ansible's display system"""
    
    def emit(self, record):
        try:
            msg = self.format(record)
            if record.levelno >= logging.ERROR:
                display.error(msg)
            elif record.levelno >= logging.WARNING:
                display.warning(msg)
            else:
                display.vvv(msg)  # Use vvv for info/debug messages (visible with -vvv)
        except Exception:
            self.handleError(record)


# Configure logging to use both console and Ansible display
def setup_logging():
    """Setup logging to output to both console and Ansible display"""
    # Create formatter
    formatter = logging.Formatter('%(asctime)s %(name)-20s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Add Ansible display handler
    ansible_handler = AnsibleDisplayHandler()
    ansible_handler.setFormatter(formatter)
    root_logger.addHandler(ansible_handler)
    
    # Also add console handler for direct execution/debugging
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)


# Initialize logging
setup_logging()


def apply_overrides(resource_data: dict, override_values: dict, resource_kind: str) -> dict:
    """
    Apply override values to a resource based on key paths, filtered by resource kind.
    
    Args:
        resource_data: The resource dictionary to modify
        override_values: Dictionary mapping resource kinds to lists of override dictionaries
        resource_kind: The kind of the current resource (e.g., 'Suite', 'Secret', 'ConfigMap')
        
    Returns:
        dict: Modified resource data
        
    Example:
        override_values = {
            'Suite': [
                {'spec.domain': 'mydomain.com'},
                {'spec.clusterIssuer.name': 'bob'}
            ],
            'Secret': [
                {'data.value': 'newvalue'}
            ]
        }
    """
    if not override_values or resource_kind not in override_values:
        return resource_data
    
    kind_overrides = override_values[resource_kind]
    if not kind_overrides:
        return resource_data
    
    for override_dict in kind_overrides:
        for key_path, new_value in override_dict.items():
            # Skip if value is NO_OVERRIDE (use backup value)
            if new_value == "NO_OVERRIDE":
                display.vvv(f"Skipping override for {resource_kind}: {key_path} (NO_OVERRIDE)")
                continue
            
            # Split the key path by dots to navigate nested structure
            keys = key_path.split('.')
            
            # Navigate to the parent of the target key
            current = resource_data
            for i, key in enumerate(keys[:-1]):
                if key not in current:
                    # Create missing intermediate dictionaries
                    current[key] = {}
                elif not isinstance(current[key], dict):
                    # Can't navigate further if intermediate value is not a dict
                    display.warning(f"Cannot apply override '{key_path}': '{'.'.join(keys[:i+1])}' is not a dictionary")
                    break
                current = current[key]
            else:
                # Set the final value
                final_key = keys[-1]
                old_value = current.get(final_key, '<not set>')
                current[final_key] = new_value
                display.vvv(f"Applied override for {resource_kind}: {key_path}: {old_value} -> {new_value}")
    
    return resource_data


class ActionModule(ActionBase):
    """
    Restore Kubernetes resources from a backup archive directory.
    Automatically discovers and restores all resources found in the backup.
    
    - If a resource doesn't exist, it will be created
    - If a resource exists and replace_resource=True, it will be updated (replaced)
    - If a resource exists and replace_resource=False, it will be skipped
    
    Usage Example
    -------------
    tasks:
      - name: "Restore and replace specific MAS Suite resources"
        ibm.mas_devops.restore_resource:
          backup_path: "/backup/backup-250115-120000-suite"
          resource_kinds:
            - Secret
            - ConfigMap
          replace_resource: true
      
      - name: "Restore all resources (skip existing)"
        ibm.mas_devops.restore_resource:
          backup_path: "/backup/backup-250115-120000-suite"
          replace_resource: false
      
      - name: "Restore resources with overrides"
        ibm.mas_devops.restore_resource:
          backup_path: "/backup/backup-250115-120000-suite"
          resource_kinds:
            - Suite
            - Secret
            - ConfigMap
          replace_resource: true
          override_values:
            Suite:
              - spec.domain: mydomain.com
              - spec.clusterIssuer.name: bob
            Secret:
              - data.value: newvalue
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

        backup_path = self._task.args.get('backup_path')
        replace_resource = self._task.args.get('replace_resource', True)
        resource_kinds = self._task.args.get('resource_kinds', None)
        override_values = self._task.args.get('override_values', None)

        if backup_path is None or backup_path == "":
            raise AnsibleError(f"Error: backup_path argument was not provided")
        
        # Check if backup path exists
        if not os.path.exists(backup_path):
            raise AnsibleError(f"Error: backup_path does not exist: {backup_path}")
        
        # Check if resources directory exists
        resources_path = os.path.join(backup_path, 'resources')
        if not os.path.exists(resources_path):
            raise AnsibleError(f"Error: resources directory not found in backup: {resources_path}")
        
        display.v(f"Starting restore of MAS Suite resources from '{backup_path}'")
        display.v(f"Replace existing resources: {'enabled' if replace_resource else 'disabled'}")
        if override_values:
            override_kinds = ', '.join(override_values.keys())
            display.v(f"Override values will be applied for resource kinds: {override_kinds}")

        total_created = 0
        total_updated = 0
        total_skipped = 0
        total_failed = 0
        failed_resources = []  # Track failed resources with details

        # Discover all resource types in the backup
        try:
            resource_dirs = [d for d in os.listdir(resources_path) 
                           if os.path.isdir(os.path.join(resources_path, d))]
        except Exception as e:
            raise AnsibleError(f"Error listing resource directories in {resources_path}: {e}")
        
        if not resource_dirs:
            display.warning(f"No resource directories found in {resources_path}")
            return dict(
                message="No resources found to restore",
                failed=False,
                changed=False,
                success=True,
                created_count=0,
                updated_count=0,
                skipped_count=0,
                failed_count=0,
                failed_resources=[]
            )
        
        display.v(f"Found {len(resource_dirs)} resource type(s) in backup: {', '.join(sorted(resource_dirs))}")
        
        # Filter resource directories if specific kinds requested
        if resource_kinds:
            # Convert resource_kinds to lowercase directory names (add 's' suffix)
            requested_dirs = set()
            for kind in resource_kinds:
                # Handle both singular and plural forms
                dir_name = kind.lower()
                if not dir_name.endswith('s'):
                    dir_name = dir_name + 's'
                requested_dirs.add(dir_name)
            
            # Filter to only requested directories
            resource_dirs = [d for d in resource_dirs if d in requested_dirs]
            
            if not resource_dirs:
                display.warning(f"None of the requested resource kinds found in backup")
                return dict(
                    message="No requested resources found to restore",
                    failed=False,
                    changed=False,
                    success=True,
                    created_count=0,
                    updated_count=0,
                    skipped_count=0,
                    failed_count=0,
                    failed_resources=[]
                )
            
            display.v(f"Restoring {len(resource_dirs)} requested resource type(s): {', '.join(sorted(resource_dirs))}")
        
        # Process each resource directory
        for resource_dir in sorted(resource_dirs):
            resource_dir_path = os.path.join(resources_path, resource_dir)
            
            # Get all YAML files in this directory
            try:
                yaml_files = [f for f in os.listdir(resource_dir_path) if f.endswith('.yaml')]
            except Exception as e:
                display.warning(f"Error listing files in {resource_dir_path}: {e}")
                continue
            
            if not yaml_files:
                display.v(f"No YAML files found in {resource_dir}/")
                continue
            
            display.v(f"Restoring {len(yaml_files)} resource(s) from {resource_dir}/")
            
            # Process each YAML file
            for yaml_file in sorted(yaml_files):
                yaml_file_path = os.path.join(resource_dir_path, yaml_file)
                
                # Load the resource data
                resource_data = loadYamlFile(yaml_file_path)
                if not resource_data:
                    display.warning(f"Failed to load {yaml_file_path}")
                    total_failed += 1
                    failed_resources.append({
                        'kind': 'Unknown',
                        'name': yaml_file.replace('.yaml', ''),
                        'description': f"Unknown/{yaml_file.replace('.yaml', '')}",
                        'error': 'Failed to load YAML file'
                    })
                    continue
                
                # Apply overrides if provided
                if override_values:
                    resource_kind = resource_data.get('kind', 'Unknown')
                    resource_data = apply_overrides(resource_data, override_values, resource_kind)
                
                # Restore the resource
                success, resource_name, status_msg = restoreResource(
                    dynClient, resource_data, namespace=None, replace_resource=replace_resource
                )
                
                if success:
                    if status_msg == "updated":
                        # Resource was updated
                        total_updated += 1
                    elif status_msg == "skipped":
                        # Resource was skipped
                        total_skipped += 1
                    else:
                        # Resource was created
                        total_created += 1
                else:
                    total_failed += 1
                    kind = resource_data.get('kind', 'Unknown')
                    failed_resources.append({
                        'kind': kind,
                        'name': resource_name,
                        'description': f"{kind}/{resource_name}",
                        'error': status_msg
                    })
            
            display.v(f"Progress: {total_created} created, {total_updated} updated, {total_skipped} skipped, {total_failed} failed")

        display.v(f"Restore complete: {total_created} resources created, {total_updated} updated, {total_skipped} skipped, {total_failed} failed")

        # Determine if the restore was successful
        has_failures = total_failed > 0
        
        return dict(
            message=f"Restored {total_created + total_updated} MAS Suite resources ({total_created} created, {total_updated} updated, {total_skipped} skipped)" + (f" with {total_failed} failures" if has_failures else ""),
            failed=has_failures,
            changed=(total_created + total_updated) > 0,
            success=not has_failures,
            created_count=total_created,
            updated_count=total_updated,
            skipped_count=total_skipped,
            failed_count=total_failed,
            failed_resources=failed_resources
        )

# Made with Bob