# Cloud Pak for Data 5.3.1 Installation Guide
## OLM vs Helm Components Architecture

---

## Executive Summary

Cloud Pak for Data (CPD) 5.3.1 introduces a **hybrid architecture** combining:
- **OLM (Operator Lifecycle Manager)** - Traditional operator-based deployment
- **Helm Charts** - New deployment method for select components (introduced in 5.3.x)

This guide provides a comprehensive overview of component distribution, installation procedures, and recommendations.

---

## 1. Component Distribution: OLM vs Helm

### 1.1 Components Supporting ONLY Helm (non-OLM)

These components are **exclusively deployed via Helm charts** in CPD 5.3.1:

| Component | Description | Support Status |
|-----------|-------------|----------------|
| `br_orchestration` | Backup & Restore Orchestration | Helm Only |
| `cognos_analytics` | Cognos Analytics | Helm Only |
| `dashboard` | Dashboard Service | Helm Only |
| `datarefinery` | Data Refinery | Helm Only |
| `datastax_mc` | DataStax Management Console | Helm Only |
| `dods` | Data Operations & Data Science | Helm Only |
| `ibm_events_operator` | IBM Events Operator | Helm Only |
| `ibm-streamsets-sdi` | StreamSets SDI | Helm Only |
| `informix` | Informix Database | Helm Only |
| `model_gateway` | Model Gateway | Helm Only |
| `replication` | Data Replication | Helm Only |
| `rstudio` | RStudio | Helm Only |
| `streamsets` | StreamSets | Helm Only |
| `watsonx_ai` | watsonx.ai | Helm Only |
| `watsonx_ai_ifm` | watsonx.ai IFM | Helm Only |
| `wca` | Watson Code Assistant | Helm Only |
| `wca_ansible` | WCA for Ansible | Helm Only |
| `wca_base` | WCA Base | Helm Only |
| `wca_z` | WCA for Z | Helm Only |
| `wca_z_agentic` | WCA Z Agentic | Helm Only |
| `ws` | Watson Studio | Helm Only |
| `ws_runtimes` | Watson Studio Runtimes | Helm Only |

### 1.2 Components Supporting ONLY OLM

These components are **exclusively deployed via OLM operators**:

| Component | Description | Support Status |
|-----------|-------------|----------------|
| `datagate` | Data Gate | OLM Only |
| `datagate_instance` | Data Gate Instance | OLM Only |
| `dpra` | Data Privacy Risk Assessment | OLM Only |
| `ibm-cert-manager` | IBM Cert Manager | OLM Only |
| `ibm-databand` | IBM Databand | OLM Only |
| `ibm-licensing` | IBM Licensing | OLM Only |
| `mantaflow` | Mantaflow | OLM Only |
| `opencontent_etcd` | OpenContent ETCD | OLM Only |
| `opencontent_redis` | OpenContent Redis | OLM Only |
| `openpages_instance` | OpenPages Instance | OLM Only |
| `productmaster_instance` | Product Master Instance | OLM Only |
| `semantic_automation` | Semantic Automation | OLM Only |
| `voice_gateway` | Voice Gateway | OLM Only |
| `wml_accelerator` | WML Accelerator | OLM Only |
| `wxd_query_optimizer` | watsonx.data Query Optimizer | OLM Only |

### 1.3 Components Supporting BOTH OLM and Helm

These components offer **flexibility** - can be deployed via either method:

