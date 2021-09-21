# Monitoring Playbooks

## Install Grafana

### Required environment variables

- `GRAFANA_USER` user name to be registered for authentication in Grafana portal
- `GRAFANA_PASSWORD` user password to be registered for authentication in Grafana portal

### Optional environment variables
- `GRAFANA_STORAGE_CLASS` storage class of GrafanaDataSource, this will default to `ibmc-file-gold-gid`
- `GRAFANA_STORAGE_SIZE` size of GrafanaDataSource, this will default to `10Gi`
- `GRAFANA_STARTING_CSV` subscription starting CSV (operator version), this will default to `grafana-operator.v3.10.3`
- `GRAFANA_DATASOURCE_URL` url of grafana data source, this will default to Thanos Querier (Prometheus) internal service: `https://thanos-querier.openshift-monitoring.svc:9091`

### Example usage
Grafana 3.10.3 will be installed having Thanos Querier (Prometheus) as its metrics data source, which will live in a file storage of 10Gi; it will also scan all the projects in the cluster looking for user defined Grafana Dashboards; credentials `admin` and `password` will be used toauthenticate in Grafana Portal

```bash
export GRAFANA_USER=admin
export GRAFANA_PASSWORD=password

ansible-playbook playbooks/monitoring/install-grafana.yml
```

!!! note
    See [grafana role](../roles/grafana.md) for more details