# Ansible DevOps Collection for IBM Maximo Application Suite

## Documentation
[https://ibm-mas.github.io/ansible-devops/](https://ibm-mas.github.io/ansible-devops/)

## Change Log
Note that links to pull requests prior to public release of the code (4.0) direct to IBM GitHub Enterprise, and will only be accessible to IBM employees.

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
    - Add support for Cloud Object Storage ([#122](https://github.com/ibm-mas/ansible-devops/pull/122))
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
- `3.2` Adding support to BAS ([#44](https://github.ibm.com/maximoappsuite/mas-devops-ansible/pull/44))
- `3.1` Adding support to SLS ([#35](https://github.ibm.com/maximoappsuite/mas-devops-ansible/pull/35))
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
