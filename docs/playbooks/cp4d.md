# CP4D Playbooks
These playbooks deploys Cloud Pak for Data from the IBM Operator Catalog using the `v1.0` channel.

!!! warning
    The credentials to sign-in are the defaults for CP4D, which are `admin/password`.

    Yes, really!

-------------------------------------------------------------------------------

## Create DB2 Instance

This playbook creates a Db2 Warehouse instance in Cloud Pak for Data.  A Db2 Warehouse cluster will be created and a public TLS encrypted route is configured to allow external access to the cluster. The certificates are available from the `internal-tls` secret in the `cpd-meta-ops` namespace.

The default user is `db2inst1` and the password is available in the `instancepassword` secret in the same namespace.

You can examine the deployed resources in the `cpd-meta-ops` namespace:

```bash
oc -n cpd-meta-ops get cpdservice,db2ucluster

NAME                                                       MESSAGE                 REASON   STATUS       LASTACTION   PHASE        CODE
cpdservice.metaoperator.cpd.ibm.com/cpdservice-db2wh       Completed                        Ready        CPDInstall   Ready        0
cpdservice.metaoperator.cpd.ibm.com/cpdservice-db2wh-dmc   CPD binary is running            Installing   CPDInstall   Installing   1

NAME                                            STATE      AGE
db2ucluster.db2u.databases.ibm.com/db2u-bludb   NotReady   8m44s
```

!!! tip
    The playbook will generate a yaml file containing the definition of a Secret and JdbcCfg resource that can be used to configure the deployed cluster as the MAS system JDBC datasource.

    This file can be directly applied using `oc apply -f /tmp/jdbccfg-cp4ddb2wh-system.yaml` or added to the `mas_config` list variable used by the `ibm.mas_devops.suite_install` role to deploy and configure MAS.


### Required Variables

- `CPD_VERSION` DB2 instance version that will be provisioned accordingly to CP4D version defined. Supported versions are `cpd35` (for CP4D 3.5) and `cpd40` (for CP4D 4.0)
- `CPD_NAMESPACE` Provide the namespace where Cloud Pak for Data is installed. CP4D playbooks create it, by default, in `cpd-meta-ops`
- `DB2WH_INSTANCE_NAME` Name of your database instance, visible in CP4D dashboard. Example: `db2w-iot`
- `MAS_INSTANCE_ID` Provide the MAS instance ID that will be used in any generated MAS configuration files

### Optional Variables

In addition to the above, these are the optional variables you can set before running the playbook:

- `DB2WH_ADDON_VERSION` version of the DB2 Warehouse instance to be creared. Default is `11.5.5.1-cn3-x86_64`
- `DB2WH_ADMIN_USER` user in CP4D that can access the database. The user must exist, it is not created by this playbook. Default is `admin`
- `DB2WH_ADMIN_PASSWORD` password of the user identified above. Default is `password`
- `DB2WH_TABLE_ORG` the way database tables will be organized. It can be either `ROW` or `COLUMN`. Default is `ROW`
- `DB2WH_META_STORAGE_CLASS` store class used to create the configuration storage.
- `DB2WH_META_STORAGE_SIZE_GB` size of configuration persistent volume, in gigabytes. Default is `20`
- `DB2WH_USER_STORAGE_CLASS` store class used to create the user storage.
- `DB2WH_USER_STORAGE_SIZE_GB` size of user persistent volume, in gigabytes. Default is `100`
- `DB2WH_BACKUP_STORAGE_CLASS` store class used to create the backup storage
- `DB2WH_BACKUP_STORAGE_SIZE_GB` size of backup persistent volume, in gigabytes. Default is `100`
- `DB2WH_LOGS_STORAGE_CLASS` store class used to store db2wh logs.
- `DB2WH_LOGS_STORAGE_SIZE_GB` size of logs persistent volume, in gigabytes. Default is `100`
- `DB2WH_TEMP_STORAGE_SIZE_GB` size of temporary persistent volume, in gigabytes. Default is `100` (only applicable for CP4D 4.0)
- `DB2WH_TEMP_STORAGE_CLASS` store class used for temporary storage.
- `MAS_CONFIG_DIR` Provide the path of the folder where the JDBCCfg yaml containing the credentials of this database will be saved at the end of the process.
- `MAS_CONFIG_SCOPE` indicates what scope the JDBCCfg instance will be named to be used later by configure-suite playbook. Possible valeus are `system`, `wsapp`, `app`, and `ws`. Default is `system`
- `MAS_APP_ID` Id of the application that will bind the DB2W. Required only if `MAS_CONFIG_SCOPE` is `wsapp` or `app`
- `MAS_WORKSPACE_ID` Id of the workspace that will bind the DB2W. Required only if `MAS_CONFIG_SCOPE` is `wsapp` or `ws`

### Usage

Here is how you can use this playbook:

```bash
export CPD_VERSION=4.0
export CPD_NAMESPACE=cpd-meta
export DB2WH_INSTANCE_NAME=db2w-shared
export MAS_INSTANCE_ID=inst1
export MAS_CONFIG_DIR=~/masconfig

ansible-playbook playbooks/cp4d/create-db2-instance.yml
```


-------------------------------------------------------------------------------

## Hack Worker Nodes

Refer to the [cp4d_hack_worker_nodes](../roles/cp4d_hack_worker_nodes.md) role documentation for more information.

```bash
export CLUSTER_NAME=masinst1
export CLUSTER_TYPE=roks
export IBMCLOUD_APIKEY=xxx
export CPD_ENTITLEMENT_KEY=xxx

ansible-playbook playbooks/cp4d/hack-worker-nodes.yml
```

-------------------------------------------------------------------------------

## Install Services: Db2

This playbook will enable the CP4D **Db2 Warehouse** service.


