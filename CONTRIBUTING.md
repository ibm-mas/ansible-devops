# Building Locally
```bash
cd mas/devops

ansible-galaxy collection build --force && ansible-galaxy collection install mas-devops-1.0.0.tar.gz -p /home/david/.ansible/collections/ansible_collections --force

ansible-playbook ../../playbook.yml
```
