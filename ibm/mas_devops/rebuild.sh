rm -rf /Users/alefq/Documents/projects/mas/testconfig/** 
rm -rf /Users/alefq/Documents/projects/mas/masconfig/**
ansible-galaxy collection build --force
ansible-galaxy collection install ibm-mas_devops-11.0.0.tar.gz --force
ansible-playbook playbooks/run_role.yml

