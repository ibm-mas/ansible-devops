#!/bin/bash
#  MinIO to Ceph Migration using MinIO Client (mc)
# Features: Metadata backup, object migration, retry logic, automatic cleanup

set -e
set -o pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
MINIO_NAMESPACE="${MINIO_NAMESPACE:-minio}"
CEPH_NAMESPACE="${CEPH_NAMESPACE:-openshift-storage}"
AISERVICE_NAMESPACE="${AISERVICE_NAMESPACE:-aiservice-aisdk}"
MC_IMAGE="${MC_IMAGE:-minio/mc:RELEASE.2025-07-21T05-28-08Z}"
MAX_RETRIES=3
RETRY_DELAY=5
BACKUP_DIR="/backup"
PVC_SIZE="${PVC_SIZE:-10Gi}"

# Global variables
MIGRATION_FAILED=0
CLEANUP_DONE=0

# Cleanup function
cleanup() {
  if [ ${CLEANUP_DONE} -eq 1 ]; then
    return
  fi
  
  log_info "Performing cleanup..."
  
  # Delete migration pod
  if oc get pod mc-migration -n ${CEPH_NAMESPACE} &>/dev/null; then
    log_info "Deleting migration pod..."
    oc delete pod mc-migration -n ${CEPH_NAMESPACE} --ignore-not-found=true --wait=false
  fi
  
  # Delete ConfigMap
  if oc get configmap mc-migration-config -n ${CEPH_NAMESPACE} &>/dev/null; then
    log_info "Deleting migration ConfigMap..."
    oc delete configmap mc-migration-config -n ${CEPH_NAMESPACE} --ignore-not-found=true
  fi
  
  CLEANUP_DONE=1
  log_success "Cleanup completed"
}

# Trap for cleanup on exit
trap cleanup EXIT INT TERM

# Retry function
retry_command() {
  local max_attempts=$1
  shift
  local cmd="$@"
  local attempt=1
  
  while [ ${attempt} -le ${max_attempts} ]; do
    log_info "Attempt ${attempt}/${max_attempts}: ${cmd}"
    if eval "${cmd}"; then
      return 0
    else
      if [ ${attempt} -lt ${max_attempts} ]; then
        log_warning "Command failed, retrying in ${RETRY_DELAY} seconds..."
        sleep ${RETRY_DELAY}
      fi
      attempt=$((attempt + 1))
    fi
  done
  
  log_error "Command failed after ${max_attempts} attempts"
  return 1
}

log_info "=========================================="
log_info "MinIO to Ceph Migration (mc)"
log_info "=========================================="
log_info "Configuration:"
log_info "  MinIO Namespace: ${MINIO_NAMESPACE}"
log_info "  Ceph Namespace: ${CEPH_NAMESPACE}"
log_info "  mc Image: ${MC_IMAGE}"
log_info "  Max Retries: ${MAX_RETRIES}"

# Step 1: Get MinIO credentials
log_info "Step 1: Getting MinIO credentials..."

if ! oc get secret minio-secret -n ${MINIO_NAMESPACE} &>/dev/null; then
  log_warning "MinIO secret 'minio-secret' not found, using defaults"
  MINIO_ACCESS_KEY="minio"
  MINIO_SECRET_KEY="minio123"
else
  MINIO_ACCESS_KEY=$(oc get secret minio-secret -n ${MINIO_NAMESPACE} -o jsonpath='{.data.accesskey}' 2>/dev/null | base64 -d || echo "minio")
  MINIO_SECRET_KEY=$(oc get secret minio-secret -n ${MINIO_NAMESPACE} -o jsonpath='{.data.secretkey}' 2>/dev/null | base64 -d || echo "minio123")
  log_success "MinIO credentials retrieved"
fi

MINIO_ENDPOINT="http://minio-service.${MINIO_NAMESPACE}.svc.cluster.local:9000"

# Step 2: Get Ceph credentials
log_info "Step 2: Getting Ceph credentials..."

