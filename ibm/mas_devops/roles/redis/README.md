# Redis Role

This Ansible role deploys a highly available Redis cluster with Sentinel and HAProxy for IBM Maximo Application Suite (MAS) Collaborate addon.

## Overview

The role deploys:
- **Redis StatefulSet**: 3 replicas with master-replica replication
- **Redis Sentinel**: High availability monitoring and automatic failover
- **HAProxy**: Load balancer for automatic master detection
- **TLS Support**: Optional encrypted connections using cert-manager
- **Persistent Storage**: Data persistence using PVCs

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         HAProxy Service                      │
│              (Automatic Master Detection)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼───┐   ┌───▼────┐   ┌───▼────┐
   │ Redis  │   │ Redis  │   │ Redis  │
   │ Pod 0  │   │ Pod 1  │   │ Pod 2  │
   │(Master)│◄──┤(Replica)◄──┤(Replica)│
   └────┬───┘   └───┬────┘   └───┬────┘
        │           │            │
   ┌────▼───┐   ┌───▼────┐   ┌───▼────┐
   │Sentinel│   │Sentinel│   │Sentinel│
   └────────┘   └────────┘   └────────┘
```

## Requirements

- OpenShift/Kubernetes cluster
- cert-manager (if TLS is enabled)
- Storage class for persistent volumes
- Ansible 2.9+
- kubernetes.core collection

## Role Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `redis_namespace` | Namespace for Redis deployment | `redis` |
| `redis_instance_name` | Instance identifier | `dev91x` |
| `mas_instance_id` | MAS instance ID | `dev91x` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `redis_replicas` | `3` | Number of Redis replicas |
| `redis_port` | `6379` | Redis port |
| `redis_tls_enabled` | `true` | Enable TLS |
| `redis_tls_port` | `6380` | Redis TLS port |
| `redis_sentinel_enabled` | `true` | Enable Sentinel |
| `redis_sentinel_port` | `26379` | Sentinel port |
| `redis_storage_size` | `10Gi` | PVC storage size |
| `redis_storage_class` | `""` | Storage class name |
| `redis_maxmemory` | `2gb` | Max memory per Redis instance |
| `cluster_domain` | `cluster.local` | Kubernetes cluster domain |

### Resource Limits

| Variable | Default | Description |
|----------|---------|-------------|
| `redis_cpu_request` | `500m` | Redis CPU request |
| `redis_cpu_limit` | `2000m` | Redis CPU limit |
| `redis_memory_request` | `1Gi` | Redis memory request |
| `redis_memory_limit` | `4Gi` | Redis memory limit |
| `haproxy_cpu_request` | `100m` | HAProxy CPU request |
| `haproxy_cpu_limit` | `500m` | HAProxy CPU limit |
| `haproxy_memory_request` | `128Mi` | HAProxy memory request |
| `haproxy_memory_limit` | `512Mi` | HAProxy memory limit |

### Image Configuration

The role uses the latest Redis images (version 2.1.40) with SHA256 digests:

```yaml
redis_image: "cp.icr.io/cp/assist/ema-redis:2.1.40@sha256:a07d618d43dc0d0fe7d476a227e5b27dde6e390bdbdf76ee3056f990367a6633"
haproxy_image: "cp.icr.io/cp/assist/ema-haproxy:2.1.40@sha256:48670439441724a5fadc1a3ccc8f206feae19fbf6977cb78e00d3d1c5674852c"
```

### Output Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `mas_config_dir` | `/tmp` | Directory for output files |
| `rediscfg_name` | `{{ redis_instance_name }}-redis-system` | RedisCfg CR name |
| `rediscfg_namespace` | `mas-{{ mas_instance_id }}-core` | RedisCfg namespace |

## Usage

### Basic Deployment

```yaml
- name: Deploy Redis for MAS Collaborate
  hosts: localhost
  roles:
    - role: redis
      vars:
        redis_namespace: redis
        redis_instance_name: dev91x
        mas_instance_id: dev91x
        redis_action: install
