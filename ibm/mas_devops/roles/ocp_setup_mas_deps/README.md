ocp_setup_mas_deps
==================

This role provides support to install operators that are required by MAS to work. The role will deploy Service Binding Operator in all namespaces and Cert Manager in the cert-manager namespace.  The role declares a dependency on `ocp_verify` to ensure that the RedHat Operator Catalog is installed and ready before we try to install the Service Binding Operator from that catalog.
In addition, this role updates cluster's internal image registry settings to increase storage to 400GB (needed only for ROKS Cluster to install full stack of services in CP4D) and to configure custom storage for Prometheus monitoring service.


Role Variables
--------------

- `sbo_channel` Catalog channel used to obtain the Service Binding Operator.
- `sbo_startingcsv` Starting version for the Service Binding Operator subscription.
- `sbo_plan_approval` Update strategy for the Service Binding Operator subscription.
- `prometheus_retention` The maximum period of time to retain data for metrics in Prometheus
- `prometheus_storage_class` The storage class used to provision the persistent volume for Prometheus metrics data
- `prometheus_storage_size` The size of the Prometheus persistent volume used to store metrics data
- `alertmgr_storage_size` The size of the Prometheus Alert Manager persistent volume

Example Playbook
----------------

```yaml
- hosts: localhost
  vars:
    sbo_channel: "{{ lookup('env', 'SBO_CHANNEL') | default('preview', true) }}"
    sbo_startingcsv: "{{ lookup('env', 'SBO_STARTINGCSV') | default('service-binding-operator.v0.8.0', true) }}"
    sbo_plan_approval: "{{ lookup('env', 'SBO_PLAN_APPROVAL') | default('Manual', true) }}"
    prometheus_retention: "{{ lookup('env', 'PROMETHEUS_RETENTION') | default('15d', true) }}"
    prometheus_storage_class: "{{ lookup('env', 'PROMETHEUS_STORAGE_CLASS') | default('ibmc-block-gold', true) }}"
    prometheus_storage_size: "{{ lookup('env', 'PROMETHEUS_STORAGE_SIZE') | default('300Gi', true) }}"
    alertmgr_storage_size: "{{ lookup('env', 'ALERTMGR_STORAGE_SIZE') | default('20Gi', true) }}"
  roles:
    - ibm.mas_devops.ocp_setup_mas_deps
```
License
-------

EPL-2.0
