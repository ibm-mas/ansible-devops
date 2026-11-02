# UMS Usage Guide

This document covers three topics:

1. [Installation commands and ENV variables](#installation)
2. [How to use UMS after installation](#using-ums)
3. [MAS metric definitions for UMS](#mas-metric-definitions)

---

## Installation

### Scenario 1 — Fresh install (no existing DRO)

```bash
export ROLE_NAME=ums

# Required
export IBM_ENTITLEMENT_KEY=<your-entitlement-key>
export UMS_CONTACT_EMAIL=john@example.com
export UMS_CONTACT_FIRSTNAME=John
export UMS_CONTACT_LASTNAME=Doe

# MAS config generation
export MAS_INSTANCE_ID=masinst1
export MAS_CONFIG_DIR=/tmp/masconfig

# No DRO to migrate from
export UMS_MIGRATE_FROM_DRO=false

ansible-playbook ibm/mas_devops/playbooks/run_role.yml
```

### Scenario 2 — Migrate from DRO (most common)

```bash
export ROLE_NAME=ums

# Required
export IBM_ENTITLEMENT_KEY=<your-entitlement-key>
export UMS_CONTACT_EMAIL=john@example.com
export UMS_CONTACT_FIRSTNAME=John
export UMS_CONTACT_LASTNAME=Doe

# MAS config generation
export MAS_INSTANCE_ID=masinst1
export MAS_CONFIG_DIR=/tmp/masconfig

# Migration — specify where DRO is currently installed
export UMS_MIGRATE_FROM_DRO=true
export DRO_NAMESPACE=redhat-marketplace  # default; change if DRO was in a custom namespace

# Optional overrides
export UMS_NAMESPACE=ibm-usage-metering
export UMS_CATALOG_IMAGE=icr.io/cpopen/ibm-usage-metering-operator-catalog:1.0.4

ansible-playbook ibm/mas_devops/playbooks/run_role.yml
```

### Scenario 3 — Skip install, generate MAS config for existing UMS

```bash
export ROLE_NAME=ums
export UMS_ACTION=skip

# Pre-existing UMS endpoint (skips in-cluster route lookup)
export UMS_ENDPOINT_URL=https://ibm-usage-metering-instance.apps.cluster.example.com
export UMS_API_TOKEN=<token-from-ibm-usage-metering-upload-token-secret>

export UMS_CONTACT_EMAIL=john@example.com
export UMS_CONTACT_FIRSTNAME=John
export UMS_CONTACT_LASTNAME=Doe

export MAS_INSTANCE_ID=masinst1
export MAS_CONFIG_DIR=/tmp/masconfig

ansible-playbook ibm/mas_devops/playbooks/run_role.yml
```

### Scenario 4 — Uninstall UMS

```bash
export ROLE_NAME=ums
export UMS_ACTION=uninstall
export UMS_NAMESPACE=ibm-usage-metering  # must match where it was installed

ansible-playbook ibm/mas_devops/playbooks/run_role.yml
```

### Environment variable reference

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `IBM_ENTITLEMENT_KEY` | ✅ install only | — | Pull images from `icr.io` |
| `UMS_CONTACT_EMAIL` | ✅ gencfg | — | Written into `BasCfg` |
| `UMS_CONTACT_FIRSTNAME` | ✅ gencfg | — | Written into `BasCfg` |
| `UMS_CONTACT_LASTNAME` | ✅ gencfg | — | Written into `BasCfg` |
| `MAS_INSTANCE_ID` | ✅ gencfg | — | Target MAS instance |
| `MAS_CONFIG_DIR` | ✅ gencfg | — | Where `ums.yml` is written |
| `UMS_ACTION` | optional | `install` | `install` / `uninstall` / `skip` |
| `UMS_NAMESPACE` | optional | `ibm-usage-metering` | Namespace for UMS resources |
| `UMS_MIGRATE_FROM_DRO` | optional | `true` | Auto-uninstall DRO before installing UMS |
| `DRO_NAMESPACE` | optional | `redhat-marketplace` | Where to look for existing DRO |
| `UMS_CATALOG_IMAGE` | optional | `…:latest` | Pin to a specific version in production |
| `UMS_SOFTWARE_CENTRAL_ENABLE` | optional | `false` | Enable automatic uploads to Software Central |

---

## Using UMS

UMS is a headless REST API service — there is no built-in UI dashboard. All interaction is via API using a token and TLS certificate retrieved from the cluster.

### Step 1 — Retrieve credentials and endpoint

```bash
# API token
oc get secret ibm-usage-metering-upload-token \
  -n ibm-usage-metering \
  -o jsonpath='{.data.token}' | base64 -d

# TLS certificate (for secure curl calls)
oc get cm ibm-usage-metering-upload-config \
  -n ibm-usage-metering \
  -o jsonpath='{.data.tls\.crt}' > /tmp/ums-tls.crt

# In-cluster service URL
oc get cm ibm-usage-metering-upload-config \
  -n ibm-usage-metering \
  -o jsonpath='{.data.url}'

# External route URL
oc get route ibm-usage-metering-instance \
  -n ibm-usage-metering \
  -o jsonpath='{.spec.host}'
```

### Step 2 — Register your metric

Create an `IBMServiceMeterDefinition` CR in the **product's namespace**. This holds the static metadata. See [MAS Metric Definitions](#mas-metric-definitions) for the full list of CRs for each MAS event type.

### Step 3 — Send metric data

```bash
TOKEN=$(oc get secret ibm-usage-metering-upload-token \
  -n ibm-usage-metering -o jsonpath='{.data.token}' | base64 -d)

UMS_URL="https://ibm-usage-metering-instance.ibm-usage-metering.svc.cluster.local"

curl --cacert /tmp/ums-tls.crt \
     --request POST \
     --header "Content-Type: application/json" \
     --header "Authorization: Bearer $TOKEN" \
     --data '[
       {
         "mappingId": "<your-mappingId>",
         "instances": [
           {
             "metrics": [
               { "metricQuantity": 10 }
             ]
           }
         ]
       }
     ]' \
     "$UMS_URL/api/v1/event"
```

> **Limit:** Combined CR + payload must be under **100 KB**. Split large payloads into multiple calls.

### Step 4 — Verify data was received

```bash
curl --cacert /tmp/ums-tls.crt \
     --request GET \
     --header "Authorization: Bearer $TOKEN" \
     "$UMS_URL/api/v1/raw"
```

### Step 5 — Download the audit snapshot

```bash
FETCH_URL=$(oc get route ibm-usage-metering-fetch \
  -n ibm-usage-metering -o jsonpath='{.spec.host}')

oc get cm kube-root-ca.crt \
  -n ibm-usage-metering -o jsonpath='{.data.ca\.crt}' > /tmp/ums-ca.crt

# Download snapshot (last 30 days by default)
curl --cacert /tmp/ums-ca.crt \
     --request GET \
     --header "Authorization: Bearer $TOKEN" \
     --output snapshot.zip \
     "https://$FETCH_URL/api/v1/snapshot"

# Optional: filter by date range
# "https://$FETCH_URL/api/v1/snapshot?startDate=2025-01-01&endDate=2025-01-31"
```

### API endpoint summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/event` | `POST` | Upload metric data |
| `/api/v1/raw` | `GET` | Verify raw uploaded data |
| `/api/v1/snapshot` | `GET` | Download audit snapshot (`.zip`) |
| `/api/v1/swc` | `GET` | Download Software Central payload (`.tar.gz`) |

Two routes are created in `ums_namespace`:
- `ibm-usage-metering-instance` — upload and query endpoint
- `ibm-usage-metering-fetch` — audit snapshot and Software Central download endpoint

### Software Central (optional)

If `UMS_SOFTWARE_CENTRAL_ENABLE=true` was set during install, UMS sends to Software Central automatically at 12:05 AM UTC daily. For airgapped clusters, download and upload manually:

```bash
# Download
curl --header "Authorization: Bearer $TOKEN" \
     --cacert /tmp/ums-ca.crt \
     --output swc_payload.tar.gz \
     "https://$FETCH_URL/api/v1/swc"

# Upload from a connected machine
curl -X POST "https://swc.saas.ibm.com/metering/api/v2/metrics" \
     -H "Authorization: Bearer $IBM_ENTITLEMENT_KEY" \
     -F "file=@swc_payload.tar.gz;type=application/gzip"
```

---

## MAS Metric Definitions

### Field mapping: MAS payload → UMS

The MAS payload `unit` field maps directly to `spec.data.metricName` in the `IBMServiceMeterDefinition` CR.

| MAS payload field | UMS CR field | UMS JSON payload field | Notes |
|---|---|---|---|
| `unit` | `spec.data.metricName` | — | e.g. `AppPoints`, `Licenses`, `Users`, `Capability Values` |
| `unitDescription` | `spec.data.metricDescription` | — | Human-readable description |
| `productId` | `spec.data.productId` | — | e.g. `5737-M66`, `5900-AMG` |
| `productTitle` | `spec.data.productName` | — | e.g. `Maximo Application Suite` |
| `instanceId` | `spec.data.instanceId` | — | `<source>-<instanceName>` |
| `quantity` | — | `metricQuantity` | Measured value, sent hourly |
| `unitMetadata.data.*` | `spec.breakdownDefs` | extra fields in metrics | Sub-metric breakdown data |
| `frequency: Hourly` | `processing: MAX` or `ADD` | — | Daily aggregation strategy |

**Contractual vs Adoption:**
- Only `AppPoints` events (`Account Contractual Usage`) use `metricType: CONTRACTUAL` — they appear in compliance/audit snapshots.
- Everything else (`Licenses`, `Users`, `Capability Values`, object events) uses `metricType: ADOPTION`.

---

### 1. Contractual — AppPoints (MAS on-prem)

**Source event:** `Account Contractual Usage`

```yaml
apiVersion: operator.ibm.com/v1
kind: IBMServiceMeterDefinition
metadata:
  name: mas-apppoints-metering-definition
  namespace: mas-inst1-core
spec:
  mappingId: mas-apppoints-5737m66-inst1
  processing: MAX
  data:
    instanceId: "<source>-<instanceName>"    # e.g. a2d89e0861e6-a311671
    productId: 5737-M66
    productName: Maximo Application Suite
    metricName: AppPoints
    metricDescription: Account level AppPoint usage
    metricType: CONTRACTUAL
```

```json
[
  {
    "mappingId": "mas-apppoints-5737m66-inst1",
    "instances": [
      {
        "metrics": [
          {
            "measurementTimestamp": "2025-12-12T21:00:20Z",
            "metricQuantity": 10,
            "quantityEntitled": 68
          }
        ]
      }
    ]
  }
]
```

---

### 2. Contractual — AppPoints (AI Service)

**Source event:** `Account Contractual Usage` with `subProductTitle: MAS AI Service`

```yaml
apiVersion: operator.ibm.com/v1
kind: IBMServiceMeterDefinition
metadata:
  name: mas-aiservice-apppoints-definition
  namespace: mas-inst1-core
spec:
  mappingId: mas-apppoints-aiservice-5737m66-inst1
  processing: MAX
  data:
    instanceId: "<source>-<instanceName>"
    productId: 5737M66
    productName: Maximo AI Service
    metricName: AppPoints
    metricDescription: Account level AppPoint usage
    metricType: CONTRACTUAL
```

```json
[
  {
    "mappingId": "mas-apppoints-aiservice-5737m66-inst1",
    "instances": [
      {
        "metrics": [
          {
            "measurementTimestamp": "2025-12-14T23:30:53Z",
            "metricQuantity": 0,
            "quantityEntitled": 500
          }
        ]
      }
    ]
  }
]
```

---

### 3. Adoption — Licenses (Account Level)

**Source event:** `Account Adoption Usage` with `unit: Licenses`

```yaml
apiVersion: operator.ibm.com/v1
kind: IBMServiceMeterDefinition
metadata:
  name: mas-licenses-metering-definition
  namespace: mas-inst1-core
spec:
  mappingId: mas-licenses-5737m66-inst1
  processing: MAX
  breakdownDefs:
    - breakdownBy:
        name: licenseTypeBreakdown
      groupBy:
        - licenseType
      source: licenseCount
      processing: MAX
  data:
    instanceId: "<source>-<instanceName>"
    productId: 5737-M66
    productName: Maximo Application Suite
    metricName: Licenses
    metricDescription: Account level License usage
    metricType: ADOPTION
```

```json
[
  {
    "mappingId": "mas-licenses-5737m66-inst1",
    "instances": [
      {
        "metrics": [
          {
            "measurementTimestamp": "2025-12-12T21:00:19Z",
            "metricQuantity": 45,
            "masAdminBase": 1,
            "masAdminPremium": 0,
            "masUsersBase": 2,
            "masUsersBaseAuthorized": 0,
            "masUsersLite": 3,
            "masUsersLiteAuthorized": 0,
            "masUsersPremium": 0,
            "masUsersPremiumAuthorized": 0,
            "masAPIBase": 0,
            "masAPILite": 0,
            "masAPIPremium": 0,
            "masSelfService": 0,
            "masServerBase": 0,
            "masServerLite": 0,
            "masServerPremium": 0,
            "masAddonBase": 0,
            "masAddonLite": 0,
            "masAddonPremium": 0
          }
        ]
      }
    ]
  }
]
```

> `metricQuantity` = total licensed users. Per-type counts from `unitMetadata.data` are passed as flat fields alongside `metricQuantity`.

---

### 4. Adoption — Users (Unique Users per Capability)

**Source event:** `Account Adoption Usage` with `unit: Users`

One CR per capability (`subProductTitle`). Repeat for `manage`, `monitor`, `health`, `visualinspection`, etc.

```yaml
apiVersion: operator.ibm.com/v1
kind: IBMServiceMeterDefinition
metadata:
  name: mas-users-manage-definition
  namespace: mas-inst1-core
spec:
  mappingId: mas-users-manage-5900amg-inst1
  processing: MAX
  data:
    instanceId: "<source>-<instanceName>"
    productId: 5900-AMG
    productName: Maximo Application Suite SaaS
    metricName: Users
    metricDescription: Unique users per capability
    metricType: ADOPTION
```

```json
[
  {
    "mappingId": "mas-users-manage-5900amg-inst1",
    "instances": [
      {
        "metrics": [
          {
            "measurementTimestamp": "2025-03-09T02:01:07Z",
            "metricQuantity": 0
          }
        ]
      }
    ]
  }
]
```

---

### 5. Adoption — Capability Values (Manage)

**Source event:** `Account Adoption Usage` with `unit: Capability Values`, `subProductTitle: manage`

```yaml
apiVersion: operator.ibm.com/v1
kind: IBMServiceMeterDefinition
metadata:
  name: mas-capvalues-manage-definition
  namespace: mas-inst1-core
spec:
  mappingId: mas-capvalues-manage-5737m66-inst1
  processing: MAX
  data:
    instanceId: "<source>-<instanceName>"
    productId: 5737-M66
    productName: Maximo Application Suite
    metricName: Capability Values
    metricDescription: Account level Capability Valuemetrics usage
    metricType: ADOPTION
```

```json
[
  {
    "mappingId": "mas-capvalues-manage-5737m66-inst1",
    "instances": [
      {
        "metrics": [
          {
            "measurementTimestamp": "2025-12-12T22:10:44Z",
            "metricQuantity": 0,
            "Install": 1,
            "AIInferencesApplied": 0,
            "AIInferencesPerformed": 0,
            "Database-replicas": 0,
            "MobileUserCountWithAccessToApp": 0,
            "SKDProject": 0,
            "SKDProjectDashboard": 0
          }
        ]
      }
    ]
  }
]
```

---

### 6. Adoption — Capability Values (Monitor)

**Source event:** `Account Adoption Usage` with `unit: Capability Values`, `subProductTitle: monitor`

```yaml
apiVersion: operator.ibm.com/v1
kind: IBMServiceMeterDefinition
metadata:
  name: mas-capvalues-monitor-definition
  namespace: mas-inst1-core
spec:
  mappingId: mas-capvalues-monitor-5737m66-inst1
  processing: MAX
  data:
    instanceId: "<source>-<instanceName>"
    productId: 5737-M66
    productName: Maximo Application Suite
    metricName: Capability Values
    metricDescription: Account level Capability Valuemetrics usage
    metricType: ADOPTION
```

```json
[
  {
    "mappingId": "mas-capvalues-monitor-5737m66-inst1",
    "instances": [
      {
        "metrics": [
          {
            "measurementTimestamp": "2025-12-12T21:00:18Z",
            "metricQuantity": 0,
            "Install": 0,
            "IOPoints": 0,
            "KPIPoints": 0,
            "NumOfAssets": 0,
            "NumOfBatchKPIs": 0,
            "NumOfBatchPipelines": 0,
            "NumOfLocations": 0,
            "NumOfRegisteredDevices": 0,
            "NumOfStreamingPipelines": 0
          }
        ]
      }
    ]
  }
]
```

---

### 7. Adoption — Capability Values (Workday / Spatial / SAP Adapters)

**Source event:** `Account Adoption Usage` with `unit: Capability Values`, `subProductTitle: workday | spatial | sapadapter`

One CR per add-on. All three have only `Install` in `unitMetadata.data`.

```yaml
apiVersion: operator.ibm.com/v1
kind: IBMServiceMeterDefinition
metadata:
  name: mas-capvalues-workday-definition    # or: spatial, sapadapter
  namespace: mas-inst1-core
spec:
  mappingId: mas-capvalues-workday-5737m66-inst1
  processing: MAX
  data:
    instanceId: "<source>-<instanceName>"
    productId: 5737-M66
    productName: Maximo Application Suite
    metricName: Capability Values
    metricDescription: Account level Capability Valuemetrics usage
    metricType: ADOPTION
```

```json
[
  {
    "mappingId": "mas-capvalues-workday-5737m66-inst1",
    "instances": [
      {
        "metrics": [
          {
            "measurementTimestamp": "2025-12-12T21:00:19Z",
            "metricQuantity": 0,
            "Install": 0
          }
        ]
      }
    ]
  }
]
```

---

### 8. Adoption — Low-Level Object Events (Manage)

**Source events:** `Created Object` / `Updated Object` with `objectType` field. No `unit` field present — use `objectType` as `metricName`.

Use `processing: ADD` since each event is a discrete occurrence. **Batch events** over the reporting interval and send a single count, rather than one API call per event.

Object types observed: `Work Order`, `Material Receipt`, `Purchase Order`, `Inspection`, `Issues and Transfers`, `Workflow`.

```yaml
apiVersion: operator.ibm.com/v1
kind: IBMServiceMeterDefinition
metadata:
  name: mas-workorder-events-definition     # one CR per objectType
  namespace: mas-inst1-core
spec:
  mappingId: mas-workorder-5900amg-inst1
  processing: ADD
  data:
    instanceId: "<source>-<instanceName>"
    productId: 5900-AMG
    productName: Maximo Application Suite SaaS
    metricName: Work Order                  # matches objectType exactly
    metricDescription: Work Orders created or updated in Manage
    metricType: ADOPTION
```

```json
[
  {
    "mappingId": "mas-workorder-5900amg-inst1",
    "instances": [
      {
        "metrics": [
          {
            "measurementTimestamp": "2025-12-12T20:24:49Z",
            "metricQuantity": 1,
            "processType": "mobile"
          }
        ]
      }
    ]
  }
]
```

> Include `processType` only when present in the original event (e.g. `"mobile"` for mobile work orders and inspections).

---

### 9. Adoption — User Created & Application Milestones

**Source events:** `Created Object` with `objectType: USER` and `Created Object` with `milestoneName: Installed | Activated | Deactivated | Uninstalled`

```yaml
# User created
apiVersion: operator.ibm.com/v1
kind: IBMServiceMeterDefinition
metadata:
  name: mas-user-created-definition
  namespace: mas-inst1-core
spec:
  mappingId: mas-user-created-5900amg-inst1
  processing: ADD
  data:
    instanceId: "<source>-<instanceName>"
    productId: 5900-AMG
    productName: Maximo Application Suite SaaS
    metricName: USER
    metricDescription: Users created in MAS
    metricType: ADOPTION
---
# Application milestone
apiVersion: operator.ibm.com/v1
kind: IBMServiceMeterDefinition
metadata:
  name: mas-app-milestone-definition
  namespace: mas-inst1-core
spec:
  mappingId: mas-app-milestone-5900amg-inst1
  processing: LAST
  data:
    instanceId: "<source>-<instanceName>"
    productId: 5900-AMG
    productName: Maximo Application Suite SaaS
    metricName: Application Milestone
    metricDescription: Application installed/activated/deactivated in MAS
    metricType: ADOPTION
```

---

### CR naming convention

| Metric | CR name | mappingId | `processing` |
|--------|---------|-----------|--------------|
| AppPoints (MAS) | `mas-apppoints-metering-definition` | `mas-apppoints-5737m66-<instanceName>` | MAX |
| AppPoints (AI Service) | `mas-aiservice-apppoints-definition` | `mas-apppoints-aiservice-5737m66-<instanceName>` | MAX |
| Licenses | `mas-licenses-metering-definition` | `mas-licenses-5737m66-<instanceName>` | MAX |
| Users (per capability) | `mas-users-<capability>-definition` | `mas-users-<capability>-5900amg-<instanceName>` | MAX |
| Capability Values — Manage | `mas-capvalues-manage-definition` | `mas-capvalues-manage-5737m66-<instanceName>` | MAX |
| Capability Values — Monitor | `mas-capvalues-monitor-definition` | `mas-capvalues-monitor-5737m66-<instanceName>` | MAX |
| Capability Values — add-on | `mas-capvalues-<addon>-definition` | `mas-capvalues-<addon>-5737m66-<instanceName>` | MAX |
| Object events | `mas-<objecttype>-events-definition` | `mas-<objecttype>-5900amg-<instanceName>` | ADD |
| User Created | `mas-user-created-definition` | `mas-user-created-5900amg-<instanceName>` | ADD |
| App Milestone | `mas-app-milestone-definition` | `mas-app-milestone-5900amg-<instanceName>` | LAST |
