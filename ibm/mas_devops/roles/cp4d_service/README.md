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


!!! warning
    The reconcile of many CP4D resources will be marked as Failed multiple times during initial installation, these are **misleading status updates**, the install is just really slow and the operators can not properly handle this.  For example, if you are watching the install of CCS you will see that each **rabbitmq-ha** pod takes 10-15 minutes to start up and it looks like there is a problem because the pod log will just stop at a certain point.  If you see something like this as the last message in the pod log `WAL: ra_log_wal init, open tbls: ra_log_open_mem_tables, closed tbls: ra_log_closed_mem_tables` be assured that there's nothing wrong, it's just there's a long delay between that message and the next (`starting system coordination`) being logged.


### Watson Studio
Subscriptions related to Watson Studio:

- **cpd-platform-operator** on channel `v2.0`
- **ibm-cpd-wsl** on channel `v2.0`
- **ibm-cpd-ccs** on channel `v1.0`
- **ibm-cpd-datarefinery** on channel `v1.0`
- **ibm-cpd-ws-runtimes** on channel `v1.0`

Watson Studio is made up of many moving parts across multiple namespaces.

In the **ibm-common-services** namespace:

- 15 workloads / 12 pods
- 0.126 CPU usage / 1.11 CPU requests / 3.57 CPU limit (11% utilization)
- 773.8 MiB memory usage, 2.27 GiB memory requests / 5.72 GiB memory limit (33% utilization)

```
oc -n ibm-common-services get deployments
NAME                                   READY   UP-TO-DATE   AVAILABLE   AGE
cert-manager-cainjector                1/1     1            1           4h57m
cert-manager-controller                1/1     1            1           4h57m
cert-manager-webhook                   1/1     1            1           4h57m
configmap-watcher                      1/1     1            1           4h57m
ibm-cert-manager-operator              1/1     1            1           4h58m
ibm-common-service-operator            1/1     1            1           5h3m
ibm-common-service-webhook             1/1     1            1           5h2m
ibm-namespace-scope-operator           1/1     1            1           5h3m
ibm-zen-operator                       1/1     1            1           4h58m
meta-api-deploy                        1/1     1            1           4h57m
operand-deployment-lifecycle-manager   1/1     1            1           5h2m
secretshare                            1/1     1            1           5h2m
```

In the **ibm-cpd-operators** namespace:

- 7 workloads / 7 pods
- 0.007 CPU usage / 0.7 CPU requests / 3.75 CPU limit (1% utilization)
- 263.4 MiB memory usage, 1.64 GiB memory requests /6.5 GiB memory limit (15% utilization)

```bash
oc -n ibm-cpd-operators get deployments
NAME                            READY   UP-TO-DATE   AVAILABLE   AGE
cpd-platform-operator-manager   1/1     1            1           5h
ibm-common-service-operator     1/1     1            1           5h
ibm-cpd-ccs-operator            1/1     1            1           3h43m
ibm-cpd-datarefinery-operator   1/1     1            1           134m
ibm-cpd-ws-operator             1/1     1            1           3h45m
ibm-cpd-ws-runtimes-operator    1/1     1            1           118m
ibm-namespace-scope-operator    1/1     1            1           5h
```

In the **ibm-cpd** namespace:

- 51 workloads / 101 pods
- 1.1 CPU usage / 18.72 CPU requests / 86.7 CPU limit (5% utilization)
- 16.46 GiB memory usage, 33.04 GiB memory requests / 175.7 GiB memory limit (50% utilization)

