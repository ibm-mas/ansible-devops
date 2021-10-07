# MAS Playbooks

## Install MAS
Before you use this playbook you will likely want to edit the `mas_config` variable to supply your own configurtation, instead of the sample data provided.

### Required environment variables
- `MAS_INSTANCE_ID` Declare the instance ID for the MAS install
- `MAS_ENTITLEMENT_KEY` Provide your IBM entitlement key
- `MAS_CONFIG_DIR` Directory where generated config files will be saved (you may also provide pre-generated config files here)

### Optional environment variables
- `MAS_CATALOG_SOURCE` Set to `ibm-mas-operators` if you want to deploy pre-release development builds
- `MAS_CHANNEL` Override the default release channel (8.x)
- `MAS_DOMAIN` Override the default generated domain for the MAS installation
- `MAS_ICR_CP` Override the registry source for all container images deployed by the MAS operator
- `MAS_ICR_CPOPEN` Override the registry source for all container images deployed by the MAS operator
- `MAS_ENTITLEMENT_USERNAME` Override the default entitlement username (cp)

### Example usage: release build

```bash
export MAS_INSTANCE_ID=xxx
export MAS_ENTITLEMENT_KEY=xxx

ansible-playbook playbooks/mas/install-suite.yml
```

!!! note
    Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)


### Example usage: pre-release build

```bash
export MAS_CATALOG_SOURCE=ibm-mas-operators
export MAS_CHANNEL=8.5.0-pre.m2dev85
export MAS_INSTANCE_ID=xxx

export MAS_ICR_CP=wiotp-docker-local.artifactory.swg-devops.com
export MAS_ICR_CPOPEN=wiotp-docker-local.artifactory.swg-devops.com
export MAS_ENTITLEMENT_USERNAME=$W3_USERNAME_LOWERCASE
export MAS_ENTITLEMENT_KEY=$ARTIFACTORY_APIKEY

export MAS_CONFIG_DIR=~/masconfig

ansible-playbook playbooks/mas/install-suite.yml
```

!!! important
    You must have already installed the development (pre-release) catalogs, pre-release builds are not available directly from the IBM Operator Catalog.


## Cloud Internet Services integration
This optional feature allows you to integrate MAS with an existing instance of [IBM Cloud Internet Services](https://www.ibm.com/cloud/cloud-internet-services) (CIS) to provide automatic DNS management and certificates signed by LetsEncrypt.

To utilise this feature you must set the optional `MAS_DOMAIN` detailed previously, and define additional CIS-specific environment variables as follows.

### Required environment variables
- `CIS_CRN` which can be obtained from your CIS service overview page, it will be in the format: `crn:v1:bluemix:public:internet-svcs:global:a/02fd888448c1415baa2bcd65684e4db3:9969652f-6955-482b-b59c-asdasasdede50c::`
- `IBMCLOUD_APIKEY` Your IBM Cloud API key with DNS API write access. Note: (This API key will be stored in your cluster for DNS challenge when requesting new certs)

!!! important "TODO"
    Support `CIS_APIKEY` instead as we don't really want to re-use the main `IBMCLOUD_APIKEY` API key as it has too wide scope for CIS.  Document what scope to set up the API key with and what steps etc.

    Could we even use our API key to create this new API key automatically so that the user does not need to do anything?

### Optional environment variables
- `CIS_SUBDOMAIN` Subdomain used by your DNS server. It allow you to reuse CIS for multiple MAS Instances.
- `CIS_SKIP_DNS_ENTRIES` Skips DNS entries creation if you are have them
- `CIS_SKIP_CLUSTER_ISSUER` Skips Cluster Issuer CR creation and CIS webhook installation if you already have it
- `UPDATE_DNS_ENTRIES` Whether to replace DNS entries already created
- `OCP_INGRESS` Default to your cluster OCP ingress. This value is used as the target for the DNS entries

### Example
This example will configure MAS to run under the domain **mas.internal.mydomain.com** with all DNS entries for MAS managed by a CIS instance controlling **mydomain.com**.

```bash
export MAS_INSTANCE_ID=xxx
export MAS_ENTITLEMENT_KEY=xxx
export MAS_DOMAIN=mas.internal.mydomain.com

# Configure CIS integration
export IBMCLOUD_APIKEY=xxx
export CIS_SUBDOMAIN=mas.internal
export CIS_CRN=crn:v1:bluemix:public:internet-svcs:global:a/02fd888448c1415baa2bcd65684e4db3:9969652f-6955-482b-b59c-asdasasdede50c::

ansible-playbook playbooks/mas/install-suite.yml
```

----


## Install MAS Application
Install a MAS (Gen2) application, supported applications:

- Manage
- Health

!!! note
    Today, this only supports deployment of a MAS application with default settings.

### Example
```bash
export MAS_INSTANCE_ID=xxx
export MAS_WORKSPACE_ID=masdev
export MAS_APP_ID=manage

ansible-playbook playbooks/mas/configure-app.yml
```


----


## Configure MAS Application
Configure a MAS (Gen2) application in a workspace, supported applications:

- Manage
- Health

!!! note
    Today, this only supports configuring a workspace with default settings.

### Example

```bash
export MAS_INSTANCE_ID=xxx
export MAS_WORKSPACE_ID=masdev
export MAS_APP_ID=manage

ansible-playbook playbooks/mas/configure-app.yml
```


----


## Manage Db2 Hack
This should should be part of the Manage operator, but is not so we have to do it as a seperate step in the install flow for now.  This will configure the Db2 database instance and create a new schema named `maximo` (the default schema name used by the Manage application).

```bash
ansible-playbook playbooks/mas/hack-manage-db2.yml
```