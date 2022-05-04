# Dependencies Playbooks

## Install AMQ Streams
AMQ Streams operator will be installed into the `amq-streams` namespace, a cluster named `maskafka` will be created using the small configuration and `ibmc-block-gold` as the storage class.  The generated configuration for MAS will be available in the `~/masconfig` directory on the local system.

Refer to the [amqstreams](../roles/amqstreams.md) role documentation for more information.

```bash
export KAFKA_STORAGE_CLASS=ibmc-block-gold
export MAS_INSTANCE_ID=masdev1
export MAS_CONFIG_DIR=~/masconfig

ansible-playbook playbooks/dependencies/install-amqstreams.yml
```

## Install MongoDb (CE)
MongoDb CE operator will be installed into the `mongoce` namespace, a 3 node cluster cluster will be created.  The cluster will bind six 20GB `ibmc-block-gold` PVCs, these provide persistence for the data and system logs across the three nodes.  The generated configuration for MAS will be available in the `~/masconfig` directory on the local system.

Refer to the [mongodb](../roles/mongodb.md) role documentation for more information.

```bash
export MONGODB_STORAGE_CLASS=ibmc-block-gold
export MAS_INSTANCE_ID=masdev1
export MAS_CONFIG_DIR=~/masconfig

ansible-playbook playbooks/dependencies/install-mongodb-ce.yml
```


## Install UDS
Installs **IBM User Data Services**.  Refer to the [uds_install](../roles/uds_install.md) role documentation for more information.

```bash
export UDS_STORAGE_CLASS=ibmc-block-bronze
export UDS_CONTACT_EMAIL=john@email.com
export UDS_CONTACT_FIRSTNAME=john
export UDS_CONTACT_LASTNAME=winter
export MAS_INSTANCE_ID=masdev1
export MAS_CONFIG_DIR=~/masconfig

ansible-playbook playbooks/dependencies/install-uds.yml
```


## Install SLS
Before you use this playbook you will likely want to edit the `MAS_CONFIG_DIR` variable to supply your own configuration, instead of the sample data provided. Refer to the [sls_install](../roles/sls_install.md) role documentation for more information. The playbook will also call the [gencfg_sls](../roles/gencfg_sls.md) role after the install to generate the slscfg. 

### Example usage: release build

```bash
export SLS_INSTANCE_ID=xxx
export SLS_ENTITLEMENT_KEY=xxx
export SLS_MONGODB_CFG_FILE="/etc/mas/mongodb.yml"
export MAS_INSTANCE_ID=masdev1
export MAS_CONFIG_DIR=~/masconfig

ansible-playbook playbooks/dependencies/install-sls.yml
```

!!! note
    Lookup your entitlement key from the [IBM Container Library](https://myibm.ibm.com/products-services/containerlibrary)


### Example usage: pre-release build

```bash
export SLS_CATALOG_SOURCE=ibm-sls-operators
export SLS_CHANNEL=3.1.0-pre.stable
export SLS_INSTANCE_ID=xxx
export SLS_MONGODB_CFG_FILE="/etc/mas/mongodb.yml"
export MAS_INSTANCE_ID=masdev1
export MAS_CONFIG_DIR=~/masconfig

export SLS_ICR_CP=wiotp-docker-local.artifactory.swg-devops.com
export SLS_ICR_CPOPEN=wiotp-docker-local.artifactory.swg-devops.com
export SLS_ENTITLEMENT_USERNAME=$W3_USERNAME_LOWERCASE
export SLS_ENTITLEMENT_KEY=$ARTIFACTORY_APIKEY


ansible-playbook playbooks/dependencies/install-sls.yml
```

!!! important
    You must have already installed the development (pre-release) catalogs, pre-release builds are not available directly from the IBM Operator Catalog.


## Install AppConnect
AppConnect will be installed into the `ibm-app-connect` namespace, using `ibmc-file-gold-gid` as the storage class.  The generated configuration for MAS will be available in the `~/masconfig` directory on the local system.

Refer to the [appconnect_install](../roles/appconnect_install.md) role documentation for more information.

```bash
export APPCONNECT_STORAGE_CLASS=ibmc-file-gold-gid
export APPCONNECT_ENTITLEMENT_KEY=xxx
export MAS_INSTANCE_ID=masdev1
export MAS_CONFIG_DIR=~/masconfig

ansible-playbook playbooks/dependencies/install-appconnect.yml
```


## Install NVIDIA
Installs **NVIDIA Graphical Processing Unit (GPU)** and its prerequisite **Node Feature Discovery (NFD)**. The NFD Operator is installed using the Red Hat Operators catalog source and the GPU operator is installed using the Certified Operators catalog source. 

Refer to the [nvidia](../roles/nvidia.md) role documentation for more information.

### Example usage: 

```bash
export NFD_NAMESPACE=nfd-operator
export NFD_CHANNEL=stable
export NVIDIA_NAMESPACE=nvidia-gpu-operator
export NVIDIA_CHANNEL=v1.9

ansible-playbook playbooks/dependencies/nvidia.yml
```


## Install DB2
Installs **IBM DB2** using the db2u operator. Refer to the [db2u] role documentation for more information. The generated configuration for MAS will be available in the `~/masconfig` directory on the local system.

```bash
export DB2U_META_STORAGE_CLASS=ibmc-file-gold
export DB2U_DATA_STORAGE_CLASS=ibmc-block-gold
export DB2U_INSTANCE_NAME=db2u-db01
export ENTITLEMENT_KEY=xxx
export MAS_INSTANCE_ID=masdev1
export MAS_CONFIG_DIR=~/masconfig

ansible-playbook playbooks/dependencies/install-db2.yml
```


## Gencfg UDS
Generates BasCfg file. Refer to the [gencfg_uds](../roles/gencfg_uds.md) role documentation for more information.

```bash
export UDS_ENDPOINT_URL="https://uds-endpoint-ibm-common-services.apps.masocp-xxxxxx.....com"
export UDS_API_KEY=xxx
export UDS_TLS_CERT_LOCAL_FILE_PATH="/etc/mas/uds.crt"
export UDS_CONTACT_EMAIL=john@email.com
export UDS_CONTACT_FIRSTNAME=john
export UDS_CONTACT_LASTNAME=winter
export MAS_INSTANCE_ID=masdev1
export MAS_CONFIG_DIR=~/masconfig

ansible-playbook playbooks/dependencies/gencfg-uds.yml
```


## Gencfg SLS
Generates SlsCfg file. Refer to the [gencfg_sls](../roles/gencfg_sls.md) role documentation for more information.

### Example usage: release build

```bash
export SLSCFG_URL="https://sls-xxxxxx.ibm-sls-xxxxxx.ibm-sls-xxxxxx.apps.masocp-xxxxxx.....com"
export SLS_REGISTRATION_KEY=xxx
export SLS_TLS_CERT_LOCAL_FILE_PATH="/etc/mas/sls.crt"
export MAS_INSTANCE_ID=masdev1
export MAS_CONFIG_DIR=~/masconfig

ansible-playbook playbooks/dependencies/gencfg-sls.yml
```