import json
import requests
from datetime import datetime, timezone

url = "https://api.tfl.gov.uk/Line/Mode/tube/Status"
response = requests.get(url, timeout=10)
response.raise_for_status()

data = response.json()
records = []
fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

for line in data:
    status_desc = (
        line["lineStatuses"][0]["statusSeverityDescription"]
        if line.get("lineStatuses")
        else "Unknown"
    )
    records.append(
        {
            "line_name": line["name"],
            "status": status_desc,
            "fetched_at": fetched_at,
        }
    )

# Save output to a JSON file
with open("live_status.json", "w") as f:
    json.dump(records, f, indent=2)

print("Saved live status snapshot!")