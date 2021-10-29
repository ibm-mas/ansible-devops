ansible-galaxy collection build
ansible-galaxy collection install ibm-mas_devops-4.3.0.tar.gz --ignore-certs --force
rm ibm-mas_devops-4.3.0.tar.gz
echo "Done"
