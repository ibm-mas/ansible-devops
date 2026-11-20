# cp4d_service

Install or upgrade a chosen Cloud Pak for Data service. Currently supported Cloud Pak for Data release versions are:

- 5.2.0 (services installed via OLM)
- 5.3.1 (services installed via Helm)
- 5.4.0 (services installed via Helm)

The role automatically installs the CPD service operator channel and custom resource version associated with the chosen Cloud Pak for Data release version. For more information about the specific CPD service channels and versions associated with a particular Cloud Pak for Data release, refer to the [olm-utils configuration](https://github.ibm.com/PrivateCloud/olm-utils/tree/master/ansible-play/config-vars).

!!! warning "Maximo tailored installation"
    This role only installs the CPD services that Maximo Application Suite depends on, configured in the specific way that the Maximo team use internally.  It does not support further post-install configuration of these services beyond the configuration supported by the role, and it does not support installing or configuring CPD services in any other way.

    Customers who need CPD services or configuration that this role does not provide can choose to install and manage Cloud Pak for Data (including its services) themselves; the MAS applications will work against any correctly configured CPD instance.  When installing and managing CPD yourself, you are responsible for the CPD lifecycle (installation, upgrades, and any configuration you apply).

## Services Supported

These services can be deployed and configured using this role:

- [Watson Studio](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=services-watson-studio) required by [Predict](https://www.ibm.com/docs/en/mas-cd/mhmpmh-and-p-u/continuous-delivery)
- [Watson Machine Learning](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=services-watson-machine-learning) required by [Predict](https://www.ibm.com/docs/en/mas-cd/mhmpmh-and-p-u/continuous-delivery)
- [Analytics Services (Apache Spark)](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=services-analytics) required by [Predict](https://www.ibm.com/docs/en/mas-cd/mhmpmh-and-p-u/continuous-delivery)

!!! info "Application Support"
    For more information on how Predict and HP Utilities make use of Watson Studio, refer to the [Predict/HP Utilities documentation](https://www.ibm.com/docs/en/mas-cd/mhmpmh-and-p-u/continuous-delivery?topic=administering-products).

## Upgrade

This role also supports seamless CPD service minor version upgrades, as well as patch version upgrades.  All you need to do is define `cpd_product_version` to the version you want to upgrade to, and run this role for the particular CPD service.  It's important that before you upgrade CPD services, the CPD Control Plane/Zen is also upgraded to the same release version.

For more information about the IBM Cloud Pak for Data upgrade process, refer to the [CPD official documentation](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.8.x?topic=upgrading).

!!! warning
    The reconcile of many CP4D resources will be marked as Failed multiple times during initial installation, these are **misleading status updates**, the install is just really slow and the operators can not properly handle this.  For example, if you are watching the install of CCS you will see that each **rabbitmq-ha** pod takes 10-15 minutes to start up and it looks like there is a problem because the pod log will just stop at a certain point.  If you see something like this as the last message in the pod log `WAL: ra_log_wal init, open tbls: ra_log_open_mem_tables, closed tbls: ra_log_closed_mem_tables` be assured that there's nothing wrong, it's just there's a long delay between that message and the next (`starting system coordination`) being logged.

## Service Details

Each service is made up of many moving parts across multiple namespaces — the subscriptions listed for each service are installed by the role, and the `oc get` output below shows what a healthy installation looks like.

### Watson Studio

Subscriptions related to Watson Studio:

- **cpd-platform-operator**
- **ibm-cpd-wsl**
- **ibm-cpd-ccs**
- **ibm-cpd-datarefinery**
- **ibm-cpd-ws-runtimes**

!!! note "Search Engine Dependency"
    On CPD 5.2.0 Watson Studio uses the **OpenSearch** operator (`ibm-opensearch-operator`).

In the **ibm-cpd-operators** namespace:

**For CPD 5.2.0:**

```bash
oc -n ibm-cpd-operators get deployments
NAME                                                   READY   UP-TO-DATE   AVAILABLE   AGE
ibm-cpd-ccs-operator                                   1/1     1            1           83m
ibm-cpd-datarefinery-operator                          1/1     1            1           83m
ibm-cpd-ws-operator                                    1/1     1            1           83m
ibm-cpd-ws-runtimes-operator                           1/1     1            1           83m
ibm-opensearch-operator-controller-manager             1/1     1            1           83m
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

!!! note "Search Engine Dependency"
    On CPD 5.2.0 Watson Machine Learning uses the **OpenSearch** operator (`ibm-opensearch-operator`).

In the **ibm-cpd-operators** namespace:

**For CPD 5.2.0:**

```bash
oc -n ibm-cpd-operators get deployments
NAME                                                   READY   UP-TO-DATE   AVAILABLE   AGE
ibm-cpd-ccs-operator                                   1/1     1            1           134m
ibm-cpd-datarefinery-operator                          1/1     1            1           134m
ibm-cpd-wml-operator                                   1/1     1            1           49m
ibm-opensearch-operator-controller-manager             1/1     1            1           134m
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

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`cpd_service_name`](#cpd_service_name) | Yes | None |
| [`cpd_product_version`](#cpd_product_version) | Yes | Defined by the installed MAS catalog version |
| [`cpd_service_storage_class`](#cpd_service_storage_class) | Conditional | Auto-detected |
| [`cpd_service_block_storage_class`](#cpd_service_block_storage_class) | Conditional | Auto-detected |
| [`cpd_instance_namespace`](#cpd_instance_namespace) | No | `ibm-cpd` |
| [`cpd_operator_namespace`](#cpd_operator_namespace) | No | `ibm-cpd-operators` |
| [`cpd_admin_username`](#cpd_admin_username) | No | `cpadmin` |
| [`cpd_admin_password`](#cpd_admin_password) | No | Secret lookup |
| [`cpd_service_scale_config`](#cpd_service_scale_config) | No | `small` |
| [`cpd_wsl_project_name`](#cpd_wsl_project_name) | No | `wsl-mas-${mas_instance_id}-hputilities` |
| [`cpd_wsl_project_description`](#cpd_wsl_project_description) | No | `Watson Studio Project for Maximo Application Suite` |
| [`mas_instance_id`](#mas_instance_id) | No | None |
| [`mas_config_dir`](#mas_config_dir) | No | None |
| [`olm_approval_mode`](#olm_approval_mode) | No | `Automatic` |
| [`olm_approval_timeout`](#olm_approval_timeout) | No | `7200` |

The storage class variables are resolved in this order: explicit variable → storage classes already in use by the existing service CR → storage classes already in use by the existing platform `Ibmcpd` CR in `cpd_instance_namespace` → cluster auto-detection. They are only required when no source yields a value. When updating or upgrading an existing CP4D service the same storage classes are read back from the existing CRs, so these variables do not need to be re-provided; the Watson Studio project and MAS configuration generation variables only apply when `cpd_service_name` is `wsl`.

### OLM Install Plan Approval

#### olm_approval_mode

- **Optional**
- Environment Variable: `OLM_APPROVAL_MODE`
- Default: `Automatic`

When set to `Manual`, the subscriptions this role creates use manual install plan approval: the role pauses with instructions whenever an install plan is waiting for approval, and never approves it automatically. See [OLM Manual Install Plan Approvals](https://ibm-mas.github.io/ansible-devops/olm-manual-approvals/) for the full details.

#### olm_approval_timeout

- **Optional**
- Environment Variable: `OLM_APPROVAL_TIMEOUT`
- Default: `7200`

Seconds to wait for each individual install plan approval before the role fails (2 hours by default).

### Service Installation

#### cpd_service_name

Name of the CPD service to install — valid values are `wsl` (Watson Studio), `wml` (Watson Machine Learning), and `spark` (Analytics Engine powered by Apache Spark).

- **Required**
- Environment Variable: `CPD_SERVICE_NAME`
- Default: None

#### cpd_product_version

The Cloud Pak for Data release version (also known as the operand version) of the service to install — valid values are `5.2.0`, `5.3.1`, and `5.4.0`.

- **Required**
- Environment Variable: `CPD_PRODUCT_VERSION`
- Default: Defined by the installed MAS catalog version

The role automatically selects the operator channel and custom resource version associated with this release version. When upgrading, the CPD Control Plane/Zen must already be upgraded to the same release version.

#### cpd_service_storage_class

Storage class used to set `spec.storageClass` in all CPD services that use file storage (read-write-many, RWX).

- **Required** when the cluster does not provide a detectable default storage class
- Environment Variable: `CPD_SERVICE_STORAGE_CLASS`
- Default: Read back from the existing service CR (`spec.storageClass`, falling back to `spec.fileStorageClass`), then the existing platform `Ibmcpd` CR, then auto-detected from the cluster's default storage classes — for example `ibmc-file` on IBM Cloud or `efs` on AWS

#### cpd_service_block_storage_class

Storage class used to set `spec.blockStorageClass` in all CPD services that use block storage (read-write-once, RWO).

- **Required** when the cluster does not provide a detectable default storage class
- Environment Variable: `CPD_SERVICE_BLOCK_STORAGE_CLASS`
- Default: Read back from the existing service CR (`spec.blockStorageClass`), then the existing platform `Ibmcpd` CR, then auto-detected from the cluster's default storage classes — for example `ibmc-block` on IBM Cloud or `gp2` on AWS

#### cpd_instance_namespace

Namespace where the CP4D instance is deployed.

- **Optional**
- Environment Variable: `CPD_INSTANCE_NAMESPACE`
- Default: `ibm-cpd`

#### cpd_operator_namespace

Namespace where the CP4D operators are deployed.

- **Optional**
- Environment Variable: `CPD_OPERATORS_NAMESPACE`
- Default: `ibm-cpd-operators`

#### cpd_admin_username

The CP4D admin username used to authenticate with the CP4D APIs.

- **Optional**
- Environment Variable: `CPD_ADMIN_USERNAME`
- Default: `cpadmin`

Only needed if you changed the initial admin username after installing CP4D.

#### cpd_admin_password

The CP4D admin password used to call the CP4D APIs (for example, to provision the Watson Studio project).

- **Optional**
- Environment Variable: `CPD_ADMIN_PASSWORD`
- Default: Looked up from the `ibm-iam-bindinfo-platform-auth-idp-credentials` secret in the `cpd_instance_namespace` namespace

Only needed if you changed the initial admin password after the CP4D install; otherwise the initial admin password for `admin` or `cpadmin` is used.

#### cpd_service_scale_config

Adjusts and scales the resources allocated to your Cloud Pak for Data services to increase processing capacity. For more information, refer to [Managing resources](https://www.ibm.com/docs/en/cloud-paks/cp-data/4.6.x?topic=services-manually-scaling) in the IBM Cloud Pak for Data documentation.

- **Optional**
- Environment Variable: `CPD_SERVICE_SCALE_CONFIG`
- Default: `small`

### Watson Studio Project

#### cpd_wsl_project_name

Name of the CP4D Watson Studio project that can be used to configure the HP Utilities application in MAS.

- **Optional**, only supported when `cpd_service_name` is `wsl`
- Environment Variable: `CPD_WSL_PROJECT_NAME`
- Default: `wsl-mas-${mas_instance_id}-hputilities`

#### cpd_wsl_project_description

Description of the CP4D Watson Studio project that can be used to configure the HP Utilities application in MAS.

- **Optional**, only supported when `cpd_service_name` is `wsl`
- Environment Variable: `CPD_WSL_PROJECT_DESCRIPTION`
- Default: `Watson Studio Project for Maximo Application Suite`

### MAS Configuration Generation

#### mas_instance_id

The instance ID of the Maximo Application Suite instance that the generated configuration will target. If this or `mas_config_dir` is not set, the role will not generate a resource template.

- **Optional**, only supported when `cpd_service_name` is `wsl`
- Environment Variable: `MAS_INSTANCE_ID`
- Default: None

#### mas_config_dir

Local directory to save the generated resource definition. This can be used to manually configure a MAS instance, or used as an input to the [suite_config](suite_config.md) role. If this or `mas_instance_id` is not set, the role will not generate a resource template.

- **Optional**, only supported when `cpd_service_name` is `wsl`
- Environment Variable: `MAS_CONFIG_DIR`
- Default: None

## Example Playbook

### Install Watson Studio on CPD 5.2.0

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    cpd_product_version: 5.2.0
    cpd_service_storage_class: ibmc-file-gold-gid
    cpd_service_name: wsl
  roles:
    - ibm.mas_devops.cp4d_service
```

## License

EPL-2.0