```bash
oc -n ibm-cpd get ccs,ws,datarefinery,notebookruntimes,deployments,sts
NAME                         VERSION   RECONCILED   STATUS      AGE
ccs.ccs.cpd.ibm.com/ccs-cr   4.0.9     4.0.9        Completed   3h42m

NAME                      VERSION   RECONCILED   STATUS      AGE
ws.ws.cpd.ibm.com/ws-cr   4.0.9     4.0.9        Completed   3h45m

NAME                                                        VERSION   STATUS      AGE
datarefinery.datarefinery.cpd.ibm.com/datarefinery-sample   4.0.9     Completed   133m

NAME                                                     VERSION   RECONCILED   STATUS      AGE
notebookruntime.ws.cpd.ibm.com/ibm-cpd-ws-runtime-py39             4.0.9        Completed   116m

NAME                                                         READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/asset-files-api                              1/1     1            1           159m
deployment.apps/ax-cdsx-jupyter-notebooks-converter-deploy   1/1     1            1           111m
deployment.apps/ax-cdsx-notebooks-job-manager-deploy         1/1     1            1           111m
deployment.apps/ax-environments-api-deploy                   1/1     1            1           144m
deployment.apps/ax-environments-ui-deploy                    1/1     1            1           144m
deployment.apps/ax-wdp-notebooks-api-deploy                  1/1     1            1           111m
deployment.apps/ax-ws-notebooks-ui-deploy                    1/1     1            1           111m
deployment.apps/catalog-api                                  2/2     2            2           167m
deployment.apps/dap-dashboards-api                           1/1     1            1           159m
deployment.apps/dataview-api-service                         1/1     1            1           138m
deployment.apps/dc-main                                      1/1     1            1           167m
deployment.apps/event-logger-api                             1/1     1            1           159m
deployment.apps/ibm-0100-model-viewer-prod                   1/1     1            1           110m
deployment.apps/ibm-nginx                                    3/3     3            3           4h37m
deployment.apps/jobs-api                                     1/1     1            1           155m
deployment.apps/jobs-ui                                      1/1     1            1           155m
deployment.apps/ngp-projects-api                             1/1     1            1           159m
deployment.apps/portal-catalog                               1/1     1            1           166m
deployment.apps/portal-common-api                            1/1     1            1           159m
deployment.apps/portal-dashboards                            1/1     1            1           159m
deployment.apps/portal-job-manager                           1/1     1            1           159m
deployment.apps/portal-main                                  1/1     1            1           159m
deployment.apps/portal-ml-dl                                 1/1     1            1           111m
deployment.apps/portal-notifications                         1/1     1            1           159m
deployment.apps/portal-projects                              1/1     1            1           159m
deployment.apps/redis-ha-haproxy                             1/1     1            1           174m
deployment.apps/runtime-assemblies-operator                  1/1     1            1           151m
deployment.apps/runtime-manager-api                          1/1     1            1           147m
deployment.apps/spaces                                       1/1     1            1           142m
deployment.apps/spawner-api                                  1/1     1            1           146m
deployment.apps/usermgmt                                     3/3     3            3           4h39m
deployment.apps/wdp-connect-connection                       1/1     1            1           167m
deployment.apps/wdp-connect-connector                        1/1     1            1           167m
deployment.apps/wdp-connect-flight                           1/1     1            1           167m
deployment.apps/wdp-dataprep                                 1/1     1            1           126m
deployment.apps/wdp-dataview                                 1/1     1            1           138m
deployment.apps/wdp-shaper                                   1/1     1            1           128m
deployment.apps/wkc-search                                   1/1     1            1           167m
deployment.apps/wml-main                                     1/1     1            1           143m
deployment.apps/zen-audit                                    1/1     1            1           4h33m
deployment.apps/zen-core                                     3/3     3            3           4h32m
deployment.apps/zen-core-api                                 3/3     3            3           4h32m
deployment.apps/zen-data-sorcerer                            2/2     2            2           4h25m
deployment.apps/zen-watchdog                                 1/1     1            1           4h25m
deployment.apps/zen-watcher                                  1/1     1            1           4h32m

NAME                                    READY   AGE
statefulset.apps/dsx-influxdb           1/1     4h28m
statefulset.apps/elasticsearch-master   3/3     171m
statefulset.apps/rabbitmq-ha            3/3     3h35m
statefulset.apps/redis-ha-server        3/3     3h1m
statefulset.apps/wdp-couchdb            3/3     3h38m
statefulset.apps/zen-metastoredb        3/3     4h43m
```


