ansible-galaxy collection build --force
ansible-galaxy collection install ibm-mas_devops-14.0.0.tar.gz --force
ansible-playbook ibm.mas_devops.run_role