| Component | Description | Recommended Method |
|-----------|-------------|-------------------|
| `analyticsengine` | Analytics Engine (Spark) | OLM (mature) |
| `bigsql` | Big SQL | OLM (mature) |
| `canvasbase` | Canvas Base | OLM (mature) |
| `ccs` | Common Core Services | OLM (mature) |
| `cpd_platform` | CPD Platform/Control Plane | **OLM (required)** |
| `cpfs` | Cloud Pak Foundational Services | **OLM (required)** |
| `data_governor` | Data Governor | OLM (mature) |
| `datalineage` | Data Lineage | OLM (mature) |
| `dataproduct` | Data Product | OLM (mature) |
| `datastage_ent` | DataStage Enterprise | OLM (mature) |
| `datastage_ent_plus` | DataStage Enterprise Plus | OLM (mature) |
| `dmc` | Data Management Console | OLM (mature) |
| `dp` | Data Privacy | OLM (mature) |
| `dv` | Data Virtualization | OLM (mature) |
| `factsheet` | Factsheet | OLM (mature) |
| `hee` | Hadoop Execution Engine | OLM (mature) |
| `ibm_redis_cp` | IBM Redis CP | OLM (mature) |
| `ibm_swhcc` | Software Hub Control Center | OLM (mature) |
| `ibm_usage_metering` | IBM Usage Metering | OLM (mature) |
| `ikc_premium` | IBM Knowledge Catalog Premium | OLM (mature) |
| `ikc_standard` | IBM Knowledge Catalog Standard | OLM (mature) |
| `mongodb` | MongoDB | OLM (mature) |
| `opencontent_fdb` | OpenContent FoundationDB | OLM (mature) |
| `opencontent_opensearch` | OpenContent OpenSearch | OLM (mature) |
| `opencontent_rabbitmq` | OpenContent RabbitMQ | OLM (mature) |
| `openpages` | OpenPages | OLM (mature) |
| `openscale` | OpenScale | OLM (mature) |
| `planning_analytics` | Planning Analytics | OLM (mature) |
| `platform-config` | Platform Configuration | **Helm (new in 5.3.x)** |
| `postgresql` | PostgreSQL/EDB | OLM (mature) |
| `scheduler` | Scheduler | OLM (mature) |
| `spss` | SPSS Modeler | OLM (mature) |
| `syntheticdata` | Synthetic Data | OLM (mature) |
| `udp` | Unified Data Platform | OLM (mature) |
| `watson_assistant` | Watson Assistant | OLM (mature) |
| `watson_discovery` | Watson Discovery | OLM (mature) |
| `watson_gateway` | Watson Gateway | OLM (mature) |
| `watson_speech` | Watson Speech | OLM (mature) |
| `watsonx_data` | watsonx.data | OLM (mature) |
| `watsonx_data_premium` | watsonx.data Premium | OLM (mature) |
| `watsonx_dataintelligence` | watsonx Data Intelligence | OLM (mature) |
| `watsonx_governance` | watsonx Governance | OLM (mature) |
| `watsonx_orchestrate` | watsonx Orchestrate | OLM (mature) |
| `wkc` | Watson Knowledge Catalog | OLM (mature) |
| `wml` | Watson Machine Learning | OLM (mature) |
| `ws_pipelines` | Watson Studio Pipelines | OLM (mature) |
| `zen` | Zen (Control Plane UI) | **OLM (required)** |

---

## 2. Installation Architecture

### 2.1 Core Platform Components (MUST use OLM)

The following **foundational components** must be installed via OLM:

1. **cpd_platform** - Cloud Pak for Data Control Plane
2. **zen** - Zen Control Plane (UI/API layer)
3. **cpfs** - Cloud Pak Foundational Services
4. **ibm-licensing** - IBM Licensing Service
5. **ibm-cert-manager** - Certificate Manager
6. **postgresql** - PostgreSQL/EDB (database backend)

### 2.2 Namespace Architecture

CPD 5.3.1 uses a **specialized installation** model:

```
┌─────────────────────────────────────────────────────────────┐
│ Cluster-Scoped Resources                                     │
│ - CRDs, ClusterRoles, ClusterRoleBindings                   │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌────────▼────────┐
│ ibm-licensing  │  │ cpd-operators│  │  cpd-instance   │
│   Namespace    │  │  Namespace   │  │   Namespace     │
│                │  │              │  │                 │
│ - Licensing    │  │ - Operators  │  │ - Workloads     │
│   Service      │  │ - Subscriptions│ │ - CRs          │
│                │  │ - OperatorGroup│ │ - Services     │
└────────────────┘  └──────────────┘  └─────────────────┘
```