### Watson Machine Learning
Subscriptions related to Watson Machine Learning:

- **cpd-platform-operator** on channel `v2.0`
- **ibm-cpd-wml** on channel `v1.1`
- **ibm-cpd-ccs** on channel `v1.0`


Watson Machine Learning is made up of many moving parts across multiple namespaces.

In the **ibm-common-services** namespace:

- 15 workloads / 12 pods
- 0.126 CPU usage / 1.11 CPU requests / 3.57 CPU limit (11% utilization)
- 773.8 MiB memory usage, 2.27 GiB memory requests / 5.72 GiB memory limit (33% utilization)

```bash
oc -n ibm-common-services get deployments
NAME                                   READY   UP-TO-DATE   AVAILABLE   AGE
cert-manager-cainjector                1/1     1            1           4h7m
cert-manager-controller                1/1     1            1           4h7m
cert-manager-webhook                   1/1     1            1           4h7m
configmap-watcher                      1/1     1            1           4h7m
ibm-cert-manager-operator              1/1     1            1           4h8m
ibm-common-service-operator            1/1     1            1           4h14m
ibm-common-service-webhook             1/1     1            1           4h12m
ibm-namespace-scope-operator           1/1     1            1           4h13m
ibm-zen-operator                       1/1     1            1           4h8m
meta-api-deploy                        1/1     1            1           4h8m
operand-deployment-lifecycle-manager   1/1     1            1           4h12m
secretshare                            1/1     1            1           4h12m
```

In the **ibm-cpd-operators** namespace:

- 5 workloads / 5 pods
- 0.011 CPU usage / 0.5 CPU requests / 2.75 CPU limit (1% utilization)
- 177.4 MiB memory usage, 1.14 GiB memory requests / 4.5 GiB memory limit (15% utilization)

```bash
oc -n ibm-cpd-operators get deployments
NAME                            READY   UP-TO-DATE   AVAILABLE   AGE
cpd-platform-operator-manager   1/1     1            1           3h57m
ibm-common-service-operator     1/1     1            1           3h57m
ibm-cpd-ccs-operator            1/1     1            1           150m
ibm-cpd-wml-operator            1/1     1            1           152m
ibm-namespace-scope-operator    1/1     1            1           3h57m
```

In the **ibm-cpd** namespace:

- 50 workloads / 103 pods
- 1.28 CPU usage / 18.07 CPU requests / 86.15 CPU limit (7% utilization)
- 16.96 GiB memory usage, 41.29 GiB memory requests / 184.5 GiB memory limit (41% utilization)

