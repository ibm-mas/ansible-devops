ansible-galaxy collection build --force
ansible-galaxy collection install ibm-mas_devops-13.0.0.tar.gz --force
export MAS_CHANNEL=dev
export MAS_INSTANCE_ID=upgtest
export MAS_APP_CHANNEL=dev
export MAS_APP_ID=assist
export SKIP_COMPATIBILITY_CHECK=true
export MAS_UPGRADE_DRYRUN=true
echo "------------------
echo "MAS Core Upgrade"
echo "------------------
export ROLE_NAME=suite_upgrade
ansible-playbook ibm.mas_devops.run_role.yml
echo "------------------
echo "MAS Assist Upgrade"
echo "------------------
export ROLE_NAME=suite_app_upgrade
ansible-playbook ibm.mas_devops.run_role.yml
