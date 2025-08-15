MAS DevOps Ansible Collection
===============================================================================
The **ibm.mas_devops** Ansible Collection is published on [Ansible Galaxy](https://galaxy.ansible.com/ui/repo/published/ibm/mas_devops/) and works with all supported releases of IBM Maximo Application Suite.  Release information for the collection can be found in [GitHub](https://github.com/ibm-mas/ansible-devops/releases).


Overview
-------------------------------------------------------------------------------
Many users ask what is the difference between the [MAS Ansible collection](https://github.com/ibm-mas/ansible-devops) and the [MAS CLI](https://github.com/ibm-mas/cli), the best way we have come up with so far to explain the difference is as below:

- The ansible collection is a **toolbox**
- The cli is a **solution** built using that toolbox

Both are viable ways to install, but anyone using the ansible collection needs to understand what they are using; it is a means to create a solution, it's not a solution in it's own right.  **The MAS CLI is the reference solution that we (IBM) offer, based on the tools provided in the ansible collection.**

Using the CLI is the right answer for 95% of users; if you are unsure what is right for you, [start here](https://ibm-mas.github.io/cli/guides/install/).


Usage
-------------------------------------------------------------------------------
### Run a Playbook
The collection includes a number of playbooks that string together multiple roles, you can directly invoke them after installing the collection:

```bash
ansible-playbook ibm.mas_devops.mas_install_core
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

Running in a Container Image
-------------------------------------------------------------------------------
The easiest way to use this collection is to take advantage of the [ibmmas/cli](https://quay.io/repository/ibmmas/cli) container image, this negates the need to install anything on your local machine (other than docker - or podman if you prefer).

```bash
# Run with docker
docker run -ti --rm --pull always quay.io/ibmmas/cli

# Run with podman
podman run -ti --rm --pull always quay.io/ibmmas/cli
```


Local Install
-------------------------------------------------------------------------------
Install the collection direct from [Ansible Galaxy](https://galaxy.ansible.com/ibm/mas_devops), you must also install the [mas-devops](https://pypi.org/project/mas-devops) Python package.  [Python 3.11](https://www.python.org/downloads/) is recommended as it is the most widely used version of Python within our development team, but any in-support version of Python should work.

```
ansible-galaxy collection install ibm.mas_devops
python3 -m pip install mas-devops
```

Optionally, you can also pin the version of the collection that you install, allowing you to control exactly what version of the collection is in use in your solution:

```
ansible-galaxy collection install ibm.mas_devops:18.10.4
python3 -m pip install mas-devops
```

The ansible collection makes use of many dependencies, you can find install scripts showing how we install these dependencies in our own container image in the [ibm-mas/cli-base](https://github.com/ibm-mas/cli-base/tree/stable/image/cli-base/install) repository, the dependencies you need will be determined by the roles that you intend to use, refer to the roles documentation for dependency infomation.

!!! tip
    Many systems contain more than one installation of Python, when you install the **mas-devops** package you must install it to the Python that Ansible is configured to use.  You can check the version being used by Ansible by reviewing the output of `ansible --version`.

    If you see the error message `ERROR! Unexpected Exception, this is probably a bug: No module named 'mas'` it almost certainly means that you have not installed the mas-devops package, or have added it to the wrong instance of Python.


Ansible Automation Platform
-------------------------------------------------------------------------------
If you wish to use [Red Hat Ansible Automation Platform](https://www.redhat.com/en/technologies/management/ansible) then a Automation Execution Environment image is available at [quay.io/ibmmas/ansible-devops-ee](https://quay.io/repository/ibmmas/ansible-devops-ee?tab=tags&tag=latest) that contains the `ibm.mas_devops` collection at the same release level, plus required client packages and access to the automation content collections supported by Red Hat.

More details on how to use the ansible-devops execution environment can be found [here](execution-environment.md)


Action Groups
-------------------------------------------------------------------------------
The collection provide a new action group `ibm.mas_devops.k8s` which can be used to set the default Kubernetes target cluster as an alternative to authenticating with the cluster prior to running our ansible playbooks/roles/actions, see the example below which would return the default storage classes that would be used in this collection for the specified cluster:

```yaml
---
- hosts: localhost
  any_errors_fatal: true
  collections:
    - ibm.mas_devops

  module_defaults:
    group/ibm.mas_devops.k8s:
      host: "<your host url>"
      api_key: "<your api key>"

  tasks:
    - name: "Lookup default storage classes"
      ibm.mas_devops.get_default_storage_classes:
      register: classes

    - debug:
        msg: "{{classes}}"
```


Support
-------------------------------------------------------------------------------
This Ansible collection is developed by the IBM Maximo Application Suite development team, customers may raise support tickets via the same routes they would an issue with the product itself, or [raise an issue directly in the GitHub repository](https://github.com/ibm-mas/ansible-devops/issues).