**Default Namespaces:**
- `ibm-licensing` - IBM Licensing Service
- `ibm-cpd-operators` (or `cpd-operators`) - All CPD operators
- `ibm-cpd` (or `zen`) - CPD instance workloads

---

## 3. Installation Procedures

### 3.1 OLM-Based Installation

#### Prerequisites
1. OpenShift Container Platform 4.12+
2. Red Hat Certificate Manager installed
3. IBM Entitlement Key
4. Sufficient cluster resources

#### Installation Steps

**Step 1: Install IBM Operator Catalog**
```bash
# Create catalog source for IBM operators
oc apply -f - <<EOF
apiVersion: operators.coreos.com/v1alpha1
kind: CatalogSource
metadata:
  name: ibm-operator-catalog
  namespace: openshift-marketplace
spec:
  displayName: IBM Operator Catalog
  publisher: IBM
  sourceType: grpc
  image: icr.io/cpopen/ibm-operator-catalog:latest
  updateStrategy:
    registryPoll:
      interval: 45m
EOF
```

**Step 2: Create Namespaces**
```bash
# Create required namespaces
oc new-project ibm-licensing
oc new-project ibm-cpd-operators
oc new-project ibm-cpd
```

**Step 3: Install IBM Entitlement Key**
```bash
# Create pull secret in all namespaces
export IBM_ENTITLEMENT_KEY=<your-key>

for ns in ibm-licensing ibm-cpd-operators ibm-cpd; do
  oc create secret docker-registry ibm-entitlement-key \
    --docker-server=cp.icr.io \
    --docker-username=cp \
    --docker-password=$IBM_ENTITLEMENT_KEY \
    -n $ns
done
```

**Step 4: Install CPD Platform Operators**

Using the ansible-devops repository:
```bash
# Set environment variables
export CPD_PRODUCT_VERSION=5.3.1
export CPD_OPERATORS_NAMESPACE=ibm-cpd-operators
export CPD_INSTANCE_NAMESPACE=ibm-cpd
export IBM_ENTITLEMENT_KEY=<your-key>
export CPD_PRIMARY_STORAGE_CLASS=<your-storage-class>
export CPD_METADATA_STORAGE_CLASS=<your-storage-class>

# Run the cp4d role
ansible-playbook ibm/mas_devops/playbooks/cp4d.yml
```

**Step 5: Install CPD Services**

For OLM-based services (e.g., Watson Machine Learning):
```bash
export CPD_SERVICE_NAME=wml
export CPD_PRODUCT_VERSION=5.3.1

ansible-playbook ibm/mas_devops/playbooks/cp4d.yml \
  -e install_watson_machine_learning=true
```

#### Using olm-utils Directly

```bash
# Clone olm-utils repository
git clone https://github.ibm.com/PrivateCloud/olm-utils.git
cd olm-utils

# Set variables
export CPD_OPERATORS_NAMESPACE=ibm-cpd-operators
export CPD_INSTANCE_NAMESPACE=ibm-cpd
export COMPONENTS=cpd_platform,wml,ws,spark

# Install components
./cpd-cli manage apply-olm \
  --release=5.3.1 \
  --components=$COMPONENTS \
  --cpd_operator_ns=$CPD_OPERATORS_NAMESPACE \
  --cpd_instance_ns=$CPD_INSTANCE_NAMESPACE
```

### 3.2 Helm-Based Installation

#### Prerequisites
1. Helm 3.17+ installed
2. OpenShift Container Platform 4.12+
3. Red Hat Certificate Manager installed
4. IBM Entitlement Key
5. Valid storage classes configured

#### Installation Steps