if ! retry_command ${MAX_RETRIES} "oc get secret noobaa-admin -n ${CEPH_NAMESPACE} &>/dev/null"; then
  log_error "Failed to access Ceph credentials"
  exit 1
fi

CEPH_ACCESS_KEY=$(oc get secret noobaa-admin -n ${CEPH_NAMESPACE} -o jsonpath='{.data.AWS_ACCESS_KEY_ID}' | base64 -d)
CEPH_SECRET_KEY=$(oc get secret noobaa-admin -n ${CEPH_NAMESPACE} -o jsonpath='{.data.AWS_SECRET_ACCESS_KEY}' | base64 -d)
CEPH_ENDPOINT="http://s3.${CEPH_NAMESPACE}.svc.cluster.local"

log_success "Ceph credentials retrieved"

# Step 3: Get existing Ceph bucket names
log_info "Step 3: Getting existing Ceph bucket names..."

CEPH_TEMPLATES_BUCKET=$(oc get objectbucketclaim km-templates -n ${CEPH_NAMESPACE} -o jsonpath='{.spec.bucketName}' 2>/dev/null || echo "")
CEPH_TENANTS_BUCKET=$(oc get objectbucketclaim km-tenants -n ${CEPH_NAMESPACE} -o jsonpath='{.spec.bucketName}' 2>/dev/null || echo "")

if [ -z "${CEPH_TEMPLATES_BUCKET}" ] || [ -z "${CEPH_TENANTS_BUCKET}" ]; then
  log_error "Required Ceph buckets (km-templates, km-tenants) not found"
  exit 1
fi

log_info "Found existing buckets:"
log_info "  km-templates: ${CEPH_TEMPLATES_BUCKET}"
log_info "  km-tenants: ${CEPH_TENANTS_BUCKET}"

# Step 4: Create mc configuration
log_info "Step 4: Creating mc configuration..."

cat <<EOF > /tmp/mc-config.json
{
  "version": "10",
  "aliases": {
    "minio": {
      "url": "${MINIO_ENDPOINT}",
      "accessKey": "${MINIO_ACCESS_KEY}",
      "secretKey": "${MINIO_SECRET_KEY}",
      "api": "s3v4",
      "path": "auto"
    },
    "ceph": {
      "url": "${CEPH_ENDPOINT}",
      "accessKey": "${CEPH_ACCESS_KEY}",
      "secretKey": "${CEPH_SECRET_KEY}",
      "api": "s3v4",
      "path": "auto"
    }
  }
}
EOF

# Create ConfigMap
if ! retry_command ${MAX_RETRIES} "oc create configmap mc-migration-config --from-file=config.json=/tmp/mc-config.json -n ${CEPH_NAMESPACE} --dry-run=client -o yaml | oc apply -f -"; then
  log_error "Failed to create mc ConfigMap"
  exit 1
fi

log_success "mc configuration created"

# Step 5: Create PVC for backups
log_info "Step 5: Creating backup PVC..."

cat <<EOF | oc apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mc-migration-backup
  namespace: ${CEPH_NAMESPACE}
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: ${PVC_SIZE}
  volumeMode: Filesystem
EOF

log_success "Backup PVC created"

# Step 6: Deploy mc migration pod
log_info "Step 6: Deploying mc migration pod..."

# Delete existing pod if present
oc delete pod mc-migration -n ${CEPH_NAMESPACE} --ignore-not-found=true --wait=true 2>/dev/null || true
sleep 5

cat <<EOF | oc apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: mc-migration
  namespace: ${CEPH_NAMESPACE}
spec:
  securityContext:
    fsGroup: 1000
    runAsUser: 1000
    runAsNonRoot: true
  containers:
  - name: mc
    image: ${MC_IMAGE}
    command: ["/bin/sh", "-c"]
    args:
    - |
      mkdir -p /tmp/.mc
      cp /config/config.json /tmp/.mc/config.json
      mkdir -p ${BACKUP_DIR}/metadata
      sleep 7200
    env:
    - name: MC_CONFIG_DIR
      value: /tmp/.mc
    - name: HOME
      value: /tmp
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop:
        - ALL
    volumeMounts:
    - name: mc-config
      mountPath: /config
      readOnly: true
    - name: backup
      mountPath: ${BACKUP_DIR}
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: mc-config
    configMap:
      name: mc-migration-config
  - name: backup
    persistentVolumeClaim:
      claimName: mc-migration-backup
  - name: tmp
    emptyDir: {}
  restartPolicy: Never
