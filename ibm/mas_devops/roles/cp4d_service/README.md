cp4d_service
=============

Install a chosen CloudPak for Data service.

Services Supported
------------------
These services can be deployed and configured using this role:

- [Watson Studio](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=services-watson-studio) required by [Predict](https://www.ibm.com/docs/en/mas87/8.7.0?topic=applications-maximo-predict) and [Health & Predict Utilities](https://www.ibm.com/docs/en/mas87/8.7.0?topic=solutions-maximo-health-predict-utilities)
- [Watson Machine Learning](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=services-watson-machine-learning) required by [Predict](https://www.ibm.com/docs/en/mas87/8.7.0?topic=applications-maximo-predict)
- [Analytics Service (Apache Spark)](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=services-analytics) required by [Predict](https://www.ibm.com/docs/en/mas87/8.7.0?topic=applications-maximo-predict)
- [Watson OpenScale](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=services-watson-openscale) an optional dependency for [Predict](https://www.ibm.com/docs/en/mas87/8.7.0?topic=applications-maximo-predict)
- [Watson Discovery](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=services-watson-discovery) required by Assist
- [Decision Optimization](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.0?topic=services-decision-optimization) an optional dependency for [Maximo Scheduler Optimization](https://www.ibm.com/docs/en/mas87/8.7.0?topic=ons-maximo-scheduler-optimization) - Requires Watson Studio and Watson Machine Learning.

!!! info "Application Support"
    For more information on how Predict and HP Utilities make use of Watson Studio, refer to [Predict/HP Utilities documentation](https://www.ibm.com/docs/en/mhmpmh-and-p-u/8.2.0?topic=started-getting-data-scientists)

### Watson Studio
Subscriptions related to Watson Studio (in the **ibm-cpd-operators** namespace):

- **cpd-platform-operator** on channel `v2.0`
- **ibm-cpd-wsl** on channel `v2.0`
- **ibm-cpd-ccs** on channel `v1.0`
- **ibm-cpd-datarefinery** on channel `v1.0`
- **ibm-cpd-ws-runtimes** on channel `v1.0`

The key resources in the installation of Watson Studio involves are listed below, they are all created in the **ibm-cpd** namespace, note that the operators function in a sequential mode so the installation can take a very long time and you will see these resources created over the course of the 3 hour plus installation:

- `ws.ws.cpd.ibm.com/ws-cr` (reconcile of this resource will fail multiple times with the message *"Unable to install CSS prerequisite"* due to timeouts waiting for the CCS resource)
- `ccs.ccs.cpd.ibm.com/ccs-cr` (reconcile of this resource will fail multiple times with the message *"The playbook has failed. See earlier output for exact error"* due to timeouts waiting for various statefulsets that it manages)
- `deployment.apps/redis-ha-haproxy`
- `statefulset.apps/elasticsearch-master`
- `statefulset.apps/redis-ha-server` (can take 15-20 minutes to start up)
- `statefulset.apps/rabbitmq-ha` (can take 30-40 minutes to start up as each pod is started in sequence)
- `statefulset.apps/wdp-couchdb` (can take 5-10 minutes to start up)

!!! note
    If you are watching the install you will see that each **rabbitmq-ha** pod takes 10-15 minutes to start up and it looks like there is a problem because the pod log will just stop at a certain point.  If you see something like this as the last message in the pod log `WAL: ra_log_wal init, open tbls: ra_log_open_mem_tables, closed tbls: ra_log_closed_mem_tables` be assured that there's nothing wrong, it's just there's a long delay between that message and the next (`starting system coordination`) being logged.

Useful debug commands:
- `oc -n ibm-cpd get deployments,sts,pods`
- `oc -n ibm-cpd get ccs,WS,DataRefinery,notebookruntimes`

### Watson Machine Learning
Subscriptions related to Watson Machine Learning (in the **ibm-cpd-operators** namespace):

- **cpd-platform-operator** on channel `v2.0`
- **ibm-cpd-wml** on channel `v1.1`
- **ibm-cpd-ccs** on channel `v1.0`

Assuming you are adding Watson Machine Learning on top of Watson Studio, the key new resources in the installation are listed below, they are all created in the **ibm-cpd** namespace:

- `wmlbase.wml.cpd.ibm.com/wml-cr`
- `deployment.apps/wmltraining`
- `deployment.apps/wmltrainingorchestrator`
- `statefulset.apps/wml-deployments-etcd`
- `statefulset.apps/wml-deployment-agent`
- `statefulset.apps/wml-deployment-manager`

Useful debug commands:
- `oc -n ibm-cpd get deployments,sts,pods`
- `oc -n ibm-cpd get ccs,wmlbase`

### Analytics Engine
Subscriptions related to Analytics Engine (in the **ibm-cpd-operators** namespace):

- **cpd-platform-operator** on channel `v2.0`
- **analyticsengine-operator** on channel `stable-v1`

Assuming you are adding Analytics Engine on top of Watson Studio, the key new resources in the installation are listed below, they are all created in the **ibm-cpd** namespace:

- `analyticsengine.ae.cpd.ibm.com/analyticsengine-sample`
- `deployment.apps/spark-hb-control-plane`

Useful debug commands:
- `oc -n ibm-cpd get deployments,pods`
- `oc -n ibm-cpd get ccs,wmlbase`

### Watson OpenScale
Subscriptions related to Watson OpenScale (in the **ibm-cpd-operators** namespace):

- **cpd-platform-operator** on channel `v2.0`
- **ibm-cpd-wos** on channel `v1.5`

Assuming you are adding Watson OpenScale on top of Watson Studio, the key new resources in the installation are listed below, they are all created in the **ibm-cpd** namespace:

- `woservice.wos.cpd.ibm.com/aiopenscale`
- `statefulset.apps/aiopenscale-ibm-aios-zookeeper`
- `statefulset.apps/aiopenscale-ibm-aios-kafka`
- `statefulset.apps/aiopenscale-ibm-aios-redis`
- `statefulset.apps/aiopenscale-ibm-aios-etcd`

Useful debug commands:
- `oc -n ibm-cpd get deployments,sts,pods`
- `oc -n ibm-cpd get woservice`

### Watson Discovery
Subscriptions related to Watson Discovery (in the **ibm-cpd-operators** namespace):

- **cpd-platform-operator** on channel `v2.0`
- **ibm-watson-discovery-operator** on channel `v4.0`
- **ibm-elasticsearch-operator** on channel `v1.1`
- **ibm-etcd-operator** on channel `v1.0`
- **ibm-minio-operator** on channel `v1.0`
- **ibm-model-train-classic-operator** on channel `v1.0`
- **ibm-rabbitmq-operator** on channel `v1.0`
- **ibm-watson-gateway-operator** on channel `v1.0`

Subscriptions related to Watson Discovery (in the **ibm-common-services** namespace):

- **cloud-native-postgresql** on channel `stable`

The key new resources in the installation are listed below, they are all created in the **ibm-cpd** namespace:

- `woservice.wos.cpd.ibm.com/aiopenscale`
- `statefulset.apps/wd-rabbitmq-discovery`
- `statefulset.apps/wd-minio-discovery`
- `statefulset.apps/wd-discovery-etcd`

Useful debug commands:
- `oc -n ibm-cpd get deployments,sts,pods`
- `oc -n ibm-cpd get watsondiscoveries`

Role Variables - Installation
-----------------------------
### cpd_service_name
Name of the service to install, supported values are: `wsl`, `wml`, `wd`, `aiopenscale`, `dods`, and `spark`

- **Required**
- Environment Variable: `CPD_SERVICE_NAME`
- Default Value: None

### cpd_service_storage_class
This is used to set `spec.storageClass` in all CPD v3.5 services, and many - but not all - CP4D v4.0 services.

- **Required**, unless IBMCloud storage classes are available.
- Environment Variable: `CPD_SERVICE_STORAGE_CLASS`
- Default Value: `ibmc-file-gold-gid` if the storage class is available.

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
- Environment Variable: `CP4D_ADMIN_USERNAME`
- Default Value: `admin`

### cpd_admin_password
The CP4D Admin User password to call CP4D API to provision Discovery Instance. If you didn't change the initial admin password after CP4D install, you don't need to provide it.  The initial admin user password for `admin` will be used.

- Optional
- Environment Variable: `CP4D_ADMIN_PASSWORD`
- Default Value: Looked up from the `admin-user-details` secret in the `cpd_instance_namespace` namespace


Role Variables - Watson Studio
------------------------------
### cpd_wsl_project_id
Stores the CP4D Watson Studio Project ID that can be used to configure HP Utilities application in MAS.  If this property is not set, or the project identified by this ID does not already exist this role will automatically create one Watson Studio project.  **TODO: This needs to be fixed we need to key off the PROJECT_NAME to make this idempotent, user can't be expected to know the project ID upfront!**

- Optional, only supported when `cpd_service_name` = `wsl`
- Environment Variable: `CPD_WSL_PROJECT_ID`
- Default Value: None

### cpd_wsl_project_name
Stores the CP4D Watson Studio Project name that can be used to configure HP Utilities application in MAS.

- Optional, only supported when `cpd_service_name` = `wsl`
- Environment Variable: `CPD_WSL_PROJECT_NAME`
- Default Value: `wsl_default_project`

### cpd_wsl_project_description
Optional - Stores the CP4D Watson Studio Project description that can be used to configure HP Utilities application in MAS.

- Optional, only supported when `cpd_service_name` = `wsl`
- Environment Variable: `CPD_WSL_PROJECT_DESCRIPTION`
- Default Value: `Watson Studio Project for Maximo Application Suite`


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
    cpd_service_storage_class: ibmc-file-gold-gid
    cpd_service_name: wsl
  roles:
    - ibm.mas_devops.cp4d_service

```

License
-------

EPL-2.0