**Step 1: Add Helm Repository**
```bash
# For production
export CHART_REPO="https://raw.github.ibm.com/IBMSoftwareHub/charts/5.3.1/stable"

# For development/testing
export CHART_REPO="https://raw.github.ibm.com/IBMSoftwareHub/charts/5.3.1/dev"

# Add repository
helm repo add cpd-helm-repo $CHART_REPO \
  --username <github-user> \
  --password <github-token>

helm repo update
```

**Step 2: Create Namespaces**
```bash
oc new-project ibm-licensing
oc new-project ibm-cpd-operators  # or zcpfs for testing
oc new-project ibm-cpd            # or zen for testing
```

**Step 3: Create Image Pull Secrets**
```bash
export IBM_ENTITLEMENT_KEY=<your-key>

# Create dockerconfig.json
cat <<EOF > dockerconfig.json
{
  "auths": {
    "cp.icr.io": {
      "auth": "$(echo -n "cp:$IBM_ENTITLEMENT_KEY" | base64 -w 0)"
    },
    "cp.stg.icr.io": {
      "auth": "$(echo -n "cp:$IBM_ENTITLEMENT_KEY" | base64 -w 0)"
    }
  }
}
EOF

# Create secrets in all namespaces
for ns in ibm-licensing ibm-cpd-operators ibm-cpd; do
  oc create secret generic ibm-entitlement-key \
    --from-file=.dockerconfigjson=dockerconfig.json \
    --type=kubernetes.io/dockerconfigjson \
    -n $ns
done
```

**Step 4: Create Override Configuration**
```bash
cat <<EOF > override.yaml
global:
  licenseAccept: true
  releaseVersion: 5.3.1
  operatorNamespace: ibm-cpd-operators
  instanceNamespace: ibm-cpd
  tetheredNamespaces: []
  
  blockStorageClass: <your-block-storage-class>
  fileStorageClass: <your-file-storage-class>
  
  imagePullPrefix: cp.icr.io
  imagePullSecret: ibm-entitlement-key
  
  components:
  - cpd_platform
  - zen
  - cpfs
  - postgresql

zen:
  operatorImageName: cp/ibm-zen-operator
  imagePullSubdir: cp/cpd

cpdPlatform:
  operatorImageName: cp/ibm-cpd-platform-operator

postgresql:
  imageRegistryNamespaceOperator: cp
  imageRegistryNamespaceOperand: cp/edb
  entitledImagePullPrefix: cp.icr.io
  entitledImageRegistryNamespace: cp/cpd
EOF
```

**Step 5: Install Cluster-Scoped Resources (as cluster-admin)**

```bash
# IBM Licensing
helm template ibm-licensing-cluster-scoped-*.tgz \
  -f override.yaml > ibm-licensing-cluster-scoped.yaml
oc apply -f ibm-licensing-cluster-scoped.yaml
oc apply -f ibm-licensing-cluster-scoped.yaml  # Apply twice for CR

# CPD Platform
helm template cpd-platform-cluster-scoped-*.tgz \
  -f override.yaml > cpd-platform-cluster-scoped.yaml
oc apply -f cpd-platform-cluster-scoped.yaml

# Zen
helm template zen-cluster-scoped-*.tgz \
  -f override.yaml > zen-cluster-scoped.yaml
oc apply -f zen-cluster-scoped.yaml

# CPFS Components
helm template ibm-namespace-scope-operator-cluster-scoped-*.tgz \
  -f override.yaml > nss-cluster-scoped.yaml
oc apply -f nss-cluster-scoped.yaml

helm template ibm-common-service-operator-cluster-scoped-*.tgz \
  -f override.yaml > commonservice-cluster-scoped.yaml
oc apply -f commonservice-cluster-scoped.yaml

helm template ibm-iam-operator-cluster-scoped-*.tgz \
  -f override.yaml > iam-cluster-scoped.yaml
oc apply -f iam-cluster-scoped.yaml

# PostgreSQL
helm template postgresql-cluster-scoped-*.tgz \
  -f override.yaml > edb-cluster-scoped.yaml
oc apply --server-side -f edb-cluster-scoped.yaml
```

