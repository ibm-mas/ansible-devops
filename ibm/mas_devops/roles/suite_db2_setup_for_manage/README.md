# suite_db2_setup_for_manage

This role performs initial setup on Db2 instances for use with the Maximo Manage application. It supports both CP4D version 3.5 and 4.0, and **now supports both Db2uCluster (deprecated) and Db2uInstance (current) custom resources**.

The role will copy a bash script (setupdb.sh) into the Db2 pod and execute it inside the container, performing configuration changes to the database and configuring tablespaces for Maximo Manage. It configures database parameters, creates tablespaces, and applies performance optimizations that the Manage operator cannot yet handle automatically.

## Supported Db2 Custom Resources

- **Db2uCluster** (deprecated, maintained for backward compatibility)
- **Db2uInstance** (current, recommended for new deployments)

The role automatically detects which CR type is deployed and applies the appropriate configuration. No changes to your playbooks are required.

!!! warning "Downtime Risk"
    Setting `enforce_db2_config=true` will restart the Db2 instance, causing downtime. Schedule during maintenance windows or use with newly created instances.

## Role Variables

| Variable | Required | Default |
|----------|----------|---------|
| [`db2_instance_name`](#db2_instance_name) | Yes | None |
| [`db2_namespace`](#db2_namespace) | No | `db2u` |
| [`db2_dbname`](#db2_dbname) | No | `BLUDB` |
| [`db2_config_version`](#db2_config_version) | No | `1.0.0` |
| [`enforce_db2_config`](#enforce_db2_config) | No | `true` |
| [`db2_helm_operator_mode`](#db2_helm_operator_mode) | No | `false` |

### Db2 Connection

#### db2_instance_name

Db2 Warehouse instance name where the Manage database setup will be performed — a valid Db2 instance name (e.g. `db2w-manage`, `db2u-manage`).

- **Required**
- Environment Variable: `DB2_INSTANCE_NAME`
- Default: None

Used to locate the correct Db2 pod. To find the instance name, go to the Db2 namespace and look for pods with `label=engine`; describe the pod and find the `app` label value.

#### db2_namespace

OpenShift namespace where the Db2 instance is deployed — a valid Kubernetes namespace name.

- **Optional**
- Environment Variable: `DB2_NAMESPACE`
- Default: `db2u`

The default `db2u` namespace is used by most Db2 Warehouse deployments; override it if Db2 is deployed in a custom namespace.

#### db2_dbname

Database name within the Db2 instance where the Manage setup will be performed — a valid Db2 database name that must exist before running this role.

- **Optional**
- Environment Variable: `DB2_DBNAME`
- Default: `BLUDB`

`BLUDB` is the default database name for Manage deployments.

### Db2 Configuration

#### db2_config_version

Version of the enhanced Db2 performance parameter set to apply during setup — `1.0.0` is the currently supported version.

- **Optional**
- Environment Variable: `DB2_CONFIG_VERSION`
- Default: `1.0.0`

The parameter set includes optimizations for Manage's specific database access patterns; different versions may have different parameter sets, and future versions may include additional optimizations.

#### enforce_db2_config

Apply the enhanced Db2 parameters with a database restart — `true` or `false`.

- **Optional**
- Environment Variable: `ENFORCE_DB2_CONFIG`
- Default: `true`

A restart is required for the parameters to take effect. Setting to `false` skips the enhanced parameter application, which is not recommended (suboptimal performance).

!!! warning
    Setting this to `true` will restart the Db2 instance, causing downtime for all applications using the database. Schedule during maintenance windows and, for production systems, coordinate with stakeholders. For new instances this is safe, as no applications are using the database yet.

#### db2_helm_operator_mode

Set to `true` when using the new helm-based Db2 operator, which has the archive logs PVC pre-configured — `true` or `false`.

- **Optional**
- Environment Variable: `DB2_HELM_OPERATOR_MODE`
- Default: `false`

## CR Type Detection

The role automatically:

1. Queries for both Db2uCluster and Db2uInstance resources
2. Validates that exactly one CR type exists
3. Applies configuration appropriate for the detected CR type
4. Fails with clear error messages if:
   - No CR is found
   - Both CR types exist (invalid state)
   - CR is not in Ready state

## Example Playbook

### Example 1: With Db2uCluster (Legacy)

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_instance_name: mydb2-cluster
    db2_namespace: db2u
    db2_config_version: "1.0.0"
    enforce_db2_config: true
  roles:
    - ibm.mas_devops.suite_db2_setup_for_manage
```

### Example 2: With Db2uInstance (Current)

```yaml
- hosts: localhost
  any_errors_fatal: true
  vars:
    db2_instance_name: mydb2-instance
    db2_namespace: db2u
    db2_config_version: "1.0.0"
    enforce_db2_config: true
  roles:
    - ibm.mas_devops.suite_db2_setup_for_manage
```

The playbook syntax is identical for both CR types — the role handles the differences automatically.

## Troubleshooting

### Error: "Both Db2uCluster and Db2uInstance resources exist"

This indicates an invalid state. Ensure only one CR type exists:

```bash
oc get db2ucluster -n <namespace>
oc get db2uinstance -n <namespace>
```

Delete the unwanted CR (Db2uInstance is recommended for new deployments).

### Error: "No Db2 instance found"

Verify the instance name and namespace:

```bash
oc get db2ucluster,db2uinstance -n <namespace>
```

### Configuration Not Applied

Check the ConfigMap to see if configuration was already applied:

```bash
oc get configmap <instance-name>-enforce-config -n <namespace> -o yaml
```

## License

EPL-2.0
