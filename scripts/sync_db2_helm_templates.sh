#!/usr/bin/env bash
# =============================================================================
# sync_db2_helm_templates.sh
#
# PURPOSE:
#   Renders the latest DB2 Helm charts and applies local environment
#   customisations on top, then writes the result into the Ansible role
#   templates so they are always in sync with upstream.
#
# WHAT IT DOES:
#   1. Extracts downloaded chart .tgz files (or uses pre-extracted dirs)
#   2. Renders both charts with `helm template`
#   3. Post-processes the rendered YAML to:
#        a) Inject Jinja2 variables  ({{ db2_namespace }}, {{ db2_instance_name }})
#        b) Strip helm warning lines
#        c) Re-apply local environment customisations:
#             - imagePullSecrets: ibm-registry on ServiceAccounts & Deployments
#             - storage_class_name: spec.storage[2].spec.storageClassName
#             - META_NAMESPACE / WATCH_NAMESPACE as hardcoded Jinja2 values
#             - Retain ClusterRole/ClusterRoleBinding for ibm-usage-metering
#   4. Diffs the result against current local .j2 files
#   5. In --apply mode, replaces the local .j2 files (with .bak backup)
#
# USAGE:
#   # Dry-run — show what would change (default):
#   ./scripts/sync_db2_helm_templates.sh
#
#   # Apply changes to the Ansible role templates:
#   ./scripts/sync_db2_helm_templates.sh --apply
#
#   # Use a specific charts directory instead of .tgz files:
#   ./scripts/sync_db2_helm_templates.sh --charts-dir /path/to/charts --apply
#
# REQUIREMENTS:
#   - helm (v3+)
#   - python3
#   - diff / sed / awk
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Paths — adjust if your layout differs
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROLE_TEMPLATES="${SCRIPT_DIR}/../ibm/mas_devops/roles/db2/templates"

LOCAL_CRD_TEMPLATE="${ROLE_TEMPLATES}/crds/db2uCRDs.yml.j2"
LOCAL_OPERATOR_TEMPLATE="${ROLE_TEMPLATES}/db2_helm_operator.yml.j2"

# Chart tgz files expected alongside this script
CRD_TGZ="${SCRIPT_DIR}/db2-operator-cluster-scoped-*.tgz"
STANDALONE_TGZ="${SCRIPT_DIR}/db2-operator-standalone-*.tgz"

WORK_DIR="/tmp/db2_helm_sync_$$"

# Jinja2 substitution placeholders used during helm template
NS_PLACEHOLDER="DB2_NAMESPACE_PLACEHOLDER"
INSTANCE_PLACEHOLDER="DB2_INSTANCE_PLACEHOLDER"

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
APPLY=false
CHARTS_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply)       APPLY=true; shift ;;
    --charts-dir)  CHARTS_DIR="$2"; shift 2 ;;
    --help|-h)
      grep "^#" "$0" | grep -v "^#!/" | sed 's/^# \{0,1\}//' | \
        awk '/^USAGE/,/^REQUIREMENTS/' | head -20
      exit 0 ;;
    *) echo "ERROR: Unknown argument: $1  (use --help)"; exit 1 ;;
  esac
done

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
log()  { echo "[sync] $*"; }
info() { echo ""; echo "─────────────────────────────────────────"; echo "  $*"; echo "─────────────────────────────────────────"; }

cleanup() { rm -rf "${WORK_DIR}"; }
trap cleanup EXIT

check_dep() {
  command -v "$1" &>/dev/null || { echo "ERROR: '$1' not found in PATH."; exit 1; }
}

check_dep helm
check_dep python3
check_dep diff

mkdir -p "${WORK_DIR}"

# ---------------------------------------------------------------------------
# Step 1: Locate / extract chart directories
# ---------------------------------------------------------------------------
info "Step 1: Locating charts"

if [[ -n "${CHARTS_DIR}" ]]; then
  log "Using provided charts directory: ${CHARTS_DIR}"
  CRD_CHART="${CHARTS_DIR}/db2-operator-cluster-scoped"
  STANDALONE_CHART="${CHARTS_DIR}/db2-operator-standalone"
