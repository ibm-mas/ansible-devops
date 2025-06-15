cp4d_service
=============

Install or upgrade a chosen CloudPak for Data service.

Currently supported Cloud Pak for Data release versions supported are:

  - 4.6.0
  - 4.6.3
  - 4.6.4
  - 4.6.6
  - 4.8.0
  - 5.0.0
  - 5.1.0

The role will automatically install the corresponding CPD service operator channel and custom resource version associated to the chosen Cloud Pak for Data release version.

For more information about the specific CPD services channels and versions associated to a particular Cloud Pak for Data release can be found [here](https://github.ibm.com/PrivateCloud/olm-utils/tree/master/ansible-play/config-vars).

Services Supported
------------------
These services can be deployed and configured using this role:

- [Watson Studio](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=services-watson-studio) required by [Predict](https://www.ibm.com/docs/en/mas-cd/mhmpmh-and-p-u/continuous-delivery)
- [Watson Machine Learning](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=services-watson-machine-learning) required by [Predict](https://www.ibm.com/docs/en/mas-cd/mhmpmh-and-p-u/continuous-delivery)
- [Analytics Services (Apache Spark)](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=services-analytics) required by [Predict](https://www.ibm.com/docs/en/mas-cd/mhmpmh-and-p-u/continuous-delivery)
- [Watson OpenScale](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=services-watson-openscale) an optional dependency for [Predict](https://www.ibm.com/docs/en/mas-cd/mhmpmh-and-p-u/continuous-delivery)
- [SPSS Modeler](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=modeler-installing) optional dependency for [Predict](https://www.ibm.com/docs/en/mas-cd/mhmpmh-and-p-u/continuous-delivery)
- [Watson Discovery](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=services-watson-discovery) required by [Assist](https://www.ibm.com/docs/en/mas-cd/maximo-assist) - Not supported with CPD 5.0
- [Cognos Analytics](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=analytics-installing) optional dependency for [Manage application](https://www.ibm.com/docs/en/mas-cd/maximo-manage)

!!! info
    - Install CP4D Services (~30 Minutes - 1 hour for each service)

    All timings are estimates.


Upgrade
------------------
This role also supports seamlessly CPD services minor version upgrades (CPD 4.6.x > CPD 4.8.0, CPD 4.8.0 > CPD 5.0.0 or CPD 5.0.0 > 5.1.0), as well as patch version upgrades (e.g. CPD 4.6.0 -> CPD 4.6.6), with the exception of [Watson Discovery](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=u-upgrading-from-version-46-2).

All you need to do is to define `cpd_product_version` variable to the version you target to upgrade and run this role for a particular CPD service.
It's important that before you upgrade CPD services, the CPD Control Plane/Zen is also upgraded to the same release version.

For more information about IBM Cloud Pak for Data upgrade process, refer to the [CPD official documentation](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=upgrading).

!!! info "Application Support"
    For more information on how Predict and HP Utilities make use of Watson Studio, refer to [Predict/HP Utilities documentation](https://www.ibm.com/docs/en/mas-cd/mhmpmh-and-p-u/continuous-delivery?topic=administering-products)


!!! warning
    The reconcile of many CP4D resources will be marked as Failed multiple times during initial installation, these are **misleading status updates**, the install is just really slow and the operators can not properly handle this.  For example, if you are watching the install of CCS you will see that each **rabbitmq-ha** pod takes 10-15 minutes to start up and it looks like there is a problem because the pod log will just stop at a certain point.  If you see something like this as the last message in the pod log `WAL: ra_log_wal init, open tbls: ra_log_open_mem_tables, closed tbls: ra_log_closed_mem_tables` be assured that there's nothing wrong, it's just there's a long delay between that message and the next (`starting system coordination`) being logged.

  **Note**: Watson Discovery 4.8.x introduces breaking changes that blocks seamless upgrade from 4.6.x. It requires backing up your data, uninstall 4.6.x, install 4.8.x and restoring Watson Discovery data. Thus, this action requires additional steps that are not covered by this automation. For detailed steps about upgrading WD 4.6 -> 4.8, read [Upgrading Watson Discovery from version 4.6 to 4.8](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=u-upgrading-from-version-46-2).

### Watson Studio
Subscriptions related to Watson Studio:

- **cpd-platform-operator**
- **ibm-cpd-wsl**
- **ibm-cpd-ccs**
- **ibm-cpd-datarefinery**
- **ibm-cpd-ws-runtimes**

Watson Studio is made up of many moving parts across multiple namespaces.

In the **ibm-cpd-operators** namespace:

```bash
oc -n ibm-cpd-operators get deployments
NAME                                                   READY   UP-TO-DATE   AVAILABLE   AGE
ibm-cpd-ccs-operator                                   1/1     1            1           83m
ibm-cpd-datarefinery-operator                          1/1     1            1           83m
ibm-cpd-ws-operator                                    1/1     1            1           83m
ibm-cpd-ws-runtimes-operator                           1/1     1            1           83m
ibm-elasticsearch-operator-ibm-es-controller-manager   1/1     1            1           83m
```

In the **ibm-cpd** namespace:

```bash
oc -n ibm-cpd get ccs,ws,datarefinery,notebookruntimes,deployments,sts
NAME                         VERSION   RECONCILED   STATUS      AGE
ccs.ccs.cpd.ibm.com/ccs-cr   9.0.0     9.0.0        Completed   82m

NAME                      VERSION   RECONCILED   STATUS      AGE
ws.ws.cpd.ibm.com/ws-cr   9.0.0     9.0.0        Completed   83m

NAME                                                    VERSION   RECONCILED   STATUS      AGE
datarefinery.datarefinery.cpd.ibm.com/datarefinery-cr   9.0.0     9.0.0        Completed   36m

NAME                                                       NLP MODELS   VERSION   RECONCILED   STATUS      AGE
notebookruntime.ws.cpd.ibm.com/ibm-cpd-ws-runtime-241-py                9.0.0     9.0.0        Completed   22m

NAME                                                         READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/asset-files-api                              1/1     1            1           60m
deployment.apps/ax-cdsx-jupyter-notebooks-converter-deploy   1/1     1            1           15m
deployment.apps/ax-cdsx-notebooks-job-manager-deploy         1/1     1            1           15m
deployment.apps/ax-environments-api-deploy                   1/1     1            1           53m
deployment.apps/ax-environments-ui-deploy                    1/1     1            1           53m
deployment.apps/ax-wdp-notebooks-api-deploy                  1/1     1            1           15m
deployment.apps/ax-ws-notebooks-ui-deploy                    1/1     1            1           15m
deployment.apps/catalog-api                                  2/2     2            2           69m
deployment.apps/dataview-api-service                         1/1     1            1           48m
deployment.apps/dc-main                                      1/1     1            1           65m
deployment.apps/event-logger-api                             1/1     1            1           59m
deployment.apps/ibm-0100-model-viewer-prod                   1/1     1            1           14m
deployment.apps/jobs-api                                     1/1     1            1           49m
deployment.apps/jobs-ui                                      1/1     1            1           49m
deployment.apps/ngp-projects-api                             1/1     1            1           60m
deployment.apps/portal-catalog                               1/1     1            1           65m
deployment.apps/portal-common-api                            1/1     1            1           60m
deployment.apps/portal-job-manager                           1/1     1            1           60m
deployment.apps/portal-main                                  1/1     1            1           60m
deployment.apps/portal-ml-dl                                 1/1     1            1           14m
deployment.apps/portal-notifications                         1/1     1            1           60m
deployment.apps/portal-projects                              1/1     1            1           60m
deployment.apps/redis-ha-haproxy                             1/1     1            1           78m
deployment.apps/runtime-assemblies-operator                  1/1     1            1           59m
deployment.apps/runtime-manager-api                          1/1     1            1           59m
deployment.apps/spaces                                       1/1     1            1           48m
deployment.apps/task-credentials                             1/1     1            1           48m
deployment.apps/wdp-connect-connection                       1/1     1            1           66m
deployment.apps/wdp-connect-connector                        1/1     1            1           66m
deployment.apps/wdp-connect-flight                           1/1     1            1           66m
deployment.apps/wdp-dataprep                                 1/1     1            1           29m
deployment.apps/wdp-dataview                                 1/1     1            1           48m
deployment.apps/wdp-shaper                                   1/1     1            1           29m
deployment.apps/wkc-search                                   1/1     1            1           66m
deployment.apps/wml-main                                     1/1     1            1           48m

NAME                                                         READY   AGE
statefulset.apps/elasticsea-0ac3-ib-6fb9-es-server-esnodes   3/3     74m
statefulset.apps/rabbitmq-ha                                 3/3     79m
statefulset.apps/redis-ha-server                             3/3     79m
statefulset.apps/wdp-couchdb                                 3/3     79m
```

### Watson Machine Learning
Subscriptions related to Watson Machine Learning:

- **cpd-platform-operator**
- **ibm-cpd-wml**
- **ibm-cpd-ccs**

Watson Machine Learning is made up of many moving parts across multiple namespaces.

In the **ibm-cpd-operators** namespace:

```bash
oc -n ibm-cpd-operators get deployments
NAME                                                   READY   UP-TO-DATE   AVAILABLE   AGE
ibm-cpd-ccs-operator                                   1/1     1            1           134m
ibm-cpd-datarefinery-operator                          1/1     1            1           134m
ibm-cpd-wml-operator                                   1/1     1            1           49m
ibm-elasticsearch-operator-ibm-es-controller-manager   1/1     1            1           134m
```

In the **ibm-cpd** namespace:

```bash
oc -n ibm-cpd get ccs,wmlbase,deployments,sts
NAME                         VERSION   RECONCILED   STATUS      AGE
ccs.ccs.cpd.ibm.com/ccs-cr   9.0.0     9.0.0        Completed   133m

NAME                             VERSION   BUILD       STATUS      RECONCILED   AGE
wmlbase.wml.cpd.ibm.com/wml-cr   5.0.0     5.0.0-918   Completed   5.0.0        50m

NAME                                                         READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/wml-deployment-envoy                         1/1     1            1           23m
deployment.apps/wml-deployment-manager                       1/1     1            1           19m
deployment.apps/wml-main                                     1/1     1            1           99m
deployment.apps/wml-repositoryv4                             1/1     1            1           16m
deployment.apps/wmltraining                                  1/1     1            1           15m
deployment.apps/wmltrainingorchestrator                      1/1     1            1           14m

NAME                                                         READY   AGE
statefulset.apps/wml-cpd-etcd                                3/3     26m
statefulset.apps/wml-deployment-agent                        1/1     21m
```

### Analytics Engine
Subscriptions related to Analytics Engine:

- **cpd-platform-operator**
- **analyticsengine-operator**

Analytics Engine is made up of many moving parts across multiple namespaces.

In the **ibm-cpd-operators** namespace:

```bash
oc -n ibm-cpd-operators get deployments
NAME                                                   READY   UP-TO-DATE   AVAILABLE   AGE
ibm-cpd-ae-operator                                    1/1     1            1           31m
```

In the **ibm-cpd** namespace:

```bash
oc -n ibm-cpd get analyticsengine,deployments
NAME                                                    VERSION   RECONCILED   STATUS      AGE
analyticsengine.ae.cpd.ibm.com/analyticsengine-sample   5.0.0     5.0.0        Completed   31m

NAME                                                         READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/spark-hb-br-recovery                         1/1     1            1           11m
deployment.apps/spark-hb-control-plane                       1/1     1            1           19m
deployment.apps/spark-hb-create-trust-store                  1/1     1            1           25m
deployment.apps/spark-hb-deployer-agent                      1/1     1            1           19m
deployment.apps/spark-hb-nginx                               1/1     1            1           19m
deployment.apps/spark-hb-register-hb-dataplane               1/1     1            1           10m
deployment.apps/spark-hb-ui                                  1/1     1            1           19m

```


### Watson OpenScale
Subscriptions related to Watson OpenScale (in the **ibm-cpd-operators** namespace):

- **cpd-platform-operator**
- **ibm-cpd-wos-operator**

Analytics Engine is made up of many moving parts across multiple namespaces.

In the **ibm-cpd-operators** namespace:

```bash
oc -n ibm-cpd-operators get deployments
NAME                                                   READY   UP-TO-DATE   AVAILABLE   AGE
ibm-cpd-wos-operator                                   1/1     1            1           30m
```

In the **ibm-cpd** namespace:


```bash
oc -n ibm-cpd get woservice,deployments,sts
NAME                                                  TYPE      STORAGE   SCALECONFIG   PHASE   RECONCILED   STATUS
woservice.wos.cpd.ibm.com/openscale-defaultinstance   service             small         Ready   5.0.0        Completed

NAME                                                                         READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/openscale-defaultinstance-ibm-aios-bias                      1/1     1            1           21m
deployment.apps/openscale-defaultinstance-ibm-aios-bkpicombined              1/1     1            1           21m
deployment.apps/openscale-defaultinstance-ibm-aios-common-api                1/1     1            1           22m
deployment.apps/openscale-defaultinstance-ibm-aios-configuration             1/1     1            1           22m
deployment.apps/openscale-defaultinstance-ibm-aios-dashboard                 1/1     1            1           21m
deployment.apps/openscale-defaultinstance-ibm-aios-datamart                  1/1     1            1           22m
deployment.apps/openscale-defaultinstance-ibm-aios-drift                     1/1     1            1           21m
deployment.apps/openscale-defaultinstance-ibm-aios-explainability            1/1     1            1           21m
deployment.apps/openscale-defaultinstance-ibm-aios-fast-path                 1/1     1            1           21m
deployment.apps/openscale-defaultinstance-ibm-aios-feedback                  1/1     1            1           21m
deployment.apps/openscale-defaultinstance-ibm-aios-metrics-compute-manager   0/0     0            0           21m
deployment.apps/openscale-defaultinstance-ibm-aios-ml-gateway-discovery      1/1     1            1           22m
deployment.apps/openscale-defaultinstance-ibm-aios-ml-gateway-service        1/1     1            1           22m
deployment.apps/openscale-defaultinstance-ibm-aios-mrm                       1/1     1            1           21m
deployment.apps/openscale-defaultinstance-ibm-aios-nginx                     1/1     1            1           25m
deployment.apps/openscale-defaultinstance-ibm-aios-notification              1/1     1            1           21m
deployment.apps/openscale-defaultinstance-ibm-aios-payload-logging           1/1     1            1           21m
deployment.apps/openscale-defaultinstance-ibm-aios-payload-logging-api       1/1     1            1           22m
deployment.apps/openscale-defaultinstance-ibm-aios-redis                     1/1     1            1           28m
deployment.apps/openscale-defaultinstance-ibm-aios-scheduling                1/1     1            1           21m

NAME                                                         READY   AGE
statefulset.apps/openscale-defaultinstance-ibm-aios-etcd     3/3     27m
statefulset.apps/openscale-defaultinstance-ibm-aios-kafka    3/3     27m

```

### Cognos Analytics
Subscriptions related to Cognos Analytics (in the **ibm-cpd-operators** namespace):

- **cpd-platform-operator**
- **ibm-ca-operator-controller-manager**

Cognos Analytics is made up of many moving parts across multiple namespaces.

In the **ibm-cpd-operators** namespace:

```bash
oc -n ibm-cpd-operators get deployments
NAME                                                   READY   UP-TO-DATE   AVAILABLE   AGE
ibm-ca-operator-controller-manager                     1/1     1            1           19m
```

In the **ibm-cpd** namespace:


```bash
oc -n ibm-cpd get caservice,deployments
NAME                                   AGE
caservice.ca.cpd.ibm.com/ca-addon-cr   19m

NAME                                                                         READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/cognos-analytics-cognos-analytics-addon                      1/1     1            1           9m17s

```

### SPSS
Subscriptions related to SPSS (in the **ibm-cpd-operators** namespace):

- **cpd-platform-operator**
- **ibm-cpd-spss-operator**

SPSS is made up of many moving parts across multiple namespaces.

In the **ibm-cpd-operators** namespace:

```bash
NAME                                                   READY   UP-TO-DATE   AVAILABLE   AGE
ibm-cpd-canvasbase-operator                            1/1     1            1           38m
ibm-cpd-spss-operator                                  1/1     1            1           38m
```

In the **ibm-cpd** namespace:


```bash
oc -n ibm-cpd get spss,deployments
NAME                                       VERSION   STATUS      AGE
spss.spssmodeler.cpd.ibm.com/spssmodeler   9.0.0     Completed   38m

NAME                                                                         READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/canvasbase-flow-api                                          1/1     1            1           35m
deployment.apps/canvasbase-flow-ui                                           1/1     1            1           30m
deployment.apps/spss-modeler-modeler-flow-api                                1/1     1            1           22m

```

Role Variables - Installation
-----------------------------
### cpd_service_name
Name of the service to install, supported values are: `wsl`, `wml`, `wd`, `aiopenscale`, `spark`, `ca` and `spss`

- **Required**
- Environment Variable: `CPD_SERVICE_NAME`
- Default Value: None

### cpd_product_version
The product version (also known as operand version) of this service to install.

- **Required**
- Environment Variable: `CPD_PRODUCT_VERSION`
- Default Value: Defined by the installed MAS catalog version

### cpd_service_storage_class
This is used to set `spec.storageClass` in all CPD services that uses file storage class (read-write-many RWX).

- **Required**, unless IBMCloud storage classes are available.
- Environment Variable: `CPD_SERVICE_STORAGE_CLASS`
- Default Value: Auto determined if default storage classes are provided and available by your cloud provider. i.e `ibmc-file` for IBM Cloud, `efs` for AWS.

### cpd_service_block_storage_class
This is used to set `spec.blockStorageClass` in all CPD services that uses block storage class (read-write-only RWO).

- **Required**, unless IBMCloud storage classes are available.
- Environment Variable: `CPD_SERVICE_BLOCK_STORAGE_CLASS`
- Default Value: Auto determined if default storage classes are provided and available by your cloud provider. i.e `ibmc-block` for IBM Cloud, `gp2` for AWS.

### cpd_instance_namespace
Namespace where the CP4D instance is deployed.

- Optional
- Environment Variable: `CPD_INSTANCE_NAMESPACE`
- Default Value: `ibm-cpd`

### cpd_operator_namespace
Namespace where the CP4D instance is deployed.

- Optional
- Environment Variable: `CPD_OPERATORS_NAMESPACE`
- Default Value: `ibm-cpd-operators`

### cpd_admin_username
The CP4D Admin username to authenticate with CP4D APIs. If you didn't change the initial admin username after installing CP4D then you don't need to provide this.

- Optional
- Environment Variable: `CPD_ADMIN_USERNAME`
- Default Value:
  - `admin` (CPD 4.6)
  - `cpadmin` (CPD 4.8 and newer)

### cpd_admin_password
The CP4D Admin User password to call CP4D API to provision Discovery Instance. If you didn't change the initial admin password after CP4D install, you don't need to provide it.  The initial admin user password for `admin` or `cpdamin` will be used.

- Optional
- Environment Variable: `CPD_ADMIN_PASSWORD`
- Default Value:
    - CPD 4.6: Looked up from the `admin-user-details` secret in the `cpd_instance_namespace` namespace
    - CPD 4.8 and newer: Looked up from the `ibm-iam-bindinfo-platform-auth-idp-credentials` secret in the `cpd_instance_namespace` namespace

### cpd_service_scale_config
Adjust and scale the resources for your Cloud Pak for Data services to increase processing capacity.
For more information, refer to [Managing resources](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.6.x?topic=services-manually-scaling) in IBM Cloud Pak for Data documentation.

- Optional
- Environment Variable: `CPD_SERVICE_SCALE_CONFIG`
- Default Value: `small`

Role Variables - Watson Studio
------------------------------
### cpd_wsl_project_name
Stores the CP4D Watson Studio Project name that can be used to configure HP Utilities application in MAS.

- Optional, only supported when `cpd_service_name` = `wsl`
- Environment Variable: `CPD_WSL_PROJECT_NAME`
- Default Value: `wsl-mas-${mas_instance_id}-hputilities`

### cpd_wsl_project_description
Optional - Stores the CP4D Watson Studio Project description that can be used to configure HP Utilities application in MAS.

- Optional, only supported when `cpd_service_name` = `wsl`
- Environment Variable: `CPD_WSL_PROJECT_DESCRIPTION`
- Default Value: `Watson Studio Project for Maximo Application Suite`


Role Variables - Watson Discovery
------------------------------
### cpd_wd_instance_name
Stores the name of the CP4D Watson Discovery Instance that can be used to configure Assist application in MAS.

- Optional, only supported when `cpd_service_name` = `wd`
- Environment Variable: `CPD_WD_INSTANCE_NAME`
- Default Value: `wd-mas-${mas_instance_id}-assist`

### cpd_wd_deployment_type
Defines the CP4D Watson Discovery deployment type:

- `Starter`: One replica pod for each wd service/component, uses fewer resources in your cluster.
- `Production`: Multiple replica pods for each Watson Discovery service/component, recommended for production deployments to increase workload capacity however consumes more cluster resources. 

- Optional
- Environment Variable: `CPD_WD_DEPLOYMENT_TYPE`
- Default Value: `Starter`

Note: Deployment type cannot be changed in the future neither while upgrading the service. If you need to change the deployment type, you must uninstall Watson Discovery and reinstall with the desired deployment type. More information, see [Upgrading Watson Discovery](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.5.x?topic=u-upgrading-from-version-40-1).

Role Variables - MAS Configuration Generation
---------------------------------------------
### mas_instance_id
The instance ID of Maximo Application Suite that a generated configuration will target.  If this or `mas_config_dir` are not set then the role will not generate a resource template.

- Optional, only supported when `cpd_service_name` = `wsl`
- Environment Variable: `MAS_INSTANCE_ID`
- Default Value: None

### mas_config_dir
Local directory to save the generated resource definition.  This can be used to manually configure a MAS instance, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` are not set then the role will not generate a resource template.

- Optional, only supported when `cpd_service_name` = `wsl`
- Environment Variable: `MAS_CONFIG_DIR`
- Default Value: None


Example Playbook
----------------

```yaml
---
- hosts: localhost
  any_errors_fatal: true
  vars:
    cpd_product_version: 5.0.0
    cpd_service_storage_class: ibmc-file-gold-gid
    cpd_service_name: wsl
  roles:
    - ibm.mas_devops.cp4d_service

```

License
-------

EPL-2.0