**Step 6: Install Namespace-Scoped Resources (as tenant-admin)**

```bash
# Switch to tenant admin user
oc login -u <tenant-admin> -p <password>

# Install namespace-scoped charts
helm template cpd-platform-*.tgz -f override.yaml > cpd-platform-ns.yaml
oc apply -f cpd-platform-ns.yaml

helm template zen-*.tgz -f override.yaml > zen-ns.yaml
oc apply -f zen-ns.yaml

helm template ibm-namespace-scope-operator-*.tgz -f override.yaml > nss-ns.yaml
oc apply -f nss-ns.yaml

helm template ibm-common-service-operator-*.tgz -f override.yaml > commonservice-ns.yaml
oc apply -f commonservice-ns.yaml

helm template ibm-iam-operator-*.tgz -f override.yaml > iam-ns.yaml
oc apply -f iam-ns.yaml

helm template postgresql-*.tgz -f override.yaml > edb-ns.yaml
oc apply -f edb-ns.yaml

# Install platform-config (Helm-only component)
helm template platform-config-*.tgz -f override.yaml > platform-config.yaml
oc apply -f platform-config.yaml
```

**Step 7: Install Helm-Only Services**

For services like Watson Studio (ws):
```bash
# Pull the chart
helm pull cpd-helm-repo/ws cpd-helm-repo/ws-cluster-scoped --version <version>

# Update override.yaml to include ws
cat <<EOF >> override.yaml
  components:
  - ws
EOF

# Install cluster-scoped resources
helm template ws-cluster-scoped-*.tgz -f override.yaml > ws-cluster-scoped.yaml
oc apply -f ws-cluster-scoped.yaml

# Install namespace-scoped resources
helm template ws-*.tgz -f override.yaml > ws-ns.yaml
oc apply -f ws-ns.yaml
```

---

## 4. Key Differences: OLM vs Helm

| Aspect | OLM | Helm |
|--------|-----|------|
| **Deployment Method** | Operator Subscriptions | Helm Charts |
| **Lifecycle Management** | Automatic via OLM | Manual via Helm |
| **Upgrade Path** | Operator-managed | Chart-based |
| **Catalog Source** | Required | Not required |
| **Maturity** | Mature (4.x+) | New (5.3.x+) |
| **Complexity** | Higher | Lower |
| **Flexibility** | Less | More |
| **Best For** | Production, automated upgrades | Development, testing, custom configs |

---

## 5. Recommendations

### 5.1 For Production Environments

**Use OLM for:**
- Core platform components (cpd_platform, zen, cpfs)
- All services with OLM support
- Environments requiring automated lifecycle management
- Environments with existing OLM infrastructure

**Use Helm for:**
- Helm-only components (no choice)
- platform-config (new in 5.3.x)
- Development/testing scenarios
- Custom configuration requirements

### 5.2 For Development/Testing

**Helm is preferred when:**
- Testing local chart modifications
- Rapid iteration required
- Fine-grained control needed
- Avoiding OLM complexity

### 5.3 Migration Strategy

If migrating from OLM to Helm:
1. Use migration charts (e.g., `cpd-platform-migration`, `zen-migration`, `cpfs-migration`)
2. Follow the migration guide in olm-utils/non-olm-wiki
3. Test thoroughly in non-production first

---

## 6. Repository Structure

### 6.1 olm-utils Repository
```
olm-utils/
├── ansible-play/
│   ├── config-vars/
│   │   ├── global.yml           # Component definitions
│   │   ├── release-5.3.1.yml    # Version mappings
│   │   └── rbac.yml             # RBAC definitions
│   └── roles/
├── non-olm-wiki/
│   └── non-olm-install.md       # Helm installation guide
└── README.md
```

### 6.2 ansible-devops Repository
```
ansible-devops/
└── ibm/mas_devops/
    ├── playbooks/
    │   └── cp4d.yml              # Main CPD playbook
    ├── roles/
    │   ├── cp4d/                 # CPD platform role
    │   └── cp4d_service/         # CPD service role
    └── common_vars/
        └── cp4d_supported_versions.yml
```

