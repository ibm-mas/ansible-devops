rm ibm-mas_devops-4.5.0.tar.gz
ansible-galaxy collection build
ansible-galaxy collection install ibm-mas_devops-4.5.0.tar.gz --force --ignore-certs
