# aiservice_ds_migration

This role provides a **complete, standalone migration solution** from Open Data Hub (ODH) to Red Hat OpenShift AI (RHOAI) for AI Service DataScienceCluster.

## Overview

The `aiservice_ds_migration` role is **fully self-contained** and performs the complete migration in a single execution:

### Phase 1: ODH Removal
1. Detects if ODH is currently installed
2. Prompts user for confirmation (unless `no_confirm=true`)
3. Scales down the DataScienceCluster kserve component
4. Removes the ODH operator subscription and CSV
5. Deletes the DataScienceCluster and DSCInitialization resources

### Phase 2: RHOAI Installation
6. Installs RHOAI operator and dependencies
7. Creates DSCInitialization and DataScienceCluster
8. Configures KServe components for model deployment

**No additional steps required!** Just run this role and the complete migration happens automatically.

## Features

- **Complete Migration**: Removes ODH AND installs RHOAI in one role execution
- **Automatic Detection**: Detects if ODH is installed and migration is needed
- **Safe Migration**: Preserves model metadata and configurations
- **Single Purpose**: Dedicated migration role

## Role Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `aiservice_instance_id` | AI Service instance identifier (REQUIRED) | `"masdev"` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `aiservice_ns` | AI Service namespace | `"aiservice-{{ aiservice_instance_id }}"` |

## Usage

### Standalone Migration - Fully Automated

This is the **recommended approach** for migration. The role does everything automatically:

```bash
# Set required variable
export AISERVICE_INSTANCE_ID=masdev

# Run the role - it will automatically:
# 1. Detect ODH
# 2. Remove ODH
# 3. Install RHOAI
# 4. Complete!
ansible-playbook ibm.mas_devops.run_role \
  -e role_name=aiservice_ds_migration
```

### Custom Playbook

```yaml
---
- hosts: localhost
  vars:
    aiservice_instance_id: "masdev"
  roles:
    - ibm.mas_devops.aiservice_ds_migration
```

## Migration Process

The role performs the following steps:

1. **Detection**: Checks if ODH and/or RHOAI are installed
2. **Decision**: Determines if migration is needed
3. **Scale Down**: Sets DataScienceCluster kserve to `Removed`
4. **Wait**: Allows pods to terminate gracefully (60s)
5. **Delete ODH**: Removes ODH subscription and CSV
6. **Cleanup**: Deletes DSCInitialization and DataScienceCluster
7. **Complete**: Sets migration flag for downstream roles

## Migration Impact

### Downtime

- **Expected**: 8-16 minutes of model downtime
- **Cause**: Model pods must be recreated by RHOAI

### What's Preserved

- Model metadata in AI Broker MongoDB
- Training data in S3/Minio
- InferenceService custom resources
- Model configurations

### What's Recreated

- InferenceService pods
- Service mesh routes
- GPU allocations

## Examples

### Example 1: Standard Migration

```yaml
---
- hosts: localhost
  vars:
    aiservice_instance_id: "masdev"
  roles:
    - ibm.mas_devops.aiservice_ds_migration
```

## License

EPL-2.0
