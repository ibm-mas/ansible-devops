#!/bin/bash

SRC_DIR=$GITHUB_WORKSPACE/ibm/mas_devops/roles
TO_DIR=$GITHUB_WORKSPACE/docs/roles

mkdir -p $TO_DIR

function copyDoc() {
  ROLE=$1
  cp $SRC_DIR/$ROLE/README.md $TO_DIR/$ROLE.md
}

copyDoc ansible_version_check
copyDoc appconnect_install
copyDoc cos_setup
copyDoc cert_manager_upgrade
copyDoc cert_manager_upgrade_check
copyDoc cp4d_install
copyDoc cp4d_install_services
copyDoc cp4d_upgrade
copyDoc cp4d_wds
copyDoc db2
copyDoc db2_backup
copyDoc db2_restore
copyDoc gencfg_workspace
copyDoc gencfg_jdbc
copyDoc gpu_install
copyDoc install_operator
copyDoc kafka
copyDoc mongodb
copyDoc ocp_deprovision
copyDoc ocp_login
copyDoc ocp_provision
copyDoc ocp_roks_upgrade_registry_storage
copyDoc ocp_setup_cluster_monitoring
copyDoc ocp_setup_common_services
copyDoc ocp_setup_github_oauth
copyDoc ocp_setup_ibm_catalogs
copyDoc ocp_setup_mas_deps
copyDoc ocp_setup_ocs
copyDoc ocp_upgrade
copyDoc ocp_verify
copyDoc sbo_upgrade
copyDoc sls
copyDoc suite_app_config
copyDoc suite_app_install
copyDoc suite_config
copyDoc suite_db2_setup_for_manage
copyDoc suite_dns
copyDoc suite_install
copyDoc suite_mustgather
copyDoc suite_mustgather_download
copyDoc suite_upgrade
copyDoc suite_upgrade_check
copyDoc suite_verify
copyDoc uds