```
oc -n ibm-cpd get ccs,wmlbase,deployments,sts
NAME                         VERSION   RECONCILED   STATUS      AGE
ccs.ccs.cpd.ibm.com/ccs-cr   4.0.9     4.0.9        Completed   149m

NAME                             VERSION   BUILD         STATUS      AGE
wmlbase.wml.cpd.ibm.com/wml-cr   4.0.9     4.0.10-3220   Completed   151m

NAME                                          READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/asset-files-api               1/1     1            1           80m
deployment.apps/ax-environments-api-deploy    1/1     1            1           66m
deployment.apps/ax-environments-ui-deploy     1/1     1            1           66m
deployment.apps/catalog-api                   2/2     2            2           89m
deployment.apps/dap-dashboards-api            1/1     1            1           80m
deployment.apps/dataview-api-service          1/1     1            1           62m
deployment.apps/dc-main                       1/1     1            1           88m
deployment.apps/event-logger-api              1/1     1            1           80m
deployment.apps/ibm-nginx                     3/3     3            3           3h34m
deployment.apps/jobs-api                      1/1     1            1           76m
deployment.apps/jobs-ui                       1/1     1            1           76m
deployment.apps/ngp-projects-api              1/1     1            1           80m
deployment.apps/portal-catalog                1/1     1            1           88m
deployment.apps/portal-common-api             1/1     1            1           80m
deployment.apps/portal-dashboards             1/1     1            1           80m
deployment.apps/portal-job-manager            1/1     1            1           80m
deployment.apps/portal-main                   1/1     1            1           80m
deployment.apps/portal-notifications          1/1     1            1           80m
deployment.apps/portal-projects               1/1     1            1           80m
deployment.apps/redis-ha-haproxy              1/1     1            1           97m
deployment.apps/runtime-assemblies-operator   1/1     1            1           72m
deployment.apps/runtime-manager-api           1/1     1            1           70m
deployment.apps/spaces                        1/1     1            1           64m
deployment.apps/spawner-api                   1/1     1            1           69m
deployment.apps/usermgmt                      3/3     3            3           3h36m
deployment.apps/wdp-connect-connection        1/1     1            1           88m
deployment.apps/wdp-connect-connector         1/1     1            1           88m
deployment.apps/wdp-connect-flight            1/1     1            1           88m
deployment.apps/wdp-dataview                  1/1     1            1           62m
deployment.apps/wkc-search                    1/1     1            1           88m
deployment.apps/wml-deployment-envoy          1/1     1            1           37m
deployment.apps/wml-main                      1/1     1            1           65m
deployment.apps/wml-repositoryv4              1/1     1            1           18m
deployment.apps/wmltraining                   1/1     1            1           13m
deployment.apps/wmltrainingorchestrator       1/1     1            1           8m11s
deployment.apps/zen-audit                     1/1     1            1           3h28m
deployment.apps/zen-core                      3/3     3            3           3h27m
deployment.apps/zen-core-api                  3/3     3            3           3h27m
deployment.apps/zen-data-sorcerer             2/2     2            2           3h20m
deployment.apps/zen-watchdog                  1/1     1            1           3h20m
deployment.apps/zen-watcher                   1/1     1            1           3h27m

NAME                                      READY   AGE
statefulset.apps/dsx-influxdb             1/1     3h23m
statefulset.apps/elasticsearch-master     3/3     94m
statefulset.apps/rabbitmq-ha              3/3     142m
statefulset.apps/redis-ha-server          3/3     106m
statefulset.apps/wdp-couchdb              3/3     145m
statefulset.apps/wml-deployment-agent     1/1     32m
statefulset.apps/wml-deployment-manager   1/1     24m
statefulset.apps/wml-deployments-etcd     3/3     43m
statefulset.apps/zen-metastoredb          3/3     3h40m
```


### Analytics Engine
Subscriptions related to Analytics Engine:

- **cpd-platform-operator** on channel `v2.0`
- **analyticsengine-operator** on channel `stable-v1`

Analytics Engine is made up of many moving parts across multiple namespaces.

In the **ibm-common-services** namespace:

- 15 workloads / 12 pods
- 0.051 CPU usage / 1.11 CPU requests / 3.57 CPU limit (5% utilization)
- 774.7 MiB memory usage, 2.27 GiB memory requests / 5.72 GiB memory limit (33% utilization)

```
oc -n ibm-common-services get deployments
NAME                                   READY   UP-TO-DATE   AVAILABLE   AGE
cert-manager-cainjector                1/1     1            1           126m
cert-manager-controller                1/1     1            1           126m
cert-manager-webhook                   1/1     1            1           126m
configmap-watcher                      1/1     1            1           126m
ibm-cert-manager-operator              1/1     1            1           126m
ibm-common-service-operator            1/1     1            1           131m
ibm-common-service-webhook             1/1     1            1           130m
ibm-namespace-scope-operator           1/1     1            1           131m
ibm-zen-operator                       1/1     1            1           126m
meta-api-deploy                        1/1     1            1           126m
operand-deployment-lifecycle-manager   1/1     1            1           130m
secretshare                            1/1     1            1           130m
```

