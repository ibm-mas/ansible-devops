# Contributing

## Building the collection locally

```bash
cd mas/devops

ansible-galaxy collection build --force && ansible-galaxy collection install mas-devops-2.0.0.tar.gz -p /home/david/.ansible/collections --force

ansible-playbook ../../playbook.yml
```
