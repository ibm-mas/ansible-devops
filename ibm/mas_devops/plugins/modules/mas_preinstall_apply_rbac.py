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
module: mas_preinstall_apply_rbac

short_description: Apply MAS pre-install RBAC resources

version_added: "1.0.0"

description: 
    - Applies the necessary RBAC resources for MAS installation
    - Supports minimal, namespaced, and cluster permission modes
    - Can apply RBAC for specific MAS applications

options:
    mas_version:
        description: MAS version for RBAC manifests
        required: true
        type: str
    mas_instance_id:
        description: MAS instance ID
        required: true
        type: str
    permission_mode:
        description: Permission mode (minimal, namespaced, or cluster)
        required: true
        type: str
        choices: ['minimal', 'namespaced', 'cluster']
    selected_apps:
        description: List of selected apps for RBAC
        required: false
        type: list
        elements: str
    rbac_root_dir:
        description: RBAC root directory
        required: false
        type: str
    kubeconfig:
        description: Path to kubeconfig file
        required: false
        type: str

author:
    - IBM MAS DevOps Team
'''

EXAMPLES = r'''
- name: Apply pre-install RBAC with default settings
  mas_preinstall_apply_rbac:
    mas_version: "9.0"
    mas_instance_id: "inst1"
    permission_mode: "namespaced"

- name: Apply pre-install RBAC for specific apps
  mas_preinstall_apply_rbac:
    mas_version: "9.0"
    mas_instance_id: "inst1"
    permission_mode: "cluster"
    selected_apps:
      - core
      - manage
      - iot
'''

RETURN = r'''
message:
    description: Success message
    type: str
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule
import sys

def main():
    module = AnsibleModule(
        argument_spec=dict(
            mas_version=dict(type='str', required=True),
            mas_instance_id=dict(type='str', required=True),
            permission_mode=dict(
                type='str',
                required=True,
                choices=['minimal', 'namespaced', 'cluster']
            ),
            selected_apps=dict(type='list', elements='str', required=False),
            rbac_root_dir=dict(type='str', required=False),
            kubeconfig=dict(type='str', required=False)
        ),
        supports_check_mode=False
    )

    try:
        # Add python-devops to path
        sys.path.insert(0, '/c/wksp/python-devops/src')
        
        from mas.devops.pre_install import applyPreInstallMASRBAC
        from openshift.dynamic import DynamicClient
        from kubernetes import config
        
        # Load kubeconfig
        if module.params.get('kubeconfig'):
            config.load_kube_config(config_file=module.params['kubeconfig'])
        else:
            config.load_kube_config()
        
        # Create dynamic client
        dynClient = DynamicClient(config.new_client_from_config())
        
        # Prepare parameters
        selectedApps = module.params.get('selected_apps')
        rbacRootDir = module.params.get('rbac_root_dir')
        
        # Apply RBAC
        applyPreInstallMASRBAC(
            dynClient=dynClient,
            masVersion=module.params['mas_version'],
            masInstanceId=module.params['mas_instance_id'],
            permissionMode=module.params['permission_mode'],
            selectedApps=selectedApps if selectedApps else None,
            rbacRootDir=rbacRootDir if rbacRootDir else None
        )
        
        module.exit_json(
            changed=True,
            message='Pre-install RBAC applied successfully'
        )
            
    except ImportError as e:
        module.fail_json(msg=f"Failed to import required Python modules: {str(e)}")
    except Exception as e:
        module.fail_json(msg=f"Failed to apply pre-install RBAC: {str(e)}")


if __name__ == '__main__':
    main()

# Made with Bob
