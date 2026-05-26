# -----------------------------------------------------------
# Licensed Materials - Property of IBM
# 5737-M66
# (C) Copyright IBM Corp. 2026 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication, or disclosure
# restricted by GSA ADP Schedule Contract with IBM Corp.
# -----------------------------------------------------------

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = r'''
---
module: mas_preinstall_check_permissions

short_description: Check cluster permissions for MAS pre-install RBAC operations

version_added: "1.0.0"

description: 
    - Validates that the current user has the necessary permissions to apply MAS pre-install RBAC resources
    - Returns detailed information about allowed and denied permissions

options:
    kubeconfig:
        description: Path to kubeconfig file
        required: false
        type: str

author:
    - IBM MAS DevOps Team
'''

EXAMPLES = r'''
- name: Check permissions for RBAC operations
  mas_preinstall_check_permissions:
  register: permission_check

- name: Display permission check results
  debug:
    msg: "{{ permission_check.results }}"
'''

RETURN = r'''
results:
    description: List of permission check results
    type: list
    returned: always
    elements: dict
    contains:
        verb:
            description: The API verb being checked
            type: str
        resource:
            description: The resource type
            type: str
        group:
            description: The API group
            type: str
        namespace:
            description: The namespace (if applicable)
            type: str
        allowed:
            description: Whether the permission is allowed
            type: bool
denied_count:
    description: Number of denied permissions
    type: int
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule
import sys

def main():
    module = AnsibleModule(
        argument_spec=dict(
            kubeconfig=dict(type='str', required=False)
        ),
        supports_check_mode=True
    )

    try:
        # Add python-devops to path
        sys.path.insert(0, '/c/wksp/python-devops/src')
        
        from mas.devops.pre_install import permissionCheckForRBAC
        from openshift.dynamic import DynamicClient
        from kubernetes import config
        
        # Load kubeconfig
        if module.params.get('kubeconfig'):
            config.load_kube_config(config_file=module.params['kubeconfig'])
        else:
            config.load_kube_config()
        
        # Create dynamic client
        dynClient = DynamicClient(config.new_client_from_config())
        
        # Run permission check
        results = permissionCheckForRBAC(dynClient)
        
        # Count denied permissions
        denied = [r for r in results if not r['allowed']]
        denied_count = len(denied)
        
        # Format results for display
        formatted_results = []
        for result in results:
            allowed = 'ALLOWED' if result['allowed'] else 'DENIED'
            namespace = f" (namespace={result['namespace']})" if 'namespace' in result else ''
            formatted_results.append(
                f"{allowed}: {result['verb']} {result['resource']} in {result['group']}{namespace}"
            )
        
        if denied_count > 0:
            module.fail_json(
                msg=f"{denied_count} permission(s) denied",
                results=results,
                formatted_results=formatted_results,
                denied_count=denied_count
            )
        else:
            module.exit_json(
                changed=False,
                results=results,
                formatted_results=formatted_results,
                denied_count=0
            )
            
    except ImportError as e:
        module.fail_json(msg=f"Failed to import required Python modules: {str(e)}")
    except Exception as e:
        module.fail_json(msg=f"Unexpected error during permission check: {str(e)}")


if __name__ == '__main__':
    main()

# Made with Bob
