# CPD 5.3.1 Version Mapping and Component Support

## Overview
Cloud Pak for Data 5.3.1 introduces a **hybrid architecture** where some components use OLM (Operator Lifecycle Manager) and others use Helm charts. This document explains the version mapping between OLM CSV versions and Helm CASE versions.

## Version Mapping Explained

### Understanding the Version Numbers

For each component in CPD 5.3.1, there are multiple version numbers:

1. **CASE Version**: The Cloud Pak Application Software Engineering (CASE) package version
2. **CSV Version**: The ClusterServiceVersion (operator) version used in OLM
3. **CR Version**: The Custom Resource version for the component
4. **Helm Chart Version**: The version embedded in the Helm chart filename

### Key Components Version Mapping

#### Watson Machine Learning (WML)
- **CASE Version**: `12.1.0`
- **CSV Version**: `9.1.0` (OLM operator version)
- **Subscription Channel**: `v9.1`
- **CR Version**: `5.3.1`
- **Helm Chart**: `wml-12.1.3+<timestamp>.tgz`
- **Support**: `helm_preferred` (supports both OLM and Helm, Helm is preferred)

**Why the difference?**
- The CASE version (12.1.0) represents the **package/bundle version**
- The CSV version (9.1.0) represents the **operator version** in OLM
- The Helm chart version (12.1.3) is the **actual chart release** from the CASE package
- These are independent versioning schemes that don't need to match

#### Analytics Engine / Spark
- **CASE Version**: `12.1.0`
- **CSV Version**: `9.1.0` (OLM operator version)
- **Subscription Channel**: `v9.1`
- **CR Version**: `5.3.1`
- **Helm Chart**: `analyticsengine-12.1.6+<timestamp>.tgz`
- **Support**: `helm_preferred` (supports both OLM and Helm, Helm is preferred)

#### Cognos Analytics (CA)
- **CASE Version**: `29.1.0`
- **CSV Version**: `29.1.0` (OLM operator version)
- **Subscription Channel**: `v29.1`
- **CR Version**: `29.1.0`
- **Helm Chart**: Not yet verified in charts repo
- **Support**: `helm_only` (OLM deprecated, Helm required)

#### Watson Studio (WSL/WS)
- **CASE Version**: Not specified in release config (Helm-only component)
- **CSV Version**: N/A (no OLM support)
- **CR Version**: `5.3.1`
- **Helm Chart**: `ws-<version>+<timestamp>.tgz`
- **Support**: `helm_only` (OLM deprecated, Helm required)

## Component Support Matrix

### Helm-Only Components (OLM Deprecated)
These components **MUST** be installed via Helm in CPD 5.3.1:

```yaml
support_olm: false
support_non_olm: true  # non_olm = Helm
```

Components:
- **Watson Studio (ws)**: `helm_only`
- **Cognos Analytics (cognos_analytics)**: `helm_only`
- **Watson Studio Runtimes (ws_runtimes)**: `helm_only`
- **DODS**: `helm_only`
- **RStudio**: `helm_only`
- **watsonx.ai**: `helm_only`
- **watsonx.ai IFM**: `helm_only`
- **Model Gateway**: `helm_only`
- **Dashboard**: `helm_only`
- **WCA (Watson Code Assistant)**: `helm_only`
- **WCA Base**: `helm_only`
- **WCA Z**: `helm_only`
- **WCA Z Agentic**: `helm_only`
- **WCA Ansible**: `helm_only`
- **Informix**: `helm_only`
- **Informix CP4D**: `helm_only`

### Helm-Preferred Components (Both Supported)
These components support **both OLM and Helm**, but Helm is the recommended method:

```yaml
support_olm: true
support_non_olm: true
```

Components:
- **Watson Machine Learning (wml)**: `helm_preferred`
- **Analytics Engine / Spark (analyticsengine)**: `helm_preferred`

### OLM-Only Components
These components **MUST** be installed via OLM:

```yaml
support_olm: true
support_non_olm: false
```

Components include:
- **Datagate**
- **Datagate Instance**
- **DPRA**
- **Voice Gateway**
- **OpenPages Instance**
- **Semantic Automation**
- **WML Accelerator**
- **OpenContent Redis**
- **OpenContent Etcd**
- **IBM Cert Manager**
- **IBM Licensing**
- **Mantaflow**
- **Product Master Instance**

### Components Supporting Both Methods Equally
These components support both OLM and Helm without preference:

