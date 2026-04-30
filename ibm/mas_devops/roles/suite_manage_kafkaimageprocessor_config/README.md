# suite_manage_kafkaimageprocessor_config

Configure Kafka Image Processor component for MAS Manage Civil Infrastructure.

## Overview

This role configures the Kafka Image Processor component which processes images from Kafka topics for Civil Infrastructure use cases. It automatically:

1. **Fetches Kafka configuration** from the MAS system-level KafkaCfg CR
2. **Creates Kafka ConfigMap and Secret** for the kafkaimageprocessor service
3. **Configures persistent storage** for image processing
4. **Updates ManageWorkspace CR** with the component configuration

## Automatic Kafka Configuration

The role automatically retrieves Kafka connection details from the MAS instance's KafkaCfg custom resource. This eliminates the need to manually provide Kafka credentials.

### How It Works

1. **Queries KafkaCfg CR**: `{{ mas_instance_id }}-kafka-system` in `mas-{{ mas_instance_id }}-core` namespace
2. **Extracts configuration**:
   - Bootstrap servers from `spec.config.hosts`
   - Credentials secret name from `spec.config.credentials.secretName`
   - SASL mechanism from `spec.config.saslMechanism`
   - Certificates from `spec.certificates`
3. **Retrieves credentials** from the referenced secret
4. **Creates application-specific resources**:
   - ConfigMap: `{{ mas_instance_id }}-kafka-manage`
   - Secret: `{{ mas_instance_id }}-kafka-manage`

### Manual Override

You can override automatic fetching by setting environment variables:

```bash
export KAFKA_BROKERS='["broker1.example.com:9093","broker2.example.com:9093"]'
export KAFKA_USERNAME='myuser'
export KAFKA_PASSWORD='mypassword'
export KAFKA_CERTIFICATES='[{"crt":"-----BEGIN CERTIFICATE-----..."}]'
export KAFKA_SASL_MECHANISM='SCRAM-SHA-512'
```

## Required Variables

```yaml
mas_instance_id: "myinstance"           # MAS instance ID
mas_workspace_id: "myworkspace"         # Manage workspace ID
kafkaimageprocessor_storage_class: "ocs-storagecluster-cephfs"  # Storage class for PVC
kafkaimageprocessor_storage_size: "20Gi"  # PVC size
```

## Optional Variables

```yaml
kafkaimageprocessor_pvcname: "manage-kafkaimageprocessor"  # PVC name (default)
kafkaimageprocessor_storage_mode: "ReadWriteMany"          # Access mode (default)
kafkaimageprocessor_storage_mountpath: "kafkaimageprocessor"  # Mount path (default)
mas_domain: ""  # Auto-detected from Suite CR if not provided

# Kafka configuration (auto-fetched if not provided)
kafka_brokers: ""
kafka_username: ""
kafka_password: ""
kafka_certificates: ""
kafka_saslmechanism: "SCRAM-SHA-512"
```

## Example Playbook

```yaml
- hosts: localhost
  roles:
    - role: suite_manage_kafkaimageprocessor_config
      vars:
        mas_instance_id: "civil"
        mas_workspace_id: "masdev"
        kafkaimageprocessor_storage_class: "ocs-storagecluster-cephfs"
        kafkaimageprocessor_storage_size: "20Gi"
```

## Multi-Application Support

This role is designed to work alongside other MAS applications (like IoT) that also use Kafka:

- **Separate namespaces**: Each application has its own namespace
- **Separate ConfigMaps/Secrets**: Named by application ID (e.g., `civil-kafka-manage`, `civil-kafka-iot`)
- **Separate topic prefixes**: Prevents topic name collisions (e.g., `civil.manage.*`, `civil.iot.*`)
- **Shared Kafka cluster**: All applications use the same underlying Kafka infrastructure

## Resources Created

1. **PersistentVolumeClaim**: `{{ mas_instance_id }}-{{ mas_workspace_id }}-{{ kafkaimageprocessor_pvcname }}`
2. **ConfigMap**: `{{ mas_instance_id }}-kafka-manage` (contains Kafka connection details)
3. **Secret**: `{{ mas_instance_id }}-kafka-manage` (contains Kafka credentials)
4. **ManageWorkspace CR**: Updated with persistent volume configuration

## Dependencies

- MAS Core must be installed with a configured KafkaCfg
- Manage application must be installed
- Storage class must be available in the cluster

## License

EPL-2.0