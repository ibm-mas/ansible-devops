# MAS Devops Ansible Collection

## Requirements

### Python & Ansible
[Python 3.8](https://www.python.org/downloads/) is recommended as it is the most widely used version of Python within our development team, but any in-support 3.x version of Python should work fine:

The following python modules are required in order to use this collection.

- **openshift**
- **ansible**

!!! important
    As of version 6 of this collection the dependencies have changed. The upgrade from `community.kubernetes` to `kubernetes.core` necessitates an upgrade in the version of the kubernetes and openshift modules from v11 to v12.


#### Useful commands
- Confirm availability and version: `python3 --version`
- Installed Python modules: `python3 -m pip install ansible junit_xml pymongo xmljson kubernetes==12.0.1 openshift==0.12.1`
- Confirm that ansible has been correctly installed: `ansible-playbook --version`


### IBM Cloud CLI
If you are using this collection to manage an OpenShift cluster in IBM Cloud RedHat OpenShift Kubernetes Service (ROKS), then you must install the IBM Cloud CLI:

#### Useful commands
- Install: `curl -sL https://raw.githubusercontent.com/IBM-Cloud/ibm-cloud-developer-tools/master/linux-installer/idt-installer | bash`
- Confirm availability and version: `ibmcloud version`

### OpenShift CLI
If you do not already have the `oc` command line tool, you can download it as below:

```
wget -q https://github.com/openshift/origin/releases/download/v3.11.0/openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit.tar.gz
tar -xvzf openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit.tar.gz
mv openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit/oc /usr/local/bin/
rm -rf openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit.tar.gz
```

#### Useful commands
- Confirm availability and version: `oc version`


## Installation
Install the collection direct from [Ansible Galaxy](https://galaxy.ansible.com/ibm/mas_devops)

```
ansible-galaxy collection install ibm.mas_devops
```

## Change Log
Note that links to pull requests prior to public release of the code (4.0) direct to IBM GitHub Enterprise, and will only be accessible to IBM employees.

- `6.5` Multiple Updates:
    - Add JDBCCfg generator role ([#188](https://github.com/ibm-mas/ansible-devops/pull/188))
    - Add mustgather clusterTask to pipeline and new mustgather_download playbook ([#222](https://github.com/ibm-mas/ansible-devops/pull/222))
- `6.4` Add support for MVI deployment ([#196](https://github.com/ibm-mas/ansible-devops/pull/196))
- `6.3` Allow `ocp_server` and `ocp_token` to be used for `ocp_login` ([#211](https://github.com/ibm-mas/ansible-devops/pull/211))
- `6.2` Multiple Updates:
    - Support manual upgrade approvals ([#205](https://github.com/ibm-mas/ansible-devops/pull/205))
    - Add support for Db2u operator ([#203](https://github.com/ibm-mas/ansible-devops/pull/203))
    - Add Workspace config generator ([#189](https://github.com/ibm-mas/ansible-devops/pull/189))
- `6.1` Create WSL project and enable HPU deploy ([#201](https://github.com/ibm-mas/ansible-devops/pull/201))
- `6.0` Multiple Updates:
    - Upgrade to [kubernetes.core](https://docs.ansible.com/ansible/latest/collections/kubernetes/core/) Ansible module ([#194](https://github.com/ibm-mas/ansible-devops/pull/194))
    - Remove BAS support (replaced by UDS) ([#194](https://github.com/ibm-mas/ansible-devops/pull/194))
- `5.3` Multiple Updates:
    - Add support for db2wh backup & restore ([#133](https://github.com/ibm-mas/ansible-devops/pull/133))
    - Add support for appConnect ([#170](https://github.com/ibm-mas/ansible-devops/pull/170))
    - Switch BAS from FullDeployment to AnalyticsProxy ([#178](https://github.com/ibm-mas/ansible-devops/pull/178))
- `5.2` Multiple Updates:
    - Support MongoDb CPU and memory configuration ([#158](https://github.com/ibm-mas/ansible-devops/pull/158))
    - Separate CIS_APIKEY support for MAS Installation ([#156](https://github.com/ibm-mas/ansible-devops/pull/156))
    - Support configurable prometheus storage & retention policy ([#151](https://github.com/ibm-mas/ansible-devops/pull/151))
    - Support configurable application spec ([#160](https://github.com/ibm-mas/ansible-devops/pull/160))
- `5.1` Multiple Updates:
    - Add support for Cloud Object Storage setup ([#122](https://github.com/ibm-mas/ansible-devops/pull/122))
    - Conditional application deployment in Tekton pipelines ([#118](https://github.com/ibm-mas/ansible-devops/pull/118))
    - Add support for CP4D v4 alongside existing support for v3.5 ([#93](https://github.com/ibm-mas/ansible-devops/pull/93))
- `5.0` Multiple Updates:
    - Add support for AI Applications' must-gather tooling ([#91](https://github.com/ibm-mas/ansible-devops/pull/91))
    - Migrate airgap support into ibm.mas_airgap collection ([#38](https://github.com/ibm-mas/ansible-devops/pull/38))
    - Support for Assist application ([#76](https://github.com/ibm-mas/ansible-devops/pull/76))
    - Significant refactoring for CP4D support ([#68](https://github.com/ibm-mas/ansible-devops/pull/68))
    - Migrate build system to GitHub Actions ([#68](https://github.com/ibm-mas/ansible-devops/pull/68))
- `4.5` Add support for Manage ([#61](https://github.com/ibm-mas/ansible-devops/pull/61))
- `4.4` Add CP4D and DB2W playbooks ([#51](https://github.com/ibm-mas/ansible-devops/pull/51))
- `4.3` Add support for playbook junit result generation ([#39](https://github.com/ibm-mas/ansible-devops/pull/39))
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
