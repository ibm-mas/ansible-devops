#!/bin/bash

SRC_DIR=$GITHUB_WORKSPACE/ibm/mas_devops/roles
TO_DIR=$GITHUB_WORKSPACE/docs/roles

mkdir -p $TO_DIR

function copyDoc() {
  ROLE=$1
  cp $SRC_DIR/$ROLE/README.md $TO_DIR/$ROLE.md
}

copyDoc amqstreams
copyDoc ansible_version_check
copyDoc cp4d_db2wh
copyDoc cp4d_db2wh_manage_hack
copyDoc cp4d_hack_worker_nodes
copyDoc cp4d_install
copyDoc cp4d_install_services
copyDoc db2u
copyDoc install_operator
copyDoc gencfg_sls
copyDoc gencfg_workspace
copyDoc mongodb
copyDoc ocp_deprovision
copyDoc ocp_login
copyDoc ocp_provision
copyDoc ocp_setup_github_oauth
copyDoc ocp_setup_mas_deps
copyDoc ocp_setup_ocs
copyDoc ocp_verify
copyDoc sls_install
copyDoc suite_app_configure
copyDoc suite_app_install
copyDoc suite_config
copyDoc suite_dns
copyDoc suite_install
copyDoc suite_mustgather
copyDoc suite_verify
copyDoc uds_install
