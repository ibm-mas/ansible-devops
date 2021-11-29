# MAS Core Service on IBM Cloud ROKS

This master playbook will drive the following playbooks in sequence:

- [Provision & setup OCP on IBM Cloud](ocp.md#provision) (20-30 minutes)
- Install dependencies:
    - [Install MongoDb (Community Edition)](dependencies.md#install-mongodb-ce) (15 minutes)
    - [Install SLS](sls.md#install-sls) (10 minutes)
    - [Install BAS](bas.md#install-bas) (35 minutes)
- Install & configure MAS:
    - [Configure Cloud Internet Services integration](mas.md#cloud-internet-services-integration) (Optional, 1 minute)
    - [Install & configure MAS](mas.md#install-mas) (25 minutes)

All timings are estimates, see the individual pages for each of these playbooks for more information.

## Preparation
Before you run the playbook you need to configure a few things in your `MAS_CONFIG_DIR`:

### Copy your entitlement license key file
Copy the MAS license key file that you obtained from Rational License Key Server to `$MAS_CONFIG_DIR/entitlement.lic` (the file must have this exact name).  During the installation of SLS this license file will be automatically bootstrapped into the system.

!!! important
    Make sure you set `SLS_LICENSE_ID` to the correct value.  For full details on what configuration options are available with the SLS install refer to the [Install SLS](sls.md#install-sls) topic.

### Create a Workspace template
If you want the playbook to create a workspace in MAS you must create a file named `MAS_CONFIG_DIR/workspace.yml` (the exact filename does not matter, as long as the extension is `.yml` or `.yaml` it will be processed when configuring MAS) with the following content:

```yaml
apiVersion: core.mas.ibm.com/v1
kind: Workspace
metadata:
  name: "{{instance_id}}-masdev"
  namespace: "mas-{{instance_id}}-core"
  labels:
    mas.ibm.com/instanceId: "{{instance_id}}"
    mas.ibm.com/workspaceId: "masdev"
spec:
  displayName: "MAS Development"
```

You do not need to create a workspace called `masdev`, you can modify the workspace template above to suite your needs.

## Required environment variables
- `IBMCLOUD_APIKEY` The API key that will be used to create a new ROKS cluster in IBMCloud
- `CLUSTER_NAME` The name to assign to the new ROKS cluster
- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `MAS_ENTITLEMENT_KEY` Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)
- `MAS_CONFIG_DIR` Directory where generated config files will be saved (you may also provide pre-generated config files here)
- `SLS_LICENSE_ID` The license ID must match the license file available in `$MAS_CONFIG_DIR/entitlement.lic`
- `SLS_ENTITLEMENT_KEY` Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)
- `BAS_CONTACT_MAIL` Defines the email for person to contact for BAS
- `BAS_CONTACT_FIRSTNAME` Defines the first name of the person to contact for BAS
- `BAS_CONTACT_LASTNAME` Defines the last name of the person to contact for BAS

## Optional environment variables
- `IBMCLOUD_RESOURCEGROUP` creates an IBM Cloud resource group to be used, if none is passed, `Default` resource group will be used.
- `OCP_VERSION` to override the default version of OCP to use (latest 4.6 release)
- `W3_USERNAME` to enable access to pre-release development builds of MAS
- `ARTIFACTORY_APIKEY`  to enable access to pre-release development builds of MAS
- `MONGODB_NAMESPACE` overrides the Kubernetes namespace where the MongoDb CE operator will be installed, this will default to `mongoce`
- `BAS_USERNAME` BAS default username. If not provided, default username will be `basuser`
- `BAS_PASSWORD` Defines the password for your BAS instance. If not provided, a random 15 character password will be generated
- `BAS_GRAFANA_USERNAME` Defines the username for the BAS Graphana instance, default is `basuser`
- `BAS_GRAFANA_PASSWORD` Defines the password for BAS Graphana dashboard. If not provided, a random 15 character password will be generated
- `BAS_NAMESPACE` Defines the targetted cluster namespace/project where BAS will be installed. If not provided, default BAS namespace will be `ibm-bas`
- `MAS_CATALOG_SOURCE` to override the use of the IBM Operator Catalog as the catalog source
- `MAS_CHANNEL` to override the use of the `8.x` channel
- `MAS_DOMAIN` to set a custom domain for the MAS installation
- `MAS_ICR_CP` to override the value MAS uses for the IBM Entitled Registry (`cp.icr.io/cp`)
- `MAS_ICR_CPOPEN` to override the value MAS uses for the IBM Open Registry (`icr.io/cpopen`)
- `MAS_ENTITLEMENT_USERNAME` to override the username MAS uses to access content in the IBM Entitled Registry
- `CIS_CRN` to enable integration with IBM Cloud Internet Services (CIS) for DNS & certificate management
- `CIS_SUBDOMAIN` if you want to use a subdomain within your CIS instance

!!! tip
    `MAS_ICR_CP`, `MAS_ICR_CPOPEN`, & `MAS_ENTITLEMENT_USERNAME` are primarily used when working with pre-release builds in conjunction with `W3_USERNAME`, `ARTIFACTORY_APIKEY` and the `MAS_CATALOG_SOURCE` environment variables.


## Release build
The simplest configuration to deploy a release build of IBM Maximo Application Suite (core only) with dependencies is:
```bash
# IBM Cloud ROKS configuration
export IBMCLOUD_APIKEY=xxx
export CLUSTER_NAME=xxx

# MAS configuration
export MAS_INSTANCE_ID=$CLUSTER_NAME
export MAS_ENTITLEMENT_KEY=xxx

export MAS_CONFIG_DIR=~/masconfig

# SLS configuration
export SLS_ENTITLEMENT_KEY=xxx
export SLS_LICENSE_ID=xxx

# BAS configuration
export BAS_CONTACT_MAIL=xxx@xxx.com
export BAS_CONTACT_FIRSTNAME=xxx
export BAS_CONTACT_LASTNAME=xxx

ansible-playbook playbooks/lite-core-roks.yml
```


## Pre-release build
The simplest configuration to deploy a pre-release build (only available to IBM employees) of IBM Maximo Application Suite (core only) with dependencies is:

```bash
# IBM Cloud ROKS configuration
export IBMCLOUD_APIKEY=xxx
export CLUSTER_NAME=xxx

# Allow development catalogs to be installed
export W3_USERNAME=xxx
export ARTIFACTORY_APIKEY=xxx

# MAS configuration
export MAS_CATALOG_SOURCE=ibm-mas-operators
export MAS_CHANNEL=m1dev87
export MAS_INSTANCE_ID=$CLUSTER_NAME

export MAS_ICR_CP=wiotp-docker-local.artifactory.swg-devops.com
export MAS_ICR_CPOPEN=wiotp-docker-local.artifactory.swg-devops.com
export MAS_ENTITLEMENT_USERNAME=$W3_USERNAME_LOWERCASE
export MAS_ENTITLEMENT_KEY=$ARTIFACTORY_APIKEY

export MAS_CONFIG_DIR=~/masconfig

# SLS configuration
export SLS_ENTITLEMENT_KEY=xxx
export SLS_LICENSE_ID=xxx

# BAS configuration
export BAS_CONTACT_MAIL=xxx@xxx.com
export BAS_CONTACT_FIRSTNAME=xxx
export BAS_CONTACT_LASTNAME=xxx

ansible-playbook playbooks/lite-core-roks.yml
```
