# MAS Devops Ansible Collection

## Requirements
The following python modules are required in order to use this collection.
- openshift
- ansible

`python -m pip install ansible openshift==0.11.2`

## Installation
Releases are available to install from Artifactory:

```bash
MASDEVOPS_VERSION=2.0.0
wget --header=X-JFrog-Art-API:$ARTIFACTORY_API_KEY  https://na.artifactory.swg-devops.com/artifactory/wiotp-generic-release/maximoappsuite/mas-devops-ansible/$MASDEVOPS_VERSION/mas-devops-$MASDEVOPS_VERSION.tar.gz

ansible-galaxy collection install ./mas-devops-$MASDEVOPS_VERSION.tar.gz --force
```