EOF

# Wait for pod
log_info "Waiting for mc pod to be ready..."
if ! retry_command ${MAX_RETRIES} "oc wait --for=condition=ready pod/mc-migration -n ${CEPH_NAMESPACE} --timeout=120s"; then
  log_error "Failed to start mc pod"
  oc describe pod mc-migration -n ${CEPH_NAMESPACE} || true
  exit 1
fi

log_success "mc pod ready"

# Step 7: Discover all buckets in MinIO
log_info "Step 7: Discovering all buckets in MinIO..."

MINIO_BUCKETS=$(oc exec -n ${CEPH_NAMESPACE} mc-migration -- \
  /bin/sh -c "mc ls minio 2>/dev/null" | awk '{print $NF}' | sed 's|/||g' | grep -v '^$' || echo "")

if [ -z "${MINIO_BUCKETS}" ]; then
  log_error "No buckets found in MinIO!"
  log_info "Debugging: Checking mc configuration..."
  oc exec -n ${CEPH_NAMESPACE} mc-migration -- /bin/sh -c "mc alias list"
  oc exec -n ${CEPH_NAMESPACE} mc-migration -- /bin/sh -c "mc ls minio"
  exit 1
fi

log_info "Found buckets in MinIO:"
echo "${MINIO_BUCKETS}" | while read bucket; do
  log_info "  - ${bucket}"
done

BUCKET_COUNT=$(echo "${MINIO_BUCKETS}" | wc -l | tr -d ' ')
log_info "Total buckets to migrate: ${BUCKET_COUNT}"

# Step 8: Backup metadata for all buckets
log_info "Step 8: Backing up bucket metadata..."

while IFS= read -r MINIO_BUCKET; do
  if [ -z "${MINIO_BUCKET}" ]; then
    continue
  fi
  
  log_info "Backing up metadata for: ${MINIO_BUCKET}"
  
  # Create backup directory
  oc exec -n ${CEPH_NAMESPACE} mc-migration -- \
    mkdir -p ${BACKUP_DIR}/metadata/${MINIO_BUCKET}
  
  # Export bucket tags directly to PVC
  log_info "  → Exporting bucket tags..."
  oc exec -n ${CEPH_NAMESPACE} mc-migration -- \
    sh -c "mc tag list --json minio/${MINIO_BUCKET} > ${BACKUP_DIR}/metadata/${MINIO_BUCKET}/tags.json 2>/dev/null || echo '{}' > ${BACKUP_DIR}/metadata/${MINIO_BUCKET}/tags.json"
  
  log_success "  ✓ Metadata backed up"
done < <(echo "${MINIO_BUCKETS}")

log_success "Metadata backup completed"

# Step 9: Migrate each bucket
log_info "Step 9: Migrating all buckets..."

MIGRATED_COUNT=0
FAILED_BUCKETS=""

while IFS= read -r MINIO_BUCKET; do
  if [ -z "${MINIO_BUCKET}" ]; then
    continue
  fi
  
  log_info "=========================================="
  log_info "Processing bucket: ${MINIO_BUCKET}"
  
  # Determine Ceph bucket name
  case "${MINIO_BUCKET}" in
    s3km-templates)
      CEPH_BUCKET="${CEPH_TEMPLATES_BUCKET}"
      log_info "  → Mapping to existing: ${CEPH_BUCKET}"
      ;;
      
    s3km-tenants)
      CEPH_BUCKET="${CEPH_TENANTS_BUCKET}"
      log_info "  → Mapping to existing: ${CEPH_BUCKET}"
      ;;
      
    s3km-pipelines)
      # Create pipelines bucket
      if ! oc get objectbucketclaim km-pipelines -n ${CEPH_NAMESPACE} &>/dev/null; then
        log_info "  → Creating km-pipelines bucket..."
        
        if retry_command ${MAX_RETRIES} "cat <<EOFPIPE | oc apply -f -