### 6.3 cpd-devops Repository
- Contains additional automation scripts
- Integration with CI/CD pipelines
- Custom deployment scenarios

---

## 7. Version Information (CPD 5.3.1)

### Core Platform Versions
- **cpd_platform**: case 5.4.0, csv 6.4.0, cr 5.4.0
- **zen**: case 6.4.0, csv 6.4.0, cr 6.4.0
- **cpfs**: case 4.17.99, csv 4.17.0
- **postgresql**: EDB Postgres
- **ibm-licensing**: case 4.2.20, csv 4.2.20

### Service Versions (Examples)
- **Watson Machine Learning (wml)**: case 12.1.0, csv 12.1.0
- **Watson Studio (ws)**: case 12.1.0, csv 12.1.0 (Helm-only)
- **Analytics Engine (spark)**: case 12.1.0, csv 9.1.0
- **Cognos Analytics (ca)**: case 29.1.0, csv 29.1.0 (Helm-only)

---

## 8. Troubleshooting

### 8.1 OLM Issues

**Subscription not progressing:**
```bash
# Check subscription status
oc get subscription -n ibm-cpd-operators

# Check install plan
oc get installplan -n ibm-cpd-operators

# Check operator pod logs
oc logs -n ibm-cpd-operators <operator-pod>
```

**Catalog source issues:**
```bash
# Verify catalog source
oc get catalogsource -n openshift-marketplace

# Check catalog pod
oc get pods -n openshift-marketplace | grep ibm-operator-catalog
```

### 8.2 Helm Issues

**Chart installation fails:**
```bash
# Dry-run to validate
helm template <chart> -f override.yaml --dry-run

# Check generated YAML
helm template <chart> -f override.yaml > output.yaml
cat output.yaml
```

**Image pull errors:**
```bash
# Verify pull secret
oc get secret ibm-entitlement-key -n <namespace> -o yaml

# Test image pull
oc run test --image=cp.icr.io/cp/cpd/olm-utils:latest \
  --overrides='{"spec":{"imagePullSecrets":[{"name":"ibm-entitlement-key"}]}}'
```

---

## 9. Next Steps

1. **Review Prerequisites**: Ensure cluster meets all requirements
2. **Choose Deployment Method**: OLM for production, Helm for flexibility
3. **Plan Component List**: Identify which services you need
4. **Prepare Configuration**: Storage classes, namespaces, credentials
5. **Execute Installation**: Follow procedures for chosen method
6. **Validate Deployment**: Check all components are healthy
7. **Configure Services**: Post-installation configuration

---

## 10. Additional Resources

### Documentation
- [olm-utils Wiki](https://github.ibm.com/PrivateCloud/olm-utils/wiki)
- [CPD Official Documentation](https://www.ibm.com/docs/en/cloud-paks/cp-data/5.3.x)
- [Non-OLM Install Guide](https://github.ibm.com/PrivateCloud/olm-utils/blob/5.2.x/non-olm-wiki/non-olm-install.md)

### Repositories
- [olm-utils](https://github.ibm.com/PrivateCloud/olm-utils)
- [cpd-devops](https://github.ibm.com/PrivateCloud/cpd-devops)
- [ansible-devops](https://github.ibm.com/PrivateCloud/ansible-devops)
- [IBM Helm Charts](https://github.com/IBM/charts/tree/master/repo/ibm-helm)

### Configuration Files
- [global.yml](https://github.ibm.com/PrivateCloud/olm-utils/blob/5.3.1/ansible-play/config-vars/global.yml) - Component support matrix
- [release-5.3.1.yml](https://github.ibm.com/PrivateCloud/olm-utils/blob/5.3.1/ansible-play/config-vars/release-5.3.1.yml) - Version mappings

---

**Document Version**: 1.0  
**Last Updated**: 2026-06-17  
**CPD Version**: 5.3.1