else
  log "Extracting .tgz files from ${SCRIPT_DIR}/"
  CRD_TGZ_FILE=$(ls ${CRD_TGZ} 2>/dev/null | sort -V | tail -1)
  STANDALONE_TGZ_FILE=$(ls ${STANDALONE_TGZ} 2>/dev/null | sort -V | tail -1)

  [[ -z "${CRD_TGZ_FILE}" ]] && { echo "ERROR: No db2-operator-cluster-scoped-*.tgz found in ${SCRIPT_DIR}"; exit 1; }
  [[ -z "${STANDALONE_TGZ_FILE}" ]] && { echo "ERROR: No db2-operator-standalone-*.tgz found in ${SCRIPT_DIR}"; exit 1; }

  log "CRD chart:        $(basename "${CRD_TGZ_FILE}")"
  log "Standalone chart: $(basename "${STANDALONE_TGZ_FILE}")"

  tar -xzf "${CRD_TGZ_FILE}"      -C "${WORK_DIR}"
  tar -xzf "${STANDALONE_TGZ_FILE}" -C "${WORK_DIR}"

  CRD_CHART="${WORK_DIR}/db2-operator-cluster-scoped"
  STANDALONE_CHART="${WORK_DIR}/db2-operator-standalone"
fi

[[ -d "${CRD_CHART}" ]]        || { echo "ERROR: Chart dir not found: ${CRD_CHART}"; exit 1; }
[[ -d "${STANDALONE_CHART}" ]] || { echo "ERROR: Chart dir not found: ${STANDALONE_CHART}"; exit 1; }

CHART_VERSION=$(grep "^version:" "${STANDALONE_CHART}/Chart.yaml" | awk '{print $2}')
log "Chart version: ${CHART_VERSION}"

# ---------------------------------------------------------------------------
# Step 2: Render charts with helm template
# ---------------------------------------------------------------------------
info "Step 2: Rendering Helm charts"

log "Rendering db2-operator-cluster-scoped..."
helm template db2-release "${CRD_CHART}" \
  --namespace "${NS_PLACEHOLDER}" \
  --include-crds \
  > "${WORK_DIR}/raw_crds.yaml"
log "  → $(wc -l < "${WORK_DIR}/raw_crds.yaml") lines"

log "Rendering db2-operator-standalone..."
helm template db2-release "${STANDALONE_CHART}" \
  --namespace "${NS_PLACEHOLDER}" \
  --set global.licenseAccept=true \
  2>/dev/null \
  > "${WORK_DIR}/raw_operator.yaml"
log "  → $(wc -l < "${WORK_DIR}/raw_operator.yaml") lines"

# ---------------------------------------------------------------------------
# Step 3: Post-process — Jinja2 substitutions + local customisations
# ---------------------------------------------------------------------------
info "Step 3: Post-processing (Jinja2 vars + local customisations)"

# --- 3a. CRD file ---
# Only substitutions needed — no structural local customisations in CRDs
sed \
  -e "s|${NS_PLACEHOLDER}|{{ db2_namespace }}|g" \
  -e "s|db2-release|{{ db2_instance_name }}|g" \
  "${WORK_DIR}/raw_crds.yaml" \
  > "${WORK_DIR}/new_crds.j2"

log "CRD post-processing complete"

# --- 3b. Operator file — Python script applies all local customisations ---
python3 - "${WORK_DIR}/raw_operator.yaml" "${WORK_DIR}/new_operator.j2" \
  "${NS_PLACEHOLDER}" "${INSTANCE_PLACEHOLDER}" << 'PYEOF'
import sys, re

src_path   = sys.argv[1]
dst_path   = sys.argv[2]
ns_ph      = sys.argv[3]
inst_ph    = sys.argv[4]
jinja_ns   = "{{ db2_namespace }}"
jinja_inst = "{{ db2_instance_name }}"

with open(src_path) as f:
    lines = f.readlines()

out = []
i = 0
while i < len(lines):
    line = lines[i]

    # ── Strip helm warning lines emitted to stdout ──────────────────────
    if line.startswith('level=INFO msg="Conflict:'):
        i += 1
        continue

    # ── Jinja2 substitutions ─────────────────────────────────────────────
    line = line.replace(ns_ph,   jinja_ns)
    line = line.replace(inst_ph, jinja_inst)
    # helm puts the release name (db2-release) in some resource names
    line = line.replace("db2-release", jinja_inst)

    # ── META_NAMESPACE / WATCH_NAMESPACE: fieldRef → hardcoded Jinja2 ───
    # Pattern: name: META_NAMESPACE or WATCH_NAMESPACE followed by valueFrom block
    if re.match(r'\s+- name: (META_NAMESPACE|WATCH_NAMESPACE)\s*$', line):
        indent = len(line) - len(line.lstrip())
        var_name = re.search(r'(META_NAMESPACE|WATCH_NAMESPACE)', line).group(1)
        out.append(line)               # keep "- name: ..."
        i += 1
        # skip the valueFrom / fieldRef / fieldPath lines (next 3 lines)
        while i < len(lines):
            peek = lines[i]
            stripped = peek.strip()
            if stripped.startswith('valueFrom') or \
               stripped.startswith('fieldRef') or \
               stripped.startswith('fieldPath'):
                i += 1
            else:
                break
        # inject "  value: ..." with matching indent
        out.append(' ' * (indent + 2) + f'value: "{jinja_ns}"\n')
        continue

    # ── storage_class_name: "" → spec.storage[2].spec.storageClassName ──
    if re.match(r'\s+storage_class_name:\s*""\s*$', line):
        line = line.replace('storage_class_name: ""',
                            'storage_class_name: spec.storage[2].spec.storageClassName')

    out.append(line)
    i += 1

