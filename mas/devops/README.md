# MAS Devops Ansible Collection

## Fyre QuickBurn

### Full stack deployment on Fyre quickburn cluster
Note that the quickburn fullstack does not include Db2, as it will not fit onto the cluster.

```bash
# Fyre credentials
export FYRE_USERNAME=xxx
export FYRE_APIKEY=xxx
# Cluster configuration
export CLUSTER_NAME=xxx
export OCP_VERSION=4.6.16
export FYRE_CLUSTER_SIZE=large
export FYRE_PRODUCT_ID=225
# Artifactory image pull credentials
export W3_USERNAME=xxx
export ARTIFACTORY_APIKEY=xxx
# MAS configuration
export INSTANCE_ID=xxx
# IBM entitlement key
export ENTITLEMENT_USERNAME=$W3_USERNAME
export ENTITLEMENT_KEY=$ARTIFACTORY_APIKEY

ansible-playbook playbooks/fullstack-quickburn.yml
```

### Provision & setup quickburn cluster on Fyre
A new cluster can be created from scratch as follows, this process will take about 20-30 minutes to complete.

```bash
export FYRE_USERNAME=xxx
export FYRE_APIKEY=xxx
export CLUSTER_NAME=xxx

export OCP_VERSION=4.6.16
export FYRE_CLUSTER_SIZE=large
export FYRE_PRODUCT_ID=225
ansible-playbook playbooks/provision-quickburn.yml
```

### Deprovision quickburn cluster on Fyre
Destroy an existing quickburn cluster.  Note that you may only have one quickburn cluster active in your account at any time.

```bash
export FYRE_USERNAME=xxx
export FYRE_APIKEY=xxx
export CLUSTER_NAME=xxx
ansible-playbook playbooks/deprovision-quickburn.yml
```


## IBMCloud ROKS

### Full stack deployment on IBM Cloud ROKS
```bash
# IBM Cloud credentials
export IBMCLOUD_APIKEY=xxx
# Cluster configuration
export CLUSTER_NAME=xxx
export OCP_VERSION=4.6.23_openshift
export ROKS_ZONE=lon02
export ROKS_FLAVOR=b3c.16x64
export ROKS_WORKERS=3
# CP4D config
export CPD_ENTITLEMENT_KEY=xxx
# Artifactory image pull credentials
export W3_USERNAME=xxx
export ARTIFACTORY_APIKEY=xxx
# MAS configuration
export INSTANCE_ID=xxx
# IBM entitlement key
export ENTITLEMENT_USERNAME=$W3_USERNAME
export ENTITLEMENT_KEY=$ARTIFACTORY_APIKEY

ansible-playbook playbooks/fullstack-roks.yml
```

### Provision & setup a cluster on IBMCloud
A new cluster can be created from scratch as follows, this process will take about 20-30 minutes to complete.

```bash
export IBMCLOUD_APIKEY=xxx
export CLUSTER_NAME=xxx

export OCP_VERSION=4.6.23_openshift
export ROKS_ZONE=lon02
export ROKS_FLAVOR=b3c.16x64
export ROKS_WORKERS=3
ansible-playbook playbooks/provision-roks.yml
```

### Deprovision cluster on IBMCloud

```bash
export IBMCLOUD_APIKEY=xxx
export CLUSTER_NAME=xxx

ansible-playbook playbooks/deprovision-roks.yml
```


## MAS

### Deploy Suite
```bash
export W3_USERNAME=xxx
export ARTIFACTORY_APIKEY=xxx
export INSTANCE_ID=xxx
export WORKSPACE_ID=xxx

# Optional - if you want to use released container images
# export ICR_CP=cp.icr.io/cp
# export ICR_CPOPEN=icr.io

# Assuming you want to use Artifactory as ICR, otherwise set to your
# real entitlement key
export ENTITLEMENT_USERNAME=$W3_USERNAME
export ENTITLEMENT_KEY=$ARTIFACTORY_APIKEY

ansible-playbook playbooks/install-suite.yml
```