In the **ibm-cpd-operators** namespace:

- 4 workloads / 4 pods
- 0.003 CPU usage / 0.4 CPU requests / 2 CPU limit (1% utilization)
- 131.5 MiB memory usage, 912 MiB memory requests / 3 GiB memory limit (15% utilization)

```
oc -n ibm-cpd-operators get deployments
NAME                            READY   UP-TO-DATE   AVAILABLE   AGE
cpd-platform-operator-manager   1/1     1            1           128m
ibm-common-service-operator     1/1     1            1           128m
ibm-cpd-ae-operator             1/1     1            1           65m
ibm-namespace-scope-operator    1/1     1            1           128m
```

In the **ibm-cpd** namespace:

- 16 workloads / 60 pods
- 0.449 CPU usage / 8.06 CPU requests / 21.15 CPU limit (5% utilization)
- 3.15 GiB memory usage, 14.31 GiB memory requests / 32.71 GiB memory limit (22% utilization)

```
oc -n ibm-cpd get analyticsengine,deployments,sts
NAME                                                    VERSION   RECONCILED   STATUS      AGE
analyticsengine.ae.cpd.ibm.com/analyticsengine-sample   4.0.9     4.0.9        Completed   66m

NAME                                             READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/ibm-nginx                        3/3     3            3           93m
deployment.apps/spark-hb-control-plane           1/1     1            1           62m
deployment.apps/spark-hb-create-trust-store      1/1     1            1           64m
deployment.apps/spark-hb-deployer-agent          1/1     1            1           62m
deployment.apps/spark-hb-helm-repo               1/1     1            1           62m
deployment.apps/spark-hb-nginx                   1/1     1            1           62m
deployment.apps/spark-hb-register-hb-dataplane   1/1     1            1           55m
deployment.apps/usermgmt                         3/3     3            3           94m
deployment.apps/zen-audit                        1/1     1            1           89m
deployment.apps/zen-core                         3/3     3            3           89m
deployment.apps/zen-core-api                     3/3     3            3           89m
deployment.apps/zen-data-sorcerer                2/2     2            2           83m
deployment.apps/zen-watchdog                     1/1     1            1           83m
deployment.apps/zen-watcher                      1/1     1            1           89m

NAME                               READY   AGE
statefulset.apps/dsx-influxdb      1/1     85m
statefulset.apps/zen-metastoredb   3/3     118m
```


### Watson OpenScale
Subscriptions related to Watson OpenScale (in the **ibm-cpd-operators** namespace):

- **cpd-platform-operator** on channel `v2.0`
- **ibm-cpd-wos** on channel `v1.5`

Analytics Engine is made up of many moving parts across multiple namespaces.

In the **ibm-common-services** namespace:

- 15 workloads / 12 pods
- 0.051 CPU usage / 1.11 CPU requests / 3.57 CPU limit (5% utilization)
- 774.7 MiB memory usage, 2.27 GiB memory requests / 5.72 GiB memory limit (33% utilization)

```
oc -n ibm-common-services get deployments
NAME                                   READY   UP-TO-DATE   AVAILABLE   AGE
cert-manager-cainjector                1/1     1            1           126m
cert-manager-controller                1/1     1            1           126m
cert-manager-webhook                   1/1     1            1           126m
configmap-watcher                      1/1     1            1           126m
ibm-cert-manager-operator              1/1     1            1           126m
ibm-common-service-operator            1/1     1            1           131m
ibm-common-service-webhook             1/1     1            1           130m
ibm-namespace-scope-operator           1/1     1            1           131m
ibm-zen-operator                       1/1     1            1           126m
meta-api-deploy                        1/1     1            1           126m
operand-deployment-lifecycle-manager   1/1     1            1           130m
secretshare                            1/1     1            1           130m
```