content = ''.join(out)

# ── imagePullSecrets on ServiceAccounts ──────────────────────────────────
# Insert after the last label line of each SA block, before any "---" or next kind
# Strategy: after "kind: ServiceAccount" block ends (next "---"), insert imagePullSecrets
# More precisely: after the metadata block of each ServiceAccount, if not already present

def inject_sa_pull_secrets(text):
    """
    For each ServiceAccount that does NOT already have imagePullSecrets,
    append the block right after its metadata/labels section.
    """
    result = []
    in_sa = False
    has_pull_secret = False
    sa_block = []

    for line in text.splitlines(keepends=True):
        if line.strip() == '---':
            if in_sa and not has_pull_secret and sa_block:
                # inject before the closing ---
                result.extend(sa_block)
                result.append('imagePullSecrets:\n')
                result.append('- name: ibm-registry\n')
                sa_block = []
                in_sa = False
                has_pull_secret = False
                result.append(line)
            else:
                result.extend(sa_block)
                sa_block = []
                in_sa = False
                has_pull_secret = False
                result.append(line)
            continue

        if re.match(r'^kind:\s+ServiceAccount\s*$', line):
            in_sa = True

        if in_sa and 'imagePullSecrets' in line:
            has_pull_secret = True

        if in_sa:
            sa_block.append(line)
        else:
            result.append(line)

    # flush last block
    if sa_block:
        if in_sa and not has_pull_secret:
            result.extend(sa_block)
            result.append('imagePullSecrets:\n')
            result.append('- name: ibm-registry\n')
        else:
            result.extend(sa_block)

    return ''.join(result)

content = inject_sa_pull_secrets(content)

# ── imagePullSecrets on Deployments (pod spec level) ─────────────────────
# Insert after serviceAccountName line inside pod spec if not already present
def inject_deployment_pull_secrets(text):
    lines_out = []
    lines_in  = text.splitlines(keepends=True)
    i = 0
    while i < len(lines_in):
        line = lines_in[i]
        lines_out.append(line)
        # After serviceAccountName inside a Deployment pod spec
        if re.match(r'\s+serviceAccountName:', line):
            # peek ahead to see if imagePullSecrets already follows
            j = i + 1
            while j < len(lines_in) and lines_in[j].strip() == '':
                j += 1
            if j < len(lines_in) and 'imagePullSecrets' not in lines_in[j]:
                indent = len(line) - len(line.lstrip())
                lines_out.append(' ' * indent + 'imagePullSecrets:\n')
                lines_out.append(' ' * indent + '  - name: ibm-registry\n')
        i += 1
    return ''.join(lines_out)

content = inject_deployment_pull_secrets(content)

# ── Retain ClusterRole + ClusterRoleBinding for ibm-usage-metering ───────
cluster_rbac = '''---
# Source: db2-operator-standalone/charts/db2-ums-collector/charts/ibm-usage-metering/templates/clusterrole.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  labels:
    app.kubernetes.io/managed-by: kustomize
    app.kubernetes.io/name: ibm-usage-metering-operator
    component-id: ibm-usage-metering
  name: ibm-usage-metering-operator-cluster
rules:
  - apiGroups:
      - apps
    resources:
      - deployments
    verbs:
      - get
      - list
      - watch
  - apiGroups:
      - operator.ibm.com
    resources:
      - ibmservicemeterdefinitions
    verbs:
      - get
      - list
      - watch
---
# Source: db2-operator-standalone/charts/db2-ums-collector/charts/ibm-usage-metering/templates/clusterrole.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  labels:
    app.kubernetes.io/managed-by: kustomize
    app.kubernetes.io/name: ibm-usage-metering-operator
    component-id: ibm-usage-metering
  name: ibm-usage-metering-operator-cluster
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: ibm-usage-metering-operator-cluster
subjects:
  - kind: ServiceAccount
    name: ibm-usage-metering-operator
    namespace: ''' + jinja_ns + '\n'