apiVersion: objectbucket.io/v1alpha1
kind: ObjectBucketClaim
metadata:
  name: km-pipelines
  namespace: ${CEPH_NAMESPACE}
spec:
  generateBucketName: km-pipelines
  storageClassName: openshift-storage.noobaa.io
EOFPIPE"; then
          sleep 10
        else
          log_error "Failed to create km-pipelines bucket"
          FAILED_BUCKETS="${FAILED_BUCKETS} ${MINIO_BUCKET}"
          MIGRATION_FAILED=1
          continue
        fi
      fi
      CEPH_BUCKET=$(oc get objectbucketclaim km-pipelines -n ${CEPH_NAMESPACE} -o jsonpath='{.spec.bucketName}')
      log_info "  → Mapping to: ${CEPH_BUCKET}"
      ;;
      
    *)
      # Model bucket or other bucket
      BUCKET_CLAIM_NAME=$(echo "${MINIO_BUCKET}" | sed 's/[^a-z0-9-]/-/g' | sed 's/^-//' | sed 's/-$//' | cut -c1-63)
      log_info "  → Detected model/custom bucket"
      log_info "  → Creating bucket claim: ${BUCKET_CLAIM_NAME}"
      
      if ! oc get objectbucketclaim ${BUCKET_CLAIM_NAME} -n ${CEPH_NAMESPACE} &>/dev/null; then
        if retry_command ${MAX_RETRIES} "cat <<EOFMODEL | oc apply -f -
apiVersion: objectbucket.io/v1alpha1
kind: ObjectBucketClaim
metadata:
  name: ${BUCKET_CLAIM_NAME}
  namespace: ${CEPH_NAMESPACE}
spec:
  generateBucketName: ${MINIO_BUCKET}
  storageClassName: openshift-storage.noobaa.io
EOFMODEL"; then
          sleep 10
        else
          log_error "Failed to create bucket ${BUCKET_CLAIM_NAME}"
          FAILED_BUCKETS="${FAILED_BUCKETS} ${MINIO_BUCKET}"
          MIGRATION_FAILED=1
          continue
        fi
      fi
      CEPH_BUCKET=$(oc get objectbucketclaim ${BUCKET_CLAIM_NAME} -n ${CEPH_NAMESPACE} -o jsonpath='{.spec.bucketName}')
      log_info "  → Created Ceph bucket: ${CEPH_BUCKET}"
      ;;
  esac
  
  # Get bucket size
  log_info "  → Checking source bucket size..."
  BUCKET_INFO=$(oc exec -n ${CEPH_NAMESPACE} mc-migration -- \
    mc du --json minio/${MINIO_BUCKET} 2>/dev/null || echo '{"size":0,"count":0}')
  
  OBJECT_COUNT=$(echo "${BUCKET_INFO}" | grep -o '"count":[0-9]*' | cut -d: -f2 || echo "0")
  BUCKET_SIZE=$(echo "${BUCKET_INFO}" | grep -o '"size":[0-9]*' | cut -d: -f2 || echo "0")
  
  log_info "  → Source: ${OBJECT_COUNT} objects, ${BUCKET_SIZE} bytes"
  
  # Backup objects to PVC (optional but recommended)
  log_info "  → Backing up objects to PVC..."
  if retry_command ${MAX_RETRIES} "oc exec -n ${CEPH_NAMESPACE} mc-migration -- \
    mc mirror --preserve --overwrite minio/${MINIO_BUCKET} ${BACKUP_DIR}/objects/${MINIO_BUCKET}"; then
    log_success "  ✓ Objects backed up to PVC"
  else
    log_warning "  ⚠ Backup to PVC failed, continuing with migration"
  fi
  
  # Migrate bucket data directly
  log_info "  → Starting direct migration to Ceph..."
  
  if retry_command ${MAX_RETRIES} "oc exec -n ${CEPH_NAMESPACE} mc-migration -- \
    mc mirror --preserve --overwrite minio/${MINIO_BUCKET} ceph/${CEPH_BUCKET}"; then
    
    # Verify migration
    log_info "  → Verifying migration..."
    DIFF_OUTPUT=$(oc exec -n ${CEPH_NAMESPACE} mc-migration -- \
      mc diff minio/${MINIO_BUCKET} ceph/${CEPH_BUCKET} 2>&1 || true)
    
    if echo "${DIFF_OUTPUT}" | grep -q "0 differences found"; then
      
      CEPH_INFO=$(oc exec -n ${CEPH_NAMESPACE} mc-migration -- \
        mc du --json ceph/${CEPH_BUCKET} 2>/dev/null || echo '{"size":0,"count":0}')
      
      CEPH_COUNT=$(echo "${CEPH_INFO}" | grep -o '"count":[0-9]*' | cut -d: -f2 || echo "0")
      CEPH_SIZE=$(echo "${CEPH_INFO}" | grep -o '"size":[0-9]*' | cut -d: -f2 || echo "0")
      
      log_success "  ✓ Migration verified: ${CEPH_COUNT} objects, ${CEPH_SIZE} bytes"
      MIGRATED_COUNT=$((MIGRATED_COUNT + 1))
    else
      log_error "  ✗ Verification failed!"
      FAILED_BUCKETS="${FAILED_BUCKETS} ${MINIO_BUCKET}"
      MIGRATION_FAILED=1
    fi
  else
    log_error "  ✗ Migration failed!"
    FAILED_BUCKETS="${FAILED_BUCKETS} ${MINIO_BUCKET}"
    MIGRATION_FAILED=1
  fi
