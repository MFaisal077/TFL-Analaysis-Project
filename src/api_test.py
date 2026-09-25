from datetime import datetime, timezone
import json
import os
import pandas as pd
import requests

# 1. Fetch current TfL status payload
URL = "https://api.tfl.gov.uk/Line/Mode/tube/Status"
response = requests.get(URL)
data = response.json()

now_utc = datetime.now(timezone.utc)
timestamp_str = now_utc.isoformat()

# 2. Structure current snapshot
lines_data = []
for line in data:
    status_desc = line["lineStatuses"][0]["statusSeverityDescription"]
    severity = line["lineStatuses"][0]["statusSeverity"]

    lines_data.append(
        {
            "timestamp": timestamp_str,
            "line_id": line["id"],
            "line_name": line["name"],
            "status": status_desc,
            "severity": severity,
            "is_disrupted": 1 if severity != 10 else 0,  # 10 = Good Service
        }
    )

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# -------------------------------------------------------------
# A. PERSISTENT HISTORICAL LOG (Append-only CSV)
# -------------------------------------------------------------
history_file = "data/tfl_status_history.csv"
df_new = pd.DataFrame(lines_data)

if not os.path.exists(history_file):
    # First time run: create CSV with headers
    df_new.to_csv(history_file, index=False)
else:
    # Append to existing CSV without writing headers again
    df_new.to_csv(history_file, mode="a", header=False, index=False)

# -------------------------------------------------------------
# B. LATEST SNAPSHOT FILE (Overwrite for Live UI Tab)
# -------------------------------------------------------------
latest_payload = {"fetched_at": timestamp_str, "lines": lines_data}

with open("data/live_status.json", "w") as f:
    json.dump(latest_payload, f, indent=2)

print(
    f"[{timestamp_str}] Successfully appended {len(lines_data)} lines to history log."
)