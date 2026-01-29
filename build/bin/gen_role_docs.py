"""
Generate role documentation by copying README files from roles directory.

This script is used by mkdocs-gen-files plugin to automatically copy role
README files into the docs/roles directory during the mkdocs build process.

The script will skip generation if the target files already exist, even if
they are out of date. To regenerate docs, manually delete the docs/roles
directory before running mkdocs serve/build.
"""

import os
from pathlib import Path
import mkdocs_gen_files

# Define the list of roles to document
ROLES = [
    "aiservice",
    "aiservice_odh",
    "aiservice_tenant",
    "ansible_version_check",
    "arcgis",
    "aws_bucket_access_point",
    "aws_documentdb_user",
    "aws_policy",
    "aws_route53",
    "aws_user_creation",
    "aws_vpc",
    "cert_manager",
    "cis",
    "configure_manage_eventstreams",
    "cos",
    "cos_bucket",
    "cp4d",
    "cp4d_admin_pwd_update",
    "cp4d_service",
    "db2",
    "dro",
    "eck",
    "entitlement_key_rotation",
    "gencfg_jdbc",
    "gencfg_mongo",
    "gencfg_watsonstudio",
    "gencfg_workspace",
    "grafana",
    "ibm_catalogs",
    "ibmcloud_resource_key",
    "kafka",
    "key_rotation",
    "longhorn",
    "mirror_case_prepare",
    "mirror_extras_prepare",
    "mirror_ocp",
    "mirror_images",
    "mongodb",
    "nvidia_gpu",
    "ocp_cluster_monitoring",
    "ocp_config",
    "ocp_idms",
    "ocp_deprovision",
    "ocp_efs",
    "ocp_github_oauth",
    "ocp_login",
    "ocp_node_config",
    "ocp_provision",
    "ocp_roks_upgrade_registry_storage",
    "ocp_simulate_disconnected_network",
    "ocp_upgrade",
    "ocp_verify",
    "ocs",
    "registry",
    "sls",
    "smtp",
    "suite_app_backup_restore",
    "suite_app_config",
    "suite_app_install",
    "suite_app_uninstall",
    "suite_app_upgrade",
    "suite_app_rollback",
    "suite_backup_restore",
    "suite_config",
    "suite_db2_setup_for_manage",
    "suite_db2_setup_for_facilities",
    "suite_dns",
    "suite_certs",
    "suite_install",
    "suite_manage_bim_config",
    "suite_manage_birt_report_config",
    "suite_manage_customer_files_config",
    "suite_manage_attachments_config",
    "suite_manage_imagestitching_config",
    "suite_manage_import_certs_config",
    "suite_manage_load_dbc_scripts",
    "suite_manage_logging_config",
    "suite_manage_pvc_config",
    "suite_upgrade",
    "suite_rollback",
    "suite_uninstall",
    "suite_verify",
    "turbonomic",
]

# Get the root directory (where mkdocs.yml is located)
# Script is in build/bin/, so go up two levels to reach root
root_dir = Path(__file__).parent.parent.parent

# Source and destination directories
src_dir = root_dir / "ibm" / "mas_devops" / "roles"
dest_dir = Path("roles")

# Check if docs/roles directory exists in the actual filesystem
# If it does, skip generation entirely
physical_dest_dir = root_dir / "docs" / "roles"
if physical_dest_dir.exists() and any(physical_dest_dir.iterdir()):
    print(f"Role documentation already exists in {physical_dest_dir}. Skipping generation.")
    print("To regenerate docs, delete the docs/roles directory before running mkdocs.")
else:
    print(f"Generating role documentation from {src_dir} to {dest_dir}")

    # Copy each role's README to the docs/roles directory
    for role in ROLES:
        src_file = src_dir / role / "README.md"
        dest_file = dest_dir / f"{role}.md"

        if src_file.exists():
            # Read the source README
            with open(src_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Write to the virtual mkdocs file system
            with mkdocs_gen_files.open(dest_file, "w") as f:
                f.write(content)

            print(f"  ✓ Copied {role}/README.md -> {dest_file}")
        else:
            print(f"  ✗ Warning: {src_file} not found, skipping {role}")

    print(f"Role documentation generation complete!")

# Made with Bob