In the **ibm-cpd-operators** namespace:

- 4 workloads / 4 pods
- 0.005 CPU usage / 0.4 CPU requests / 2 CPU limit (1% utilization)
- 148.1 MiB memory usage, 912 MiB memory requests / 3 GiB memory limit (16% utilization)

```
oc -n ibm-cpd-operators get deployments
NAME                            READY   UP-TO-DATE   AVAILABLE   AGE
cpd-platform-operator-manager   1/1     1            1           145m
ibm-common-service-operator     1/1     1            1           145m
ibm-cpd-wos-operator            1/1     1            1           76m
ibm-namespace-scope-operator    1/1     1            1           145m
```

In the **ibm-cpd** namespace:

- 32 workloads / 63 pods
- 0.591 CPU usage / 16.76 CPU requests / 31.9 CPU limit (4% utilization)
- 7.67 GiB memory usage, 37.32 GiB memory requests / 97.89 GiB memory limit (20% utilization)

```
oc -n ibm-cpd get woservice,deployments,sts
NAME                                    TYPE      STORAGE              SCALECONFIG   PHASE   RECONCILED   STATUS
woservice.wos.cpd.ibm.com/aiopenscale   service   ibmc-file-gold-gid   small         Ready   4.0.9        Completed

NAME                                                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/aiopenscale-ibm-aios-bias                   1/1     1            1           61m
deployment.apps/aiopenscale-ibm-aios-bkpicombined           1/1     1            1           61m
deployment.apps/aiopenscale-ibm-aios-common-api             1/1     1            1           61m
deployment.apps/aiopenscale-ibm-aios-configuration          1/1     1            1           61m
deployment.apps/aiopenscale-ibm-aios-dashboard              1/1     1            1           60m
deployment.apps/aiopenscale-ibm-aios-datamart               1/1     1            1           60m
deployment.apps/aiopenscale-ibm-aios-drift                  1/1     1            1           60m
deployment.apps/aiopenscale-ibm-aios-explainability         1/1     1            1           60m
deployment.apps/aiopenscale-ibm-aios-fast-path              1/1     1            1           60m
deployment.apps/aiopenscale-ibm-aios-feedback               1/1     1            1           59m
deployment.apps/aiopenscale-ibm-aios-ml-gateway-discovery   1/1     1            1           59m
deployment.apps/aiopenscale-ibm-aios-ml-gateway-service     1/1     1            1           59m
deployment.apps/aiopenscale-ibm-aios-mrm                    1/1     1            1           59m
deployment.apps/aiopenscale-ibm-aios-nginx                  1/1     1            1           58m
deployment.apps/aiopenscale-ibm-aios-notification           1/1     1            1           59m
deployment.apps/aiopenscale-ibm-aios-payload-logging        1/1     1            1           58m
deployment.apps/aiopenscale-ibm-aios-payload-logging-api    1/1     1            1           59m
deployment.apps/aiopenscale-ibm-aios-scheduling             1/1     1            1           58m
deployment.apps/ibm-nginx                                   3/3     3            3           125m
deployment.apps/usermgmt                                    3/3     3            3           127m
deployment.apps/zen-audit                                   1/1     1            1           120m
deployment.apps/zen-core                                    3/3     3            3           120m
deployment.apps/zen-core-api                                3/3     3            3           120m
deployment.apps/zen-data-sorcerer                           2/2     2            2           114m
deployment.apps/zen-watchdog                                1/1     1            1           114m
deployment.apps/zen-watcher                                 1/1     1            1           120m

NAME                                              READY   AGE
statefulset.apps/aiopenscale-ibm-aios-etcd        3/3     62m
statefulset.apps/aiopenscale-ibm-aios-kafka       3/3     62m
statefulset.apps/aiopenscale-ibm-aios-redis       3/3     62m
statefulset.apps/aiopenscale-ibm-aios-zookeeper   3/3     70m
statefulset.apps/dsx-influxdb                     1/1     116m
statefulset.apps/zen-metastoredb                  3/3     130m
```


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