- **CPD Platform**
- **Zen**
- **CPFS**
- **Scheduler**
- **DB2U**
- **DB2 Warehouse**
- **DB2 OLTP**
- **DB2 AASERVICE**
- **Data Virtualization (DV)**
- **Watson Discovery**
- **Watson Assistant**
- **Watson Speech**
- **OpenScale**
- **Planning Analytics**
- **WKC (Watson Knowledge Catalog)**
- **IKC Premium**
- **IKC Standard**
- **Match360**
- **DMC**
- **DataStage**
- **Replication**
- **SPSS**
- **Synthetic Data**
- **Factsheet**
- **MongoDB**
- **MongoDB CP4D**
- **EDB CP4D**
- **OpenSearch**
- **OpenContent FDB**
- **OpenContent RabbitMQ**
- **IBM Redis CP**
- **CCS**
- **Canvasbase**
- **HEE (Hadoop)**
- **IBM Neo4j**
- **PostgreSQL**
- **Product Master**
- **Watson Gateway**
- **watsonx Governance**
- **watsonx Orchestrate**
- **watsonx Data**
- **watsonx Data Premium**
- **watsonx BI Assistant**
- **watsonx Data Intelligence**
- **WS Pipelines**
- **WCA Z Understand**
- **WCA Z Code Explanation**
- **WCA Z Code Generation**
- **IBM Usage Metering**
- **Data Governor**

## Dependency Versions

### OpenSearch
- **CASE Version**: `1.2.0`
- **Helm Chart**: `opencontent-opensearch`
- **Cluster Chart**: `opencontent-opensearch-cluster-scoped`
- **CRD**: `clusters.opensearch.cloudpackopen.ibm.com`

### CCS (Common Core Services)
- **CASE Version**: `12.1.0`
- **Helm Chart**: `ccs`
- **Cluster Chart**: `ccs-cluster-scoped`
- **CRD**: `ccs.ccs.cpd.ibm.com`

### IBM Redis CP
- **CASE Version**: `1.3.1` (NOT 2.1.0)
- **Helm Chart**: `ibm-redis-cp`
- **Cluster Chart**: `ibm-redis-cp-cluster-scoped`
- **CRD**: `redissentinels.redis.databases.cloud.ibm.com`

## Chart Verification Results

### Verified Chart Names

#### WML Charts (Confirmed)
```bash
# From: Documents/Git/charts/promoted/ibm-wml-cpd/
wml-12.1.3+20260521.063405.18.tgz
wml-cluster-scoped-12.1.3+20260521.063405.18.tgz
```
✅ Chart names match configuration:
- Namespace chart: `wml`
- Cluster chart: `wml-cluster-scoped`

#### Spark/Analytics Engine Charts (Confirmed)
```bash
# From: Documents/Git/charts/promoted/ibm-analyticsengine/
analyticsengine-12.1.6+20260520.001203.2183.tgz
analyticsengine-cluster-scoped-12.1.6+20260520.001203.2183.tgz
```
✅ Chart names match configuration:
- Namespace chart: `analyticsengine`
- Cluster chart: `analyticsengine-cluster-scoped`

## Installation Method Decision Tree

```
Is the component in the "Helm-Only" list?
├─ YES → Use Helm installation (OLM not supported)
└─ NO → Is it in the "Helm-Preferred" list?
    ├─ YES → Use Helm installation (recommended, OLM available as fallback)
    └─ NO → Is it in the "OLM-Only" list?
        ├─ YES → Use OLM installation (Helm not supported)
        └─ NO → Use either method (both fully supported)
```

## Configuration in ansible-devops

### Component Metadata Structure
```yaml
component_name:
  helm_chart_name: "chart-name"
  helm_cluster_chart: "chart-name-cluster-scoped"
  case_version: "X.Y.Z"
  helm_dependencies:
    - *opensearch_dependency
    - *ccs_dependency
    - *ibm_redis_cp_dependency
```

### Support Matrix Entry
```yaml
component_name:
  olm: true/false
  helm: true/false
  preferred: "olm" or "helm"
```

## Key Takeaways

1. **Version numbers don't need to match** between CASE, CSV, and Helm chart versions
2. **CASE version** is used for Helm chart lookup (e.g., `12.1.0`)
3. **CSV version** is used for OLM subscriptions (e.g., `9.1.0`)
4. **Helm chart version** in filename may be higher than CASE version (e.g., `12.1.3`)
5. **Always refer to `support_olm` and `support_non_olm`** flags in global.yml to determine installation method
6. **Helm is the future** - IBM is deprecating OLM for many components in favor of Helm

## References

- **OLM Config**: `olm-utils/ansible-play/config-vars/release-5.3.1.yml`
- **Component Support**: `olm-utils/ansible-play/config-vars/global.yml`
- **Helm Charts**: `charts/promoted/ibm-<component>/`
- **ansible-devops Config**: `ibm/mas_devops/roles/cp4d_service/defaults/main.yml`
- **Support Matrix**: `ibm/mas_devops/roles/cp4d_service/vars/component-support.yml`