```

### Custom Configuration

```yaml
- name: Deploy Redis with custom settings
  hosts: localhost
  roles:
    - role: redis
      vars:
        redis_namespace: redis
        redis_instance_name: prod
        mas_instance_id: prod
        redis_action: install
        redis_replicas: 5
        redis_storage_size: 50Gi
        redis_storage_class: fast-ssd
        redis_maxmemory: 8gb
        redis_tls_enabled: true
```

### Generate RedisCfg Only

```yaml
- name: Generate RedisCfg configuration
  hosts: localhost
  roles:
    - role: redis
      vars:
        redis_namespace: redis
        redis_instance_name: dev91x
        mas_instance_id: dev91x
        redis_action: generate-config
```

## Actions

The role supports the following actions via the `redis_action` variable:

- **`install`** (default): Deploy complete Redis infrastructure
- **`generate-config`**: Generate RedisCfg CR file only

## Outputs

After successful deployment, the role generates:

1. **RedisCfg CR**: Custom resource for MAS configuration
   - Location: `{{ mas_config_dir }}/rediscfg-{{ redis_instance_name }}.yaml`
   - Apply with: `oc apply -f <file>`

2. **Connection Details**:
   - Master Service: `{{ redis_instance_name }}-redis-master-svc.{{ redis_namespace }}.svc.cluster.local:6379`
   - HAProxy Service: `{{ redis_instance_name }}-haproxy-svc.{{ redis_namespace }}.svc.cluster.local:6379`
   - Credentials Secret: `{{ redis_instance_name }}-redis-credentials`

## Security

### Credentials

Redis password is automatically generated and stored in Kubernetes secret:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ redis_instance_name }}-redis-credentials
  namespace: {{ redis_namespace }}
type: Opaque
data:
  password: <base64-encoded-password>
```

### TLS Certificates

When TLS is enabled, certificates are managed by cert-manager:
- CA certificate
- Server certificate
- Client certificate (if needed)

### Pod Security

All pods run with:
- Non-root user (UID 1000)
- Read-only root filesystem where possible
- Dropped capabilities
- seccomp profile

## Monitoring

### HAProxy Stats

Access HAProxy statistics:
```bash
oc port-forward -n {{ redis_namespace }} svc/{{ redis_instance_name }}-haproxy-svc 8404:8404
# Open http://localhost:8404/stats
```

### Redis Monitoring

Check Redis status:
```bash
# Connect to Redis master
oc exec -n {{ redis_namespace }} {{ redis_instance_name }}-redis-0 -c redis -- redis-cli -a $REDIS_PASSWORD info replication

# Check Sentinel status
oc exec -n {{ redis_namespace }} {{ redis_instance_name }}-redis-0 -c sentinel -- redis-cli -p 26379 sentinel masters
```

## Troubleshooting

### Check Pod Status
```bash
oc get pods -n {{ redis_namespace }}
```

### View Logs
```bash
# Redis logs
oc logs -n {{ redis_namespace }} {{ redis_instance_name }}-redis-0 -c redis

# Sentinel logs
oc logs -n {{ redis_namespace }} {{ redis_instance_name }}-redis-0 -c sentinel

# HAProxy logs
oc logs -n {{ redis_namespace }} deployment/{{ redis_instance_name }}-haproxy
```

### Test Connectivity
```bash
# Test from within cluster
oc run -it --rm redis-test --image=redis:7 --restart=Never -- redis-cli -h {{ redis_instance_name }}-haproxy-svc.{{ redis_namespace }}.svc.cluster.local -a <password> ping
```

### Common Issues

1. **Pods not starting**: Check storage class and PVC creation
2. **Connection refused**: Verify service names and ports
3. **Authentication failed**: Check credentials secret
4. **TLS errors**: Verify cert-manager is installed and certificates are issued

## Dependencies

This role depends on:
- `kubernetes.core` Ansible collection
- OpenShift CLI (`oc`) or kubectl
- cert-manager operator (for TLS)

## License

IBM Proprietary