# Insert after the configmap-state block (last ConfigMap before ClusterRole section)
insert_marker = '# Source: db2-operator-standalone/charts/db2-ums-collector/charts/ibm-usage-metering/templates/rbac.yaml'
if insert_marker in content and 'ibm-usage-metering-operator-cluster' not in content:
    content = content.replace(
        '---\n' + insert_marker,
        cluster_rbac + '---\n' + insert_marker,
        1
    )

with open(dst_path, 'w') as f:
    f.write(content)

print(f"  Operator post-processing complete → {dst_path}")
PYEOF

# ---------------------------------------------------------------------------
# Step 4: Diff
# ---------------------------------------------------------------------------
info "Step 4: Comparing against local templates"

show_diff() {
  local label="$1" local_file="$2" new_file="$3" diff_out="$4"

  if diff --unified=3 "${local_file}" "${new_file}" > "${diff_out}" 2>&1; then
    log "✓  ${label} — NO CHANGES (already up to date)"
  else
    local add del
    add=$(grep -c '^+' "${diff_out}" 2>/dev/null || echo 0)
    del=$(grep -c '^-' "${diff_out}" 2>/dev/null || echo 0)
    log "✗  ${label} — CHANGES DETECTED  (+$((add-1)) / -$((del-1)) lines)"
    log "   Preview (first 60 lines):"
    echo ""
    head -60 "${diff_out}" | sed 's/^/   /'
    echo ""
  fi
}

show_diff "db2uCRDs.yml.j2"         "${LOCAL_CRD_TEMPLATE}"      "${WORK_DIR}/new_crds.j2"     "${WORK_DIR}/diff_crds.txt"
show_diff "db2_helm_operator.yml.j2" "${LOCAL_OPERATOR_TEMPLATE}" "${WORK_DIR}/new_operator.j2" "${WORK_DIR}/diff_operator.txt"

# ---------------------------------------------------------------------------
# Step 5: Version summary
# ---------------------------------------------------------------------------
info "Step 5: Version summary"

echo "  Component                        LOCAL (current)                          UPSTREAM (v${CHART_VERSION})"
echo "  ─────────────────────────────── ──────────────────────────────────────── ────────────────────────────────────────"

show_versions() {
  local label="$1" local_f="$2" new_f="$3"
  local old_img new_img
  old_img=$(grep -m1 'image:.*db2-operator' "${local_f}" 2>/dev/null | xargs || echo "n/a")
  new_img=$(grep -m1 'image:.*db2-operator' "${new_f}"   2>/dev/null | xargs || echo "n/a")
  printf "  %-32s %-40s %s\n" "${label}" "${old_img}" "${new_img}"
}

show_versions "DB2 Operator image" "${LOCAL_OPERATOR_TEMPLATE}" "${WORK_DIR}/new_operator.j2"

OLD_UMS=$(grep -m1 'ibm-usage-metering-operator@' "${LOCAL_OPERATOR_TEMPLATE}" 2>/dev/null | xargs | cut -c1-50 || echo "n/a")
NEW_UMS=$(grep -m1 'ibm-usage-metering-operator@' "${WORK_DIR}/new_operator.j2"   2>/dev/null | xargs | cut -c1-50 || echo "n/a")
printf "  %-32s %-40s %s\n" "UMS Operator image" "${OLD_UMS}" "${NEW_UMS}"

# ---------------------------------------------------------------------------
# Step 6: Apply (optional)
# ---------------------------------------------------------------------------
if [[ "${APPLY}" == "true" ]]; then
  info "Step 6: Applying changes"

  apply_file() {
    local label="$1" local_file="$2" new_file="$3" diff_file="$4"
    if diff -q "${local_file}" "${new_file}" >/dev/null 2>&1; then
      log "  (unchanged) ${label}"
    else
      cp "${local_file}" "${local_file}.bak"
      cp "${new_file}"   "${local_file}"
      log "✓  Updated:  ${label}"
      log "   Backup:   ${local_file}.bak"
    fi
  }

  apply_file "db2uCRDs.yml.j2"          "${LOCAL_CRD_TEMPLATE}"      "${WORK_DIR}/new_crds.j2"     "${WORK_DIR}/diff_crds.txt"
  apply_file "db2_helm_operator.yml.j2" "${LOCAL_OPERATOR_TEMPLATE}" "${WORK_DIR}/new_operator.j2" "${WORK_DIR}/diff_operator.txt"

  echo ""
  log "Done. Review with:"
  log "  git diff ibm/mas_devops/roles/db2/templates/"
else
  info "Dry-run complete — no files modified"
  echo "  Run with --apply to update the local templates:"
  echo "  ./scripts/sync_db2_helm_templates.sh --apply"
fi
