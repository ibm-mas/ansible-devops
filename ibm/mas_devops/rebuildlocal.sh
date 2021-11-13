ansible-galaxy collection build
ansible-galaxy collection install ibm-mas_devops-4.3.0.tar.gz --ignore-certs --force
rm ibm-mas_devops-4.3.0.tar.gz
source /Users/quinteiro/Documents/projects/mas/cicd/automation/scripts/pipeline-iot-run.sh
echo "Done"
