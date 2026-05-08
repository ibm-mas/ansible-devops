# suite_manage_kafkaimageprocessor_config

Configure Kafka Image Processor component for MAS Manage Civil Infrastructure.

## Overview

This role provides **basic configuration** for the Kafka Image Processor component which processes images from Kafka topics for Civil Infrastructure use cases. 

**Important:** This role handles only storage and Maximo configuration. The Kafka topic creation and Kafka ConfigMap/Secret management are handled by the **ibm-mas-kafkaimageprocessor operator** using the kafkamodel approach.

### What This Role Does

1. ✅ **Creates PVC** for image storage
2. ✅ **Patches ManageWorkspace CR** with `kafkaimageprocessorpvcname`
3. ✅ **Sets Maximo system properties** for Kafka endpoints

### What This Role Does NOT Do

1. ❌ Does NOT create Kafka ConfigMaps (operator handles this)
2. ❌ Does NOT create Kafka Secrets (operator handles this)
3. ❌ Does NOT create Kafka topics (operator's kafkamodel Job handles this)
4. ❌ Does NOT fetch Kafka configuration (operator handles this)
5. ❌ Does NOT create RBAC resources (not needed with kafkamodel)

## Architecture

The kafkaimageprocessor uses the **kafkamodel approach** from IoT Platform:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. ansible-devops (this role)                              │
│    - Creates PVC                                            │
│    - Patches ManageWorkspace CR                            │
│    - Sets Maximo system properties                         │
└────────────────────┬────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. ManageWorkspace Operator                                 │
│    - Detects kafkaimageprocessorpvcname                     │
│    - Creates Kafkaimageprocessor CR                         │
└────────────────────┬────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Kafkaimageprocessor Operator                             │
│    - Creates Kafka ConfigMaps                               │
│    - Creates Kubernetes Job running kafkaSync.py            │
│    - Job creates 22 topics via Kafka Admin API              │
│    - Deploys kafka-image-processor application              │
└─────────────────────────────────────────────────────────────┘
```

## Required Variables

```yaml
mas_instance_id: "civil"                    # MAS instance ID
mas_workspace_id: "manage"                  # Manage workspace ID
kafkaimageprocessor_storage_class: "ocs-storagecluster-cephfs"  # Storage class for PVC
kafkaimageprocessor_storage_size: "20Gi"    # PVC size
```

## Optional Variables

```yaml
kafkaimageprocessor_pvcname: "manage-kafkaimageprocessor"  # PVC name (default)
```

## Example Playbook

```yaml
- hosts: localhost
  roles:
    - role: suite_manage_kafkaimageprocessor_config
      vars:
        mas_instance_id: "civil"
        mas_workspace_id: "manage"
        kafkaimageprocessor_storage_class: "ocs-storagecluster-cephfs"
        kafkaimageprocessor_storage_size: "20Gi"
```

## Resources Created by This Role

### 1. PersistentVolumeClaim

**Name:** `{{ mas_instance_id }}-{{ mas_workspace_id }}-{{ kafkaimageprocessor_pvcname }}`

**Example:** `civil-manage-manage-kafkaimageprocessor`

**Spec:**
```yaml
accessModes:
  - ReadWriteMany
resources:
  requests:
    storage: "20Gi"
storageClassName: "ocs-storagecluster-cephfs"
```

### 2. ManageWorkspace CR Patch

**Patch Applied:**
```yaml
spec:
  components:
    civil:
      kafkaimageprocessorpvcname: "manage-kafkaimageprocessor"
```

**Effect:** Triggers ManageWorkspace operator to deploy Kafkaimageprocessor CR

### 3. Maximo System Properties

Three system properties are set via Maximo REST API:

| Property | Value | Purpose |
|----------|-------|---------|
| `civil.kafka.ingest.url` | `http://{instance}-{workspace}-kafkaimageprocessor.mas-{instance}-manage.svc:8080/ingest` | Image ingestion endpoint |
| `civil.kafka.validation.url` | `http://{instance}-{workspace}-kafkaimageprocessor.mas-{instance}-manage.svc:8080/validation` | Validation endpoint |
| `civil.kafka.reprocess.url` | `http://{instance}-{workspace}-kafkaimageprocessor.mas-{instance}-manage.svc:8080/reprocess` | Reprocessing endpoint |

## Kafka Configuration (Handled by Operator)

The **ibm-mas-kafkaimageprocessor operator** handles all Kafka-related configuration:

### Operator Creates:

1. **Kafka Configuration ConfigMap** - Connection details for kafkaSync.py
2. **Kafka Topics ConfigMap** - Definitions for 22 topics
3. **Kafka Credentials Secret** - SASL username/password
4. **Kubernetes Job** - Runs kafkaSync.py to create topics via Kafka Admin API
5. **Application Deployment** - kafka-image-processor pods

### Topics Created (by Operator's Job):

22 topics with naming pattern: `mas_{instanceId}_{appId}_{topic-name}`

Example: `mas_civil_manage_folder-ingest`

**Topic Categories:**
- Folder Processing (3 topics)
- Image Processing (4 topics)
- Inference (3 topics)
- Bulk Processing (3 topics)
- Stitching (3 topics)
- Dead Letter Topics (6 topics)

## Kafkamodel Approach

The operator uses the **kafkamodel** approach from IoT Platform:

**Benefits:**
- ✅ No Kubernetes RBAC required for topic creation
- ✅ Works with any Kafka provider (Strimzi, AWS MSK, Confluent, etc.)
- ✅ Topics created via Kafka Admin API (not Kubernetes CRDs)
- ✅ Simpler architecture
- ✅ Faster topic creation

**How It Works:**
1. Operator creates Kubernetes Job
2. Job runs kafkaSync.py (from IoT Platform)
3. kafkaSync.py uses Kafka Admin API to create topics
4. No Strimzi KafkaTopic CRs needed
5. No cross-namespace RBAC needed

## Dependencies

- MAS Core must be installed
- Manage application must be installed
- ManageWorkspace CR must exist
- Storage class must be available in the cluster
- Kafka cluster must be configured (any provider)

## Workflow

1. **Run this role** - Creates PVC, patches workspace, sets properties
2. **ManageWorkspace operator** - Detects patch, creates Kafkaimageprocessor CR
3. **Kafkaimageprocessor operator** - Handles all Kafka setup and topic creation
4. **Application starts** - Begins processing images from Kafka topics

## Troubleshooting

### PVC Not Created

Check storage class exists and supports ReadWriteMany:
```bash
oc get storageclass
```

### ManageWorkspace Not Updated

Check workspace CR:
```bash
oc get manageworkspace -n mas-{instance}-manage
oc describe manageworkspace {workspace-name} -n mas-{instance}-manage
```

### Kafkaimageprocessor Not Deployed

Check if operator created the CR:
```bash
oc get kafkaimageprocessor -n mas-{instance}-manage
```

### Topics Not Created

Check the operator's Job logs:
```bash
oc get jobs -n mas-{instance}-manage | grep topics-setup
oc logs job/{instance}-kafkaimageprocessor-topics-setup -n mas-{instance}-manage
```
