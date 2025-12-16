# Backup Architecture Diagrams

## In-Cluster DB2 Backup to S3 (Direct Upload)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         OpenShift/Kubernetes Cluster                     │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        DB2 Namespace (db2u)                       │   │
│  │                                                                    │   │
│  │  ┌────────────────────────────────────────────────────────────┐  │   │
│  │  │                    DB2 Pod (db2u-manage-0)                  │  │   │
│  │  │                                                              │  │   │
│  │  │  ┌──────────────┐         ┌─────────────────────────────┐  │  │   │
│  │  │  │              │         │                             │  │  │   │
│  │  │  │  DB2 Engine  │────────▶│  Backup PVC (/mnt/backup)  │  │  │   │
│  │  │  │              │  backup │                             │  │  │   │
│  │  │  └──────────────┘         │  ┌───────────────────────┐ │  │  │   │
│  │  │                           │  │ db2backup/            │ │  │  │   │
│  │  │                           │  │ - BLUDB.0.db2inst1... │ │  │  │   │
│  │  │                           │  │ - keystore.p12        │ │  │  │   │
│  │  │                           │  │ - master_key_label.kdb│ │  │  │   │
│  │  │                           │  └───────────────────────┘ │  │  │   │
│  │  │                           │           │                 │  │  │   │
│  │  │                           │           │ tar.gz          │  │  │   │
│  │  │                           │           ▼                 │  │  │   │
│  │  │  ┌──────────────┐         │  ┌───────────────────────┐ │  │  │   │
│  │  │  │              │         │  │ backup-20240621.tar.gz│ │  │  │   │
│  │  │  │  AWS CLI     │◀────────┼──┤                       │ │  │  │   │
│  │  │  │  (installed) │  read   │  └───────────────────────┘ │  │  │   │
│  │  │  │              │         │                             │  │  │   │
│  │  │  └──────┬───────┘         └─────────────────────────────┘  │  │   │
│  │  │         │                                                    │  │   │
│  │  │         │ Direct S3 Upload (aws s3 cp)                      │  │   │
│  │  │         │ No local/PVC intermediate storage                 │  │   │
│  │  └─────────┼────────────────────────────────────────────────────┘  │   │
│  │            │                                                        │   │
│  └────────────┼────────────────────────────────────────────────────────┘   │
│               │                                                            │
└───────────────┼────────────────────────────────────────────────────────────┘
                │
                │ HTTPS/TLS
                │
                ▼
    ┌───────────────────────────────────────────────┐
    │              AWS S3 Bucket                     │
    │         (my-db2-backups)                       │
    │                                                 │
    │  new_db2/                                      │
    │  └── db2u-manage/                              │
    │      └── database/                             │
    │          └── backup-20240621021316.tar.gz      │
    │                                                 │
    │  ✓ Encrypted in transit (TLS)                  │
    │  ✓ Encrypted at rest (S3 server-side)          │
    │  ✓ Versioning enabled (optional)               │
    │  ✓ Lifecycle policies (optional)               │
    └─────────────────────────────────────────────────┘
```

## In-Cluster DB2 Backup to Local Storage

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         OpenShift/Kubernetes Cluster                     │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        DB2 Namespace (db2u)                       │   │
│  │                                                                    │   │
│  │  ┌────────────────────────────────────────────────────────────┐  │   │
│  │  │                    DB2 Pod (db2u-manage-0)                  │  │   │
│  │  │                                                              │  │   │
│  │  │  ┌──────────────┐         ┌─────────────────────────────┐  │  │   │
│  │  │  │              │         │                             │  │  │   │
│  │  │  │  DB2 Engine  │────────▶│  Backup PVC (/mnt/backup)  │  │  │   │
│  │  │  │              │  backup │                             │  │  │   │
│  │  │  └──────────────┘         │  ┌───────────────────────┐ │  │  │   │
│  │  │                           │  │ backup-20240621.tar.gz│ │  │  │   │
│  │  │                           │  └───────────────────────┘ │  │  │   │
│  │  │                           └─────────────────────────────┘  │  │   │
│  │  └────────────────────────────────────────────────────────────┘  │   │
│  └────────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────┘
                │
                │ oc cp (copy from pod to local)
                │
                ▼
    ┌───────────────────────────────────────────────┐
    │         Ansible Controller / Local Host        │
    │                                                 │
    │  /tmp/db2-backups/                             │
    │  └── backup-20240621021316/                    │
    │      └── database/                             │
    │          └── backup-20240621021316.tar.gz      │
    │                                                 │
    └─────────────────────────────────────────────────┘
```

## RDS DB2 Backup to S3