### Example usage
```bash
export CPD_ENTITLEMENT_KEY=xxx
export CPD_STORAGE_CLASS=ibmc-file-gold-gid
export MAS_INSTANCE_ID=inst1

ansible-playbook playbooks/cp4d/install-db2.yml
```

### Debugging Db2 install
The following command may come in handy:

```bash
oc -n cpd-meta-ops get formations.db2u.databases.ibm.com db2wh-db01 -o go-template='{{range .status.components}}{{printf "%s,%s,%s\n" .kind .name .status.state}}{{end}}' | column -s, -t
```


### Required environment variables

- `CPD_VERSION` CP4D version to be installed. Supported versions are `cpd35` (for CP4D 3.5) and `cpd40` (for CP4D 4.0)
- `CPD_ENTITLEMENT_KEY` An [IBM entitlement key](https://myibm.ibm.com/products-services/containerlibrary) that includes access to Cloud Pak for Data 3.5.0
- `CPD_STORAGE_CLASS` Provide the storage class to use for Db2
- `MAS_INSTANCE_ID` Provide the MAS instance ID that will be used in any generated MAS configuration files

### Example Usage

Here is how you can use this playbook:

```bash
export CPD_ENTITLEMENT_KEY=xxx
export CPD_STORAGE_CLASS=ibmc-file-gold-gid

ansible-playbook playbooks/cp4d/install-cp4d.yml
```

-------------------------------------------------------------------------------

## Install Services: Fullstack

This playbook will install CP4D, with all services that are supported by one or more applications in Maximo Application Suite enabled:

- **Db2 Warehouse** & **Db2 Management Console**
- **Watson Studio** with **Watson Machine Learning**, **Apache Spark**, & **Watson AI OpenScale**

For more information refer to the documentation for the individual Db2 and Watson Studio playbooks above.

### Required environment variables

- `CPD_VERSION` CP4D version to be installed. Supported versions are `cpd35` (for CP4D 3.5) and `cpd40` (for CP4D 4.0)
- `CPD_ENTITLEMENT_KEY` An [IBM entitlement key](https://myibm.ibm.com/products-services/containerlibrary) that includes access to Cloud Pak for Data 3.5.0
- `CPD_STORAGE_CLASS` Provide the storage class to use for Db2
- `MAS_INSTANCE_ID` Provide the MAS instance ID that will be used in any generated MAS configuration files


### Example usage
```bash
export CPD_ENTITLEMENT_KEY=xxx
export CPD_STORAGE_CLASS=ibmc-file-gold-gid
export MAS_INSTANCE_ID=inst1

ansible-playbook playbooks/cp4d/install-fullstack.yml
```

-------------------------------------------------------------------------------

## Install Services: Lite
This playbook will only install CP4D, none of the Cloud Pak's supported services will be enabled allowing you to set these up seperately.

### Required environment variables

- `CPD_VERSION` CP4D version to be installed. Supported versions are `cpd35` (for CP4D 3.5) and `cpd40` (for CP4D 4.0)
- `CPD_ENTITLEMENT_KEY` An [IBM entitlement key](https://myibm.ibm.com/products-services/containerlibrary) that includes access to Cloud Pak for Data 3.5.0
- `CPD_STORAGE_CLASS` Provide the storage class to use for Db2
- `MAS_INSTANCE_ID` Provide the MAS instance ID that will be used in any generated MAS configuration files

### Example Usage
```bash
export CPD_ENTITLEMENT_KEY=xxx
export CPD_STORAGE_CLASS=ibmc-file-gold-gid
export MAS_INSTANCE_ID=inst1

ansible-playbook playbooks/cp4d/install-lite.yml
```

-------------------------------------------------------------------------------

## Install Services: Watson Studio

This playbook will enable **Watson Studio** services in CP4D and enable a number of additional components to expand the base capability of Watson Studio.

- **Watson Machine Learning** As part of Watson Studio, Watson Machine Learning helps data scientists and developers accelerate AI and machine learning deployment.
- **Apache Spark** Apache Spark is a runtime environment configured inside of Watson Studio similar to a Python Runtime environment.  When Spark is enabled from CP4D, you can opt to create a notebook and choose Spark as runtime to expand data modeling capabilities.
- **Watson AI OpenScale**  Watson OpenScale enables tracking AI models in production, validation and test models to mitigate operational risks.

For more information on how Predict and HP Utilities make use of Watson Studio, refer to [Predict/HP Utilities documentation](https://www.ibm.com/docs/en/mhmpmh-and-p-u/8.2.0?topic=started-getting-data-scientists)

!!! info "Application Support"
    - [Predict](https://www.ibm.com/docs/en/mas84/8.4.0?topic=applications-maximo-predict) requires Watson Studio, Machine Learning and Spark; Openscale is an optional dependency
    - [Health & Predict Utilities](https://www.ibm.com/docs/en/mas84/8.4.0?topic=solutions-maximo-health-predict-utilities) requires Watson Studio base capability only


### Required environment variables

- `CPD_VERSION` CP4D version to be installed. Supported versions are `cpd35` (for CP4D 3.5) and `cpd40` (for CP4D 4.0)
- `CPD_ENTITLEMENT_KEY` An [IBM entitlement key](https://myibm.ibm.com/products-services/containerlibrary) that includes access to Cloud Pak for Data 3.5.0
- `CPD_STORAGE_CLASS` Provide the storage class to use for Db2
- `MAS_INSTANCE_ID` Provide the MAS instance ID that will be used in any generated MAS configuration files


### Example usage
```bash
export CPD_ENTITLEMENT_KEY=xxx
export CPD_STORAGE_CLASS=ibmc-file-gold-gid
export MAS_INSTANCE_ID=inst1

ansible-playbook playbooks/cp4d/install-watsonstudio.yml
```
