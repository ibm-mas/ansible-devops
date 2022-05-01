# CP4D Playbooks

CloudPak for Data support comes in two flavours: CP4D v3.5 and CP4D v4.  For users of MAS v8.7 or later only CP4D v4 is supported.  MAS 8.6 with the January 2022 maintenance updates supports both, and earlier version of MAS only support CP4D v3.5.

- CloudPak for Data v3.5 is installed from the IBM Operator Catalog using the `v1.0` channel to the `cpd-meta-ops` namespace.
- CloudPak for Data v4 is installed from the IBM Operator Catalog using the `v2.0` channel to the `ibm-common-services` namespace.

!!! warning
    The credentials to sign-in when deploying CP4D v3.5 are the defaults, which are `admin/password`.  Yes, really!

-------------------------------------------------------------------------------

## Hack Worker Nodes
This playbook will auto-detect whether CP4D v3.5 or v4 is active in the cluster.  Refer to the [cp4d_hack_worker_nodes](../roles/cp4d_hack_worker_nodes.md) role documentation for more information.

```bash
export CLUSTER_NAME=masinst1
export CLUSTER_TYPE=roks
export IBMCLOUD_APIKEY=xxx
export CPD_ENTITLEMENT_KEY=xxx

ansible-playbook ibm.mas_devops.cp4d_hack_worker_nodes
```

-------------------------------------------------------------------------------

## Install Services: Fullstack
This playbook will install CP4D and enable **Watson Studio** with Watson Machine Learning, Apache Spark, & Watson AI OpenScale capabilities enabled.

- **Watson Machine Learning** As part of Watson Studio, Watson Machine Learning helps data scientists and developers accelerate AI and machine learning deployment.
- **Apache Spark** Apache Spark is a runtime environment configured inside of Watson Studio similar to a Python Runtime environment.  When Spark is enabled from CP4D, you can opt to create a notebook and choose Spark as runtime to expand data modeling capabilities.
- **Watson AI OpenScale**  Watson OpenScale enables tracking AI models in production, validation and test models to mitigate operational risks.

!!! info "Application Support"
    For more information on how Predict and HP Utilities make use of Watson Studio, refer to [Predict/HP Utilities documentation](https://www.ibm.com/docs/en/mhmpmh-and-p-u/8.2.0?topic=started-getting-data-scientists)

    - [Predict](https://www.ibm.com/docs/en/mas84/8.4.0?topic=applications-maximo-predict) requires Watson Studio, Machine Learning and Spark; Openscale is an optional dependency
    - [Health & Predict Utilities](https://www.ibm.com/docs/en/mas84/8.4.0?topic=solutions-maximo-health-predict-utilities) requires Watson Studio base capability only

Refer to the [cp4d_install](../roles/cp4d_install.md) and [cp4d_install_services](../roles/cp4d_install_services.md) role documentation for more information.

```bash
export CPD_VERSION=cpd40
export CPD_STORAGE_CLASS=ibmc-file-gold-gid
export CPD_METADB_BLOCK_STORAGE_CLASS=ibmc-block-gold

ansible-playbook ibm.mas_devops.cp4d_install_services_fullstack
```

-------------------------------------------------------------------------------

## Install Services: Watson Studio
This playbook will install CP4D and install the **Watson Studio** with Watson Machine Learning, Apache Spark, & Watson AI OpenScale capabilities enabled.

- **Watson Machine Learning** As part of Watson Studio, Watson Machine Learning helps data scientists and developers accelerate AI and machine learning deployment.
- **Apache Spark** Apache Spark is a runtime environment configured inside of Watson Studio similar to a Python Runtime environment.  When Spark is enabled from CP4D, you can opt to create a notebook and choose Spark as runtime to expand data modeling capabilities.
- **Watson AI OpenScale**  Watson OpenScale enables tracking AI models in production, validation and test models to mitigate operational risks.

!!! info "Application Support"
    For more information on how Predict and HP Utilities make use of Watson Studio, refer to [Predict/HP Utilities documentation](https://www.ibm.com/docs/en/mhmpmh-and-p-u/8.2.0?topic=started-getting-data-scientists)

    - [Predict](https://www.ibm.com/docs/en/mas84/8.4.0?topic=applications-maximo-predict) requires Watson Studio, Machine Learning and Spark; Openscale is an optional dependency
    - [Health & Predict Utilities](https://www.ibm.com/docs/en/mas84/8.4.0?topic=solutions-maximo-health-predict-utilities) requires Watson Studio base capability only

Refer to the [cp4d_install](../roles/cp4d_install.md) and [cp4d_install_services](../roles/cp4d_install_services.md) role documentation for more information.

```bash
export CPD_VERSION=cpd40
export CPD_STORAGE_CLASS=ibmc-file-gold-gid
export CPD_METADB_BLOCK_STORAGE_CLASS=ibmc-block-gold

ansible-playbook ibm.mas_devops.cp4d_install_services_watsonstudio
```

-------------------------------------------------------------------------------

## Install Services: Discovery
This playbook will install CP4D and enable the CP4D **Discovery** service.

Refer to the [cp4d_install](../roles/cp4d_install.md) and [cp4d_install_services](../roles/cp4d_install_services.md) role documentation for more information.

```bash
export CPD_VERSION=cpd40
export CPD_STORAGE_CLASS=ibmc-file-gold-gid
export CPD_METADB_BLOCK_STORAGE_CLASS=ibmc-block-gold

ansible-playbook ibm.mas_devops.cp4d_install_services_discovery
```
-------------------------------------------------------------------------------

## Create Discovery Instance
This playbook will auto-detect whether CP4D v4 is active in the cluster, and Create the Disocvery instance.
Refer to the [cp4d_wds](../roles/cp4d_wds.md) role documentation for more information.
`CP4D_USERNAME` and `CP4D_PASSWORD` is not required if you didn't  change the initial admin password after install discovery.

```bash
export CP4D_USERNAME=admin
export CP4D_PASSWORD=xxxx
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig

ansible-playbook ibm.mas_devops.cp4d_create_discovery_instance
```

-------------------------------------------------------------------------------