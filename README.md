# Ansible DevOps Tooling Collection for IBM Maximo Application Suite

## Future Work
- [x] Rewrite config management, support loading configs from https://github.ibm.com/maximoappsuite/devops-configs and remove configs embedded in the collection.
- [ ] Make Db2 deployment (and all future deployments) generate a JdbcCfg yaml file that can be passed to the suite install (see above) so that MAS is automatically configured for the deployed DB instance.
- [ ] Support restoring a Db2 backup, to significantly speed up Manage deployment time (as manage will not need to init the database from scratch).
- [ ] Obtain and record measurements for deployment time, broken down by stage.
- [ ] Create exhaustive, high-quality, documentation, none of this is any good if no-one know how to use it.
- [ ] Support mongodb deployment.
- [ ] Support kafka deployment.
- [ ] Work out full list of dependencies we need to support and add support for them.
- [ ] Support customizable suite CR spec.
- [ ] Investigate migrating code from this collection into MAS operators (only when everything we are using is 100% stable/reliable).
- [ ] Setup db2wh for Manage and Health
- [ ] Restore db2wh backup on a newly created db2wh instance
- [ ] Add capability to approve install plan

## Documentation
See [mas/devops/README.md](mas/devops/README.md).

## Change Log
- `1.0` Initial release

## Installation
Download mas-devops:

```bash
wget --header=X-JFrog-Art-API:$ARTIFACTORY_API_KEY  https://na.artifactory.swg-devops.com/artifactory/wiotp-generic-release/maximoappsuite/mas-devops-ansible/$MASDEVOPS_VERSION/mas-devops-$MASDEVOPS_VERSION.tar.gz
```
Install collection:

```bash
ansible-galaxy collection install ./mas-devops-1.0.0.tar.gz --force
```

## Usage

### Directly invoke the playbook
```bash
ansible-playbook ~/.ansible/collections/ansible_collections/mas/devops/playbooks/quickburn.yml
```

### Indirectly import the playbook in your own playbook
```yaml
---
- name: Quickburn
  import_playbook: "~/.ansible/collections/ansible_collections/mas/devops/playbooks/fullstack-quickburn.yml"
```
