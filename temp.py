import subprocess, json, sys

CLUSTER_NAME = "mas-atlas-cluster"
PROJECT_ID   = "68ffa9d908ff531136cef231"

# ── 1. Fetch ALL alert configs — loop until empty page ───────────────────────
all_alerts = []
page = 1
while True:
    cmd = [
        "atlas", "api", "alertConfigurations", "listAlertConfigs",
        "--groupId", PROJECT_ID,
        "--version", "2023-01-01",
        "--pageNum", str(page),
        "--itemsPerPage", "100",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Hard stop on CLI error (auth failure, network issue, bad project ID, etc.)
    if result.returncode != 0:
        print(f"ERROR: Atlas CLI failed on page {page} — cannot proceed.")
        print(f"  stderr: {result.stderr.strip()}")
        print("  Ensure you are logged in: atlas auth login")
        sys.exit(1)

    data    = json.loads(result.stdout)
    results = data.get("results", [])
    all_alerts.extend(results)
    print(f"Page {page}: {len(results)} results  |  running total={len(all_alerts)}  |  totalCount={data.get('totalCount','?')}")

    if len(results) == 0:
        break
    page += 1

print(f"\nTOTAL fetched: {len(all_alerts)}")
if len(all_alerts) == 0:
    print("Note: No existing alert configs found — all alerts will be created.\n")
else:
    print()

# ── 2. Helpers ────────────────────────────────────────────────────────────────
def has_webhook(alert):
    return any(n.get("typeName") == "WEBHOOK" for n in alert.get("notifications", []))

def has_cluster_matcher(alert, cluster_name):
    return any(
        m.get("fieldName") == "CLUSTER_NAME" and m.get("value") == cluster_name
        for m in alert.get("matchers", [])
    )

def get_existing_metric_alert(metric_name):
    """Find existing alert by eventTypeName + metricName + WEBHOOK (no threshold check)."""
    return next(
        (
            a for a in all_alerts
            if a.get("eventTypeName") == "OUTSIDE_METRIC_THRESHOLD"
            and a.get("metricThreshold", {}).get("metricName") == metric_name
            and has_webhook(a)
        ),
        None,
    )

# ── 3. Project-level metric alert checks (create or update) ──────────────────
print("=" * 70)
print("PROJECT-LEVEL CHECKS  (eventTypeName + metricName + WEBHOOK)")
print("=" * 70)

for metric_name, threshold, label in [
    ("NORMALIZED_SYSTEM_CPU_USER",  70.0, "CPU warning"),
    ("NORMALIZED_SYSTEM_CPU_USER",  80.0, "CPU critical"),
    ("SYSTEM_MEMORY_PERCENT_USED",  70.0, "Memory warning"),
    ("SYSTEM_MEMORY_PERCENT_USED",  80.0, "Memory critical"),
    ("CONNECTIONS_PERCENT",         70.0, "Connections warning"),
    ("CONNECTIONS_PERCENT",         80.0, "Connections critical"),
]:
    match = get_existing_metric_alert(metric_name)

    if not match:
        status = "❌  missing         — will create"
        aid    = ""
    else:
        existing_threshold = float(match.get("metricThreshold", {}).get("threshold", -1))
        if existing_threshold == float(threshold):
            status = "✅  exists, same threshold — will skip  "
        else:
            status = f"⚠️   exists, threshold {existing_threshold} → {threshold} — will update"
        aid = match.get("id", "")

    print(f"  {label:25s} | {status}  {aid}")

# ── 4. Cluster-level event alert checks ──────────────────────────────────────
print(f"\n{'=' * 70}")
print(f"CLUSTER-LEVEL CHECKS  (eventTypeName + CLUSTER_NAME={CLUSTER_NAME} + WEBHOOK)")
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

# Oplog window — LESS_THAN threshold, sent as 60 MINUTES
# Atlas may normalise back to 1 HOURS — accept both
match = next(
    (
        a for a in all_alerts
        if a.get("eventTypeName") == "REPLICATION_OPLOG_WINDOW_RUNNING_OUT"
        and has_cluster_matcher(a, CLUSTER_NAME)
        and has_webhook(a)
        and (
            float(a.get("threshold", {}).get("threshold", -1)) == 60.0
            or float(a.get("threshold", {}).get("threshold", -1)) == 1.0
        )
    ),
    None,
)
status = "✅  exists  — will skip  " if match else "❌  missing — will create"
aid    = match.get("id", "") if match else ""
print(f"  {'Oplog window low':25s} | {status}  {aid}")

# Replication lag — project-scoped metric alert, no cluster matcher
match = get_existing_metric_alert("OPLOG_SLAVE_LAG_MASTER_TIME")
if not match:
    status = "❌  missing         — will create"
    aid    = ""
else:
    existing_threshold = float(match.get("metricThreshold", {}).get("threshold", -1))
    if existing_threshold == 30.0:
        status = "✅  exists, same threshold — will skip  "
    else:
        status = f"⚠️   exists, threshold {existing_threshold} → 30.0 — will update"
    aid = match.get("id", "")
print(f"  {'Replication lag':25s} | {status}  {aid}")
print()

# ── 5. TEST: PUT to update an existing alert's threshold ─────────────────────
# Picks the CPU warning alert at threshold 70 specifically,
# updates it to 72 (test value) via curl digest, then confirms.
# After confirming, run again with NEW_THRESHOLD=70 to revert.

NEW_THRESHOLD = 72   # ← change to 70 to revert after testing

print("=" * 70)
print(f"PUT TEST — update CPU warning (threshold=70) → {NEW_THRESHOLD}")
print("=" * 70)

# Pick specifically the alert with threshold 70 (not just any CPU alert)
test_alert = next(
    (
        a for a in all_alerts
        if a.get("eventTypeName") == "OUTSIDE_METRIC_THRESHOLD"
        and a.get("metricThreshold", {}).get("metricName") == "NORMALIZED_SYSTEM_CPU_USER"
        and float(a.get("metricThreshold", {}).get("threshold", -1)) == 70.0
        and has_webhook(a)
    ),
    None,
)

if not test_alert:
    print("  CPU warning alert (threshold=70) not found — cannot test PUT")
else:
    alert_id = test_alert["id"]
    print(f"  Alert ID : {alert_id}")
    print(f"  Current threshold: {test_alert['metricThreshold']['threshold']}")

    # Build the full body — Atlas PUT requires ALL fields, not just the changed one
    put_body = {
        "eventTypeName": test_alert["eventTypeName"],
        "enabled": test_alert["enabled"],
        "metricThreshold": {
            "metricName": test_alert["metricThreshold"]["metricName"],
            "operator": test_alert["metricThreshold"]["operator"],
            "threshold": NEW_THRESHOLD,
            "units": test_alert["metricThreshold"]["units"],
            "mode": test_alert["metricThreshold"]["mode"],
        },
        "notifications": test_alert["notifications"],
    }

    # Write body to a temp file — atlas api --file requires a file path
    import tempfile, os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(put_body, f)
        tmp_path = f.name

    cmd = [
        "atlas", "api", "alertConfigurations", "updateAlertConfig",
        "--groupId", PROJECT_ID,
        "--alertConfigId", alert_id,
        "--version", "2023-01-01",
        "--file", tmp_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    os.unlink(tmp_path)
    if result.returncode != 0:
        print(f"  PUT failed: {result.stderr.strip()}")
    else:
        updated = json.loads(result.stdout)
        if "error" in updated:
            print(f"  PUT failed: {updated.get('detail', updated.get('error'))}")
        else:
            new_threshold = updated.get("metricThreshold", {}).get("threshold")
            print(f"  PUT succeeded — new threshold: {new_threshold}")
            if float(new_threshold) == float(NEW_THRESHOLD):
                print("  ✅ Update confirmed")
            else:
                print("  ❌ Unexpected threshold value after PUT")
