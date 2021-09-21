grafana
==========

This role provides support to install Gradana Operator and configure OpenShift to extend its default monitoring to user defined metrics. Grafana Operator then will have Prometheus set as its data source and will be configured to scan all the namespaces looking for user defined Grafana Dashboards to be displayed in its UI. Follow all the steps performed by `grafana` role:

**1. Create a cluster monitoring config map**

Enable OpenShift monitoring for user-defined projects. When this config map is created and configured, prometheus and thanos workload will be deployed in `openshift-user-workload-monitoring` project.

> Reference:
> - https://docs.openshift.com/container-platform/4.6/monitoring/enabling-monitoring-for-user-defined-projects.html#enabling-monitoring-for-user-defined-projects_enabling-monitoring-for-user-defined-projects


**2. Install Grafana Operator**

Create Grafana Operator subscription. It is created under `openshift-user-workload-monitoring` project and, by default, starting CSV is `grafana-operator.v3.10.3`

**3. Patch operator with '--scan-all' argument**

Once created by the Subscription, CSV must be configured to scann the other projects, otherwise Grafana will not consider Grafana Dashboards outside of `openshift-user-workload-monitoring`.

> Reference:
> - https://github.com/ibm-watson-iot/iot-docs/tree/master/monitoring#red-hat-grafana-operator

**4. Create ClusterRole and ClusterRoleBinding**

Once `scan-all` argument is configured in CSV, we must deploy a ClusterRole and a ClusterRoleBinding to grant view access to Grafana ServiceAccount

> Reference:
> - https://github.com/grafana-operator/grafana-operator/tree/master/deploy/cluster_roles#grant-grafana-instance-rbac-to-grafanadashboard-definitions-in-other-projectsnamespaces

**5. Install Grafana Operand**

Create an instance of `Grafana` Operand, defining its CR. This is where `grafana_user` and `grafana_password` are set. They will be credentials used to authenticate into Grafana portal.

**6. Install GrafanaDataSource Operand**

Create an instance of `GrafanaDataSource` Operand, defining its CR. This is where metrics' data source is set. By default the data source is Prometheus, and the service used to query metrics is Thanos, defined by `grafana_datasource_url`

> Reference: 
> - Obtaining Bearer Token to connect to DataSource: [here](https://github.com/ibm-watson-iot/iot-docs/tree/master/monitoring#grafana-datasource)
> - Using Thanos as Grafana DataSource (1): [here](https://docs.openshift.com/container-platform/4.6/monitoring/enabling-monitoring-for-user-defined-projects.html#accessing-metrics-from-outside-cluster_enabling-monitoring-for-user-defined-projects)
> - Using Thanos as Grafana DataSource (2): [here](https://github.com/OpenLiberty/open-liberty-operator/issues/190#issuecomment-683427911)


Role Variables
--------------

### Required

- `grafana_user` name of the user to authenticate in Grafana portal
- `grafana_password` password of the user to authenticate in Grafana portal

### Optional (have default values)

- `grafana_storage_class` storage class used to claim a Persisent Volume for GrafanaDataSource. Set as `ibmc-file-gold-gid` by default, which can be used in ROKS clusters. Use `rook-ceph-block-internal` for Fyre clusters.
- `grafana_storage_size` size of the storage claimed. Set as `10Gi` by default
- `grafana_starting_csv` correspondend to the `startingCSV` set for Gratana Operator subscription. Set as `grafana-operator.v3.10.3` by default.
- `grafana_datasource_url` data source hostname configured inside Grafana Portal. Set as Thanos Querier's URL `https://thanos-querier.openshift-monitoring.svc:9091` by default


Example Playbook
----------------

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    grafana_user: "{{ lookup('env', 'GRAFANA_USER') }}"
    grafana_password: "{{ lookup('env', 'GRAFANA_PASSWORD') }}"
    grafana_storage_class: "{{ lookup('env', 'GRAFANA_STORAGE_CLASS') }}"
    grafana_storage_size: "{{ lookup('env', 'GRAFANA_STORAGE_SIZE') }}"
    grafana_starting_csv: "{{ lookup('env', 'GRAFANA_STARTING_CSV') }}"
    grafana_datasource_url: "{{ lookup('env', 'GRAFANA_DATASOURCE_URL') }}"
  roles:
    - ibm.mas_devops.grafana
```

License
-------

EPL-2.0