Watson Discovery is made up of many moving parts across multiple namespaces.

In the **ibm-common-services** namespace:

- 13 workloads / 16 pods
- 0.126 CPU usage / 1.11 CPU requests / 3.57 CPU limit (8% utilization)
- 921.9 MiB memory usage, 2.27 GiB memory requests / 5.72 GiB memory limit (40% utilization)

```
oc -n ibm-common-services get deployments
NAME                                            READY   UP-TO-DATE   AVAILABLE   AGE
cert-manager-cainjector                         1/1     1            1           3h9m
cert-manager-controller                         1/1     1            1           3h9m
cert-manager-webhook                            1/1     1            1           3h9m
configmap-watcher                               1/1     1            1           3h9m
ibm-cert-manager-operator                       1/1     1            1           3h10m
ibm-common-service-operator                     1/1     1            1           3h16m
ibm-common-service-webhook                      1/1     1            1           3h14m
ibm-namespace-scope-operator                    1/1     1            1           3h15m
ibm-zen-operator                                1/1     1            1           3h10m
meta-api-deploy                                 1/1     1            1           3h9m
operand-deployment-lifecycle-manager            1/1     1            1           3h14m
postgresql-operator-controller-manager-1-15-0   1/1     1            1           134m
secretshare                                     1/1     1            1           3h14m
```

In the **ibm-cpd-operators** namespace:

- 10 workloads / 10 pods
- 0.984 CPU usage / 1.65 CPU requests / 7.3 CPU limit (60% utilization)
- 671.6 MiB memory usage, 2.56 GiB memory requests / 9.46 GiB memory limit (25% utilization)

```
oc -n ibm-cpd-operators get deployments
NAME                                                   READY   UP-TO-DATE   AVAILABLE   AGE
cpd-platform-operator-manager                          1/1     1            1           3h12m
gateway-operator                                       1/1     1            1           131m
ibm-common-service-operator                            1/1     1            1           3h12m
ibm-elasticsearch-operator-ibm-es-controller-manager   1/1     1            1           131m
ibm-etcd-operator                                      1/1     1            1           131m
ibm-minio-operator                                     1/1     1            1           131m
ibm-model-train-classic-operator                       1/1     1            1           131m
ibm-namespace-scope-operator                           1/1     1            1           3h12m
ibm-rabbitmq-operator                                  1/1     1            1           131m
wd-discovery-operator                                  1/1     1            1           131m
```

In the **ibm-cpd** namespace:

- 49 workloads / 83 pods
- 0.994 CPU usage / 20.06 CPU requests / 112.3 CPU limit (5% utilization)
- 12.2 GiB memory usage, 96.1 GiB memory requests / 195.5 GiB memory limit (12% utilization)

