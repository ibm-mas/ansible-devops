# MAS Devops Ansible Collection

## Requirements

### Python & Ansible
[Python 3.8](https://www.python.org/downloads/) is recommended as it is the most widely used version of Python within our development team, but any in-support 3.x version of Python should work fine:

The following python modules are required in order to use this collection.

- **openshift**
- **ansible**

#### Useful commands
- Confirm availability and version: `python --version`
- Installed Python modules: `python -m pip install ansible openshift==0.11.2`
- Confirm that ansible has been correctly installed: `ansible-playbook --version`


### IBM Cloud CLI
If you are using this collection to manage an OpenShift cluster in IBM Cloud RedHat OpenShift Kubernetes Service (ROKS), then you must install the IBM Cloud CLI:

#### Useful commands
- Install: `curl -sL https://raw.githubusercontent.com/IBM-Cloud/ibm-cloud-developer-tools/master/linux-installer/idt-installer | bash`
- Confirm availability and version: `ibmcloud version`


### OpenShift CLI
If you do not already have the `oc` command line tool, you can download the version corresponding to the OpenShift cluster you are using, from the Command Line Tools option under the help menu

#### Useful commands
- Confirm availability and version: `oc version`

!!! note
    This is a rather annoying chicken and egg situation, you need to have a running OCP instance before you can access the command line client that we want to use to automate setting up that instance.

    See [ibm-mas/ansible-devops#2](https://github.com/ibm-mas/ansible-devops/issues/2)


## Installation
Install the collection direct from [Ansible Galaxy](https://galaxy.ansible.com/ibm/mas_devops)

```
ansible-galaxy collection install ibm.mas_devops
```

## Change Log
Note that links to pull requests prior to public release of the code (4.0) direct to IBM GitHub Enterprise, and will only be accessible to IBM employees.

- `4.2` Add support for Tekton pipelines ([#34](https://github.com/ibm-mas/ansible-devops/pull/34))
- `4.1` Add `ocp_verify` role and associated playbook ([#20](https://github.com/ibm-mas/ansible-devops/pull/20))
- `4.0` Initial Public Release on ibm.mas_devops ([#5](https://github.com/ibm-mas/ansible-devops/pull/5))
- `3.3` Support configurable SLS settings ([#53](https://github.ibm.com/maximoappsuite/mas-devops-ansible/pull/53))
- `3.2` Add support for BAS ([#44](https://github.ibm.com/maximoappsuite/mas-devops-ansible/pull/44))
- `3.1` Add support for SLS ([#35](https://github.ibm.com/maximoappsuite/mas-devops-ansible/pull/35))
- `3.0` Switch to config dir instead of config file list ([#36](https://github.ibm.com/maximoappsuite/mas-devops-ansible/pull/36))
- `2.7` Support AirGap install of MAS ([#28](https://github.ibm.com/maximoappsuite/mas-devops-ansible/pull/28))
- `2.6` Add support for Gen2 application mgmt (install and configure) ([#24](https://github.ibm.com/maximoappsuite/mas-devops-ansible/pull/24))
- `2.5` Add support for Watson Studio ([#16](https://github.ibm.com/maximoappsuite/mas-devops-ansible/pull/16))
- `2.4` Add support for MongoDb Community Edition ([#25](https://github.ibm.com/maximoappsuite/mas-devops-ansible/pull/25))
- `2.3` Add support for IBM Cloud resource groups ([#20](https://github.ibm.com/maximoappsuite/mas-devops-ansible/pull/20))
- `2.2` Support DNS and certificate mgmt with CIS & LetsEncrypt ([#10](https://github.ibm.com/maximoappsuite/mas-devops-ansible/pull/10))
- `2.1` Add support for AMQ Streams (Kafka) ([#19](https://github.ibm.com/maximoappsuite/mas-devops-ansible/pull/19))
- `2.0` Major refactor of the roles and playbooks ([#17](https://github.ibm.com/maximoappsuite/mas-devops-ansible/pull/17))
- `1.2` Add initial Spark support (incomplete) ([#15](https://github.ibm.com/maximoappsuite/mas-devops-ansible/pull/15))
- `1.1` Enable db2wh SSL and generate jdbccfg for MAS ([#9](https://github.ibm.com/maximoappsuite/mas-devops-ansible/pull/9))
- `1.0` Initial release
