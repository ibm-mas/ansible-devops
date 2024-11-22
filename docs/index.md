MAS DevOps Ansible Collection
===============================================================================
The **ibm.mas_devops** Ansible Collection is published on [Ansible Galaxy](https://galaxy.ansible.com/ui/repo/published/ibm/mas_devops/) and works with all supported releases of IBM Maximo Application Suite.  Release information for the collection can be found in [GitHub](https://github.com/ibm-mas/ansible-devops/releases).


Usage
-------------------------------------------------------------------------------
### Run a Playbook
The collection includes a number of playbooks that string together multiple roles, you can directly invoke them after installing the collection:

```bash
ansible-playbook ibm.mas_devops.lite_core_roks
```

### Run a Role
If you only want to perform a single action, you can directly invoke one of our roles from the command line without the need to build a playbook:

```bash
ansible localhost -m include_role -a name=ibm.mas_devops.ocp_verify
```

You can also use the **run_role** playbook:

```bash
ROLE_NAME=cert_manager ansible-playbook ibm.mas_devops.run_role
```

Running in Docker
-------------------------------------------------------------------------------
The easiest way to use this collection is to take advantage of the [ibmmas/cli](https://quay.io/repository/ibmmas/cli) container image, this negates the need to install anything on your local machine (other than docker - or podman if you prefer).

```bash
docker run -ti --rm --pull always quay.io/ibmmas/cli
```


Local Install
-------------------------------------------------------------------------------
### Install Python & Ansible
[Python 3.9](https://www.python.org/downloads/) is recommended as it is the most widely used version of Python within our development team, but any in-support 3.x version of Python should work fine.

```bash
python3 --version
python3 -m pip install ansible junit_xml pymongo xmljson jmespath kubernetes==12.0.1 openshift==0.12.1
ansible --version
ansible-playbook --version
```

We recommend using the latest version of ansible-core at all times (at time of writing this was v2.12.3) and the collection has a minimum supported version of ansible-core v2.10.3 which is enforced by the `ibm.mas_devops.ansible_version_check` role.

### Install OpenShift CLI
If you do not already have the `oc` command line tool, you can download it as below:

```
wget -q https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/4.14.7/openshift-client-linux-4.14.7.tar.gz
tar -zxf openshift-client-linux.tar.gz
mv oc kubectl /usr/local/bin/
rm -rf openshift-client-linux.tar.gz
oc version
```

### Install IBM Cloud CLI
If you are using this collection to manage an OpenShift cluster in IBM Cloud RedHat OpenShift Kubernetes Service (ROKS), then you must also install the IBM Cloud CLI:

```bash
curl -sL https://raw.githubusercontent.com/IBM-Cloud/ibm-cloud-developer-tools/master/linux-installer/idt-installer | bash
ibmcloud version`
```

### Install the Ansible Collection
Install the collection direct from [Ansible Galaxy](https://galaxy.ansible.com/ibm/mas_devops)

```
ansible-galaxy collection install ibm.mas_devops
```

Optionally, you can also pin the version of the collection that you install, allowing you to control exactly what version of the collection is in use in your automation:
```
ansible-galaxy collection install ibm.mas_devops:18.10.4
```

Ansible Automation Platform
-------------------------------------------------------------------------------
If you wish to use [Red Hat Ansible Automation Platform](https://www.redhat.com/en/technologies/management/ansible) then a Automation Execution Environment image is available at [quay.io/ibmmas/ansible-devops-ee](https://quay.io/repository/ibmmas/ansible-devops-ee?tab=tags&tag=latest) that contains the `ibm.mas_devops` collection at the same release level, plus required client packages and access to the automation content collections supported by Red Hat.

More details on how to use the ansible-devops execution environment can be found [here](execution-environment.md)


Support
-------------------------------------------------------------------------------
This Ansible collection is developed by the IBM Maximo Application Suite development team, customers may raise support tickets via the same routes they would an issue with the product itself, or [raise an issue directly in the GitHub repository](https://github.com/ibm-mas/ansible-devops/issues).
