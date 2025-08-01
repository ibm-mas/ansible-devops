#!/bin/bash

SRC_DIR=$GITHUB_WORKSPACE/ibm/mas_devops/roles
TO_DIR=$GITHUB_WORKSPACE/docs/roles

mkdir -p $TO_DIR

function copyDoc() {
  ROLE=$1
  cp $SRC_DIR/$ROLE/README.md $TO_DIR/$ROLE.md
}

copyDoc aiservice
copyDoc aiservice_kmodels
copyDoc aiservice_odh
copyDoc aiservice_tenant
copyDoc ansible_version_check
copyDoc appconnect
copyDoc arcgis
copyDoc aws_bucket_access_point
copyDoc aws_documentdb_user
copyDoc aws_policy
copyDoc aws_route53
copyDoc aws_user_creation
copyDoc aws_vpc
copyDoc cert_manager
copyDoc cis
copyDoc common_services
copyDoc configure_manage_eventstreams
copyDoc cos
copyDoc cos_bucket
copyDoc cp4d
copyDoc cp4d_admin_pwd_update
copyDoc cp4d_service
copyDoc db2
copyDoc dro
copyDoc eck
copyDoc entitlement_key_rotation
copyDoc gencfg_jdbc
copyDoc gencfg_mongo
copyDoc gencfg_watsonstudio
copyDoc gencfg_workspace
copyDoc grafana
copyDoc ibm_catalogs
copyDoc ibmcloud_resource_key
copyDoc kafka
copyDoc key_rotation
copyDoc mirror_case_prepare
copyDoc mirror_extras_prepare
copyDoc mirror_ocp
copyDoc mirror_images
copyDoc mongodb
copyDoc nvidia_gpu
copyDoc ocp_cluster_monitoring
copyDoc ocp_config
copyDoc ocp_idms
copyDoc ocp_deprovision
copyDoc ocp_efs
copyDoc ocp_github_oauth
copyDoc ocp_login
copyDoc ocp_node_config
copyDoc ocp_provision
copyDoc ocp_roks_upgrade_registry_storage
copyDoc ocp_simulate_disconnected_network
copyDoc ocp_upgrade
copyDoc ocp_verify
copyDoc ocs
copyDoc opentelemetry
copyDoc registry
copyDoc sls
copyDoc smtp
copyDoc suite_app_backup_restore
copyDoc suite_app_config
copyDoc suite_app_install
copyDoc suite_app_uninstall
copyDoc suite_app_upgrade
copyDoc suite_app_rollback
copyDoc suite_app_verify
copyDoc suite_backup_restore
copyDoc suite_config
copyDoc suite_db2_setup_for_manage
copyDoc suite_db2_setup_for_facilities
copyDoc suite_dns
copyDoc suite_certs
copyDoc suite_install
copyDoc suite_manage_bim_config
copyDoc suite_manage_birt_report_config
copyDoc suite_manage_customer_files_config
copyDoc suite_manage_attachments_config
copyDoc suite_manage_imagestitching_config
copyDoc suite_manage_import_certs_config
copyDoc suite_manage_load_dbc_scripts
copyDoc suite_manage_logging_config
copyDoc suite_manage_pvc_config
copyDoc suite_upgrade
copyDoc suite_rollback
copyDoc suite_uninstall
copyDoc suite_verify
copyDoc turbonomic
copyDoc uds