done < <(echo "${MINIO_BUCKETS}")

# Step 10: Display summary
log_info "=========================================="
log_info "Migration Summary"
log_info "=========================================="

echo ""
log_info "Statistics:"
echo "  Total buckets: ${BUCKET_COUNT}"
echo "  Successfully migrated: ${MIGRATED_COUNT}"
echo "  Failed: $((BUCKET_COUNT - MIGRATED_COUNT))"

if [ -n "${FAILED_BUCKETS}" ]; then
  echo ""
  log_error "Failed buckets:${FAILED_BUCKETS}"
fi

echo ""
log_info "Backup Location:"
echo "  PVC: mc-migration-backup"
echo "  Metadata: ${BACKUP_DIR}/metadata/"
echo "  Objects: ${BACKUP_DIR}/objects/"

echo ""
if [ ${MIGRATION_FAILED} -eq 0 ]; then
  log_success "=========================================="
  log_success "All buckets migrated successfully!"
  log_success "=========================================="
  
  echo ""
  log_info "Next steps:"
  echo "1. Verify AI Service functionality"
  echo "2. Monitor for 24-48 hours"
  echo "3. Keep backup PVC for 30 days"
  echo "4. Uninstall MinIO after validation"
  
  echo ""
  log_info "Backup retention:"
  echo "  PVC will persist after pod deletion"
  echo "  To access backups: oc exec -it mc-migration -n ${CEPH_NAMESPACE} -- ls ${BACKUP_DIR}"
  echo "  To delete backups: oc delete pvc mc-migration-backup -n ${CEPH_NAMESPACE}"
  
  exit 0
else
  log_error "=========================================="
  log_error "Migration completed with failures!"
  log_error "=========================================="
  
  echo ""
  log_info "Troubleshooting:"
  echo "1. Check failed bucket logs above"
  echo "2. Verify network connectivity"
  echo "3. Check storage capacity in Ceph"
  echo "4. Restore from backup if needed:"
  echo "   oc exec -it mc-migration -n ${CEPH_NAMESPACE} -- mc mirror ${BACKUP_DIR}/objects/<bucket> ceph/<bucket>"
  
  exit 1
fi