```
    ┌───────────────────────────────────────────────┐
    │              AWS RDS DB2 Instance              │
    │         (my-db2.abc123.rds.amazonaws.com)      │
    │                                                 │
    │  ┌──────────────────────────────────────────┐ │
    │  │         DB2 Database (BLUDB)             │ │
    │  │                                          │ │
    │  │  - Tables                                │ │
    │  │  - Indexes                               │ │
    │  │  - Data                                  │ │
    │  └──────────────────────────────────────────┘ │
    └───────────────────────────────────────────────┘
                │
                │ DB2 Client Connection (SSL/TLS)
                │ db2 backup db command
                │
                ▼
    ┌───────────────────────────────────────────────┐
    │         Ansible Controller / Local Host        │
    │                                                 │
    │  ┌──────────────────────────────────────────┐ │
    │  │  DB2 Client Tools                        │ │
    │  │  - Catalog RDS node                      │ │
    │  │  - Connect to RDS DB2                    │ │
    │  │  - Execute backup command                │ │
    │  └──────────────────────────────────────────┘ │
    │                                                 │
    │  /tmp/db2-backups/ (temporary)                 │
    │  └── backup-20240621021316/                    │
    │      └── database/                             │
    │          ├── backup-20240621021316.tar.gz      │
    │          └── rds_metadata.yml                  │
    │                                                 │
    │  ┌──────────────────────────────────────────┐ │
    │  │  AWS CLI                                 │ │
    │  │  - Upload to S3                          │ │
    │  │  - Cleanup local files                   │ │
    │  └──────────────────────────────────────────┘ │
    └───────────────────────────────────────────────┘
                │
                │ HTTPS/TLS (aws s3 cp)
                │
                ▼
    ┌───────────────────────────────────────────────┐
    │              AWS S3 Bucket                     │
    │         (my-db2-backups)                       │
    │                                                 │
    │  new_db2/                                      │
    │  └── my-rds-db2/                               │
    │      └── database/                             │
    │          └── backup-20240621021316.tar.gz      │
    │                                                 │
    └─────────────────────────────────────────────────┘
```

## Backup Flow Decision Tree

```
                    ┌─────────────────────┐
                    │  Start Backup Job   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Check db2_type     │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
    ┌───────────────────────┐    ┌───────────────────────┐
    │  db2_type=incluster   │    │   db2_type=rds        │
    └───────────┬───────────┘    └───────────┬───────────┘
                │                             │
                ▼                             ▼
    ┌───────────────────────┐    ┌───────────────────────┐
    │ Check storage_type    │    │ Catalog RDS DB2       │
    └───────────┬───────────┘    │ Connect & Backup      │
                │                 └───────────┬───────────┘
    ┌───────────┴───────────┐                │
    │                       │                 ▼
    ▼                       ▼     ┌───────────────────────┐
┌─────────┐         ┌─────────┐  │ Check storage_type    │
│ S3 Mode │         │Local Mode│  └───────────┬───────────┘
└────┬────┘         └────┬────┘               │
     │                   │        ┌───────────┴───────────┐
     ▼                   ▼        │                       │
┌─────────────────┐ ┌─────────────────┐  ┌─────────┐  ┌─────────┐
│ 1. DB2 backup   │ │ 1. DB2 backup   │  │ S3 Mode │  │Local Mode│
│ 2. Create tar.gz│ │ 2. Create tar.gz│  └────┬────┘  └────┬────┘
│ 3. Install AWS  │ │ 3. oc cp to     │       │            │
│    CLI in pod   │ │    local storage│       ▼            ▼
│ 4. Direct S3    │ └─────────────────┘  ┌─────────────────────┐
│    upload       │                      │ 1. Upload to S3     │
│ 5. No local copy│                      │ 2. Cleanup local    │
└─────────────────┘                      └─────────────────────┘
```

## Key Differences: Old vs New Architecture

### OLD Architecture (Before Fix)
```
In-Cluster DB2 → Pod PVC → Local Storage → S3
                           ↑ unnecessary intermediate step
                           ↑ requires local disk space
                           ↑ double transfer time
```

### NEW Architecture (After Fix)
```
In-Cluster DB2 → Pod PVC → S3 (direct)
                           ↑ single transfer
                           ↑ no local storage needed
                           ↑ faster backup
```

## Storage Requirements Comparison

| Scenario | Old Architecture | New Architecture | Savings |
|----------|------------------|------------------|---------|
| In-Cluster to S3 | Pod PVC + Local Storage + S3 | Pod PVC + S3 | 100% local storage |
| RDS to S3 | Local Storage + S3 | Temp Local + S3 (auto-cleanup) | ~90% local storage |
| In-Cluster to Local | Pod PVC + Local Storage | Pod PVC + Local Storage | No change |

## Security Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. DB2 Encryption                                           │
│     └─ Keystore (keystore.p12)                              │
│     └─ Master Key (master_key_label.kdb)                    │
│                                                               │
│  2. Backup Compression                                       │
│     └─ tar.gz with compression                              │
│                                                               │
│  3. Transfer Encryption                                      │
│     └─ TLS/HTTPS for S3 upload                              │
│     └─ AWS credentials (access key + secret key)            │
│                                                               │
│  4. S3 Storage Encryption                                    │
│     └─ Server-side encryption (SSE-S3 or SSE-KMS)           │
│     └─ Bucket policies and IAM roles                        │
│                                                               │
│  5. Access Control                                           │
│     └─ S3 bucket policies                                   │
│     └─ IAM user/role permissions                            │
│     └─ VPC endpoints (optional)                             │
│                                                               │
└─────────────────────────────────────────────────────────────┘