```
oc -n ibm-cpd get watsondiscoveries,deployments,sts
NAME                                          VERSION   READY   READYREASON   UPDATING   UPDATINGREASON   DEPLOYED   VERIFIED   QUIESCE        DATASTOREQUIESCE   AGE
watsondiscovery.discovery.watson.ibm.com/wd   4.0.9     True    Stable        False      Stable           23/23      23/23      NOT_QUIESCED   NOT_QUIESCED       130m

NAME                                                       READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/ibm-nginx                                  3/3     3            3           174m
deployment.apps/usermgmt                                   3/3     3            3           176m
deployment.apps/wd-discovery-cnm-api                       1/1     1            1           39m
deployment.apps/wd-discovery-converter                     1/1     1            1           39m
deployment.apps/wd-discovery-crawler                       1/1     1            1           39m
deployment.apps/wd-discovery-gateway                       1/1     1            1           19m
deployment.apps/wd-discovery-glimpse-builder               1/1     1            1           37m
deployment.apps/wd-discovery-glimpse-query                 1/1     1            1           39m
deployment.apps/wd-discovery-haywire                       1/1     1            1           39m
deployment.apps/wd-discovery-hdp-rm                        1/1     1            1           39m
deployment.apps/wd-discovery-ingestion-api                 1/1     1            1           39m
deployment.apps/wd-discovery-inlet                         1/1     1            1           39m
deployment.apps/wd-discovery-management                    1/1     1            1           39m
deployment.apps/wd-discovery-minerapp                      1/1     1            1           24m
deployment.apps/wd-discovery-orchestrator                  1/1     1            1           39m
deployment.apps/wd-discovery-outlet                        1/1     1            1           39m
deployment.apps/wd-discovery-po-box                        1/1     1            1           122m
deployment.apps/wd-discovery-project-data-prep-agent       1/1     1            1           39m
deployment.apps/wd-discovery-ranker-master                 1/1     1            1           37m
deployment.apps/wd-discovery-ranker-monitor-agent          1/1     1            1           39m
deployment.apps/wd-discovery-ranker-rest                   1/1     1            1           37m
deployment.apps/wd-discovery-rapi                          1/1     1            1           120m
deployment.apps/wd-discovery-rcm                           1/1     1            1           122m
deployment.apps/wd-discovery-serve-ranker                  1/1     1            1           37m
deployment.apps/wd-discovery-stateless-api-model-runtime   1/1     1            1           39m
deployment.apps/wd-discovery-stateless-api-rest-proxy      1/1     1            1           39m
deployment.apps/wd-discovery-support                       0/0     0            0           39m
deployment.apps/wd-discovery-tooling                       1/1     1            1           24m
deployment.apps/wd-discovery-training-agents               1/1     1            1           39m
deployment.apps/wd-discovery-training-crud                 1/1     1            1           39m
deployment.apps/wd-discovery-training-rest                 1/1     1            1           39m
deployment.apps/wd-discovery-watson-gateway-gw-instance    1/1     1            1           15m
deployment.apps/wd-discovery-wd-indexer                    1/1     1            1           122m
deployment.apps/wd-discovery-wksml                         1/1     1            1           39m
deployment.apps/zen-audit                                  1/1     1            1           171m
deployment.apps/zen-core                                   3/3     3            3           171m
deployment.apps/zen-core-api                               3/3     3            3           171m
deployment.apps/zen-data-sorcerer                          2/2     2            2           165m
deployment.apps/zen-watchdog                               1/1     1            1           165m
deployment.apps/zen-watcher                                1/1     1            1           170m

NAME                                                     READY   AGE
statefulset.apps/dsx-influxdb                            1/1     167m
statefulset.apps/wd-discovery-etcd                       3/3     124m
statefulset.apps/wd-discovery-hdp-worker                 2/2     39m
statefulset.apps/wd-discovery-sdu                        1/1     24m
statefulset.apps/wd-ibm-elasticsearch-es-server-client   1/1     121m
statefulset.apps/wd-ibm-elasticsearch-es-server-data     1/1     121m
statefulset.apps/wd-ibm-elasticsearch-es-server-master   1/1     121m
statefulset.apps/wd-minio-discovery                      4/4     125m
statefulset.apps/wd-rabbitmq-discovery                   1/1     125m
statefulset.apps/zen-metastoredb                         3/3     179m
```


Role Variables - Installation
-----------------------------
### cpd_service_name
Name of the service to install, supported values are: `wsl`, `wml`, `wd`, `aiopenscale`, `dods`, and `spark`

- **Required**
- Environment Variable: `CPD_SERVICE_NAME`
- Default Value: None

### cpd_product_version
The product version (also known as operand version) of this service to install.  Currently, due to defects in Cloud Pak for Data the only version that works is the latest (`4.0.9`), but in the future you should be able to set this to any released version of CP4D.

- **Required**
- Environment Variable: `CPD_PRODUCT_VERSION`
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
