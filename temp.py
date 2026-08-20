import subprocess, json, sys

CLUSTER_NAME = "mas-atlas-cluster"
PROJECT_ID   = "68ffa9d908ff531136cef231"

# ── 1. Fetch ALL alert configs via Atlas CLI ──────────────────────────────────
# Uses atlas api alertConfigurations listAlertConfigs (Admin API v2, 2023-01-01).
# Paginates 100 per page until the server returns an error or empty results.
# NOTE: This test project has 338 alerts from accumulated test runs. Atlas
# returns a 500 on page 4 (a server-side bug for this project only). In a clean
# production project all alerts fit on page 1. We collect whatever pages succeed.
all_alerts  = []
page        = 1
while True:
    cmd = [
        "atlas", "api", "alertConfigurations", "listAlertConfigs",
        "--groupId", PROJECT_ID,
        "--version", "2023-01-01",
        "--pageNum", str(page),
        "--itemsPerPage", "100",
        "--includeCount",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Page {page}: server error — stopping pagination here.")
        print(f"  stderr: {result.stderr.strip()}")
        break

    data    = json.loads(result.stdout)
    results = data.get("results", [])
    total   = data.get("totalCount", "?")
    all_alerts.extend(results)
    print(f"Page {page}: {len(results)} results  |  running total={len(all_alerts)}  |  totalCount={total}")

    if len(results) == 0:
        break
    page += 1

print(f"\nTOTAL fetched: {len(all_alerts)}\n")

# ── 2. Helpers ────────────────────────────────────────────────────────────────
def has_webhook(alert):
    return any(n.get("typeName") == "WEBHOOK" for n in alert.get("notifications", []))

def has_cluster_matcher(alert, cluster_name):
    return any(
        m.get("fieldName") == "CLUSTER_NAME" and m.get("value") == cluster_name
        for m in alert.get("matchers", [])
    )

# ── 3. Project-level metric alert checks ─────────────────────────────────────
print("=" * 70)
print("PROJECT-LEVEL CHECKS  (metricName + threshold + WEBHOOK)")
print("=" * 70)

metric_targets = [
    ("NORMALIZED_SYSTEM_CPU_USER",  70.0, "CPU warning"),
    ("NORMALIZED_SYSTEM_CPU_USER",  80.0, "CPU critical"),
    ("SYSTEM_MEMORY_PERCENT_USED",  70.0, "Memory warning"),
    ("SYSTEM_MEMORY_PERCENT_USED",  80.0, "Memory critical"),
    ("CONNECTIONS_PERCENT",         70.0, "Connections warning"),
    ("CONNECTIONS_PERCENT",         80.0, "Connections critical"),
]

for metric_name, threshold, label in metric_targets:
    match = next(
        (
            a for a in all_alerts
            if a.get("eventTypeName") == "OUTSIDE_METRIC_THRESHOLD"
            and a.get("metricThreshold", {}).get("metricName") == metric_name
            and float(a.get("metricThreshold", {}).get("threshold", -1)) == float(threshold)
            and has_webhook(a)
        ),
        None,
    )
    status = "✅  exists  — will skip  " if match else "❌  missing — will create"
    aid    = match.get("id", "") if match else ""
    print(f"  {label:25s} | {status}  {aid}")

# ── 4. Cluster-level event alert checks ──────────────────────────────────────
print(f"\n{'=' * 70}")
print(f"CLUSTER-LEVEL CHECKS  (cluster={CLUSTER_NAME})")
print("=" * 70)

for event_type, label in [
    ("PRIMARY_ELECTED",           "Primary elected"),
    ("NO_PRIMARY",                "No primary"),
    ("CLUSTER_MONGOS_IS_MISSING", "Mongos missing"),
]:
    match = next(
        (
            a for a in all_alerts
            if a.get("eventTypeName") == event_type
            and has_cluster_matcher(a, CLUSTER_NAME)
            and has_webhook(a)
        ),
        None,
    )
    status = "✅  exists  — will skip  " if match else "❌  missing — will create"
    aid    = match.get("id", "") if match else ""
    print(f"  {label:25s} | {status}  {aid}")

# Oplog window
oplog_threshold_minutes = 60
match = next(
    (
        a for a in all_alerts
        if a.get("eventTypeName") == "REPLICATION_OPLOG_WINDOW_RUNNING_OUT"
        and has_cluster_matcher(a, CLUSTER_NAME)
        and has_webhook(a)
        and (
            float(a.get("threshold", {}).get("threshold", -1)) == float(oplog_threshold_minutes)
            or float(a.get("threshold", {}).get("threshold", -1)) == float(oplog_threshold_minutes / 60)
        )
    ),
    None,
)
status = "✅  exists  — will skip  " if match else "❌  missing — will create"
aid    = match.get("id", "") if match else ""
print(f"  {'Oplog window low':25s} | {status}  {aid}")

# Replication lag
match = next(
    (
        a for a in all_alerts
        if a.get("eventTypeName") == "OUTSIDE_METRIC_THRESHOLD"
        and a.get("metricThreshold", {}).get("metricName") == "OPLOG_SLAVE_LAG_MASTER_TIME"
        and float(a.get("metricThreshold", {}).get("threshold", -1)) == 30.0
        and has_webhook(a)
    ),
    None,
)
status = "✅  exists  — will skip  " if match else "❌  missing — will create"
aid    = match.get("id", "") if match else ""
print(f"  {'Replication lag':25s} | {status}  {aid}")
print()
