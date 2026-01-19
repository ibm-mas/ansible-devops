export MAS_INSTANCE_ID=backup
export MAS_BACKUP_DIR=/Users/whitfiea/temp/mas_backups
export ROLE_NAME=suite_backup

export SUITE_BACKUP_VERSION=260119-112418

/Users/whitfiea/Work/Git/ibm-mas/ansible-devops/.venv/bin/ansible-playbook  ibm.mas_devops.run_role -vvv 