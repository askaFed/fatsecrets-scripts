#!/usr/bin/env python3
import os
import json
import requests
from pathlib import Path
import re

from dotenv import load_dotenv

load_dotenv()

# ======== CONFIGURATION ========
GRAFANA_URL = os.getenv("GRAFANA_URL")
API_KEY = os.getenv("GRAFANA_API_KEY")
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./dashboards"))
# ===============================

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}


def fetch_all_dashboards():
    """Fetch the list of all dashboards."""
    url = f"{GRAFANA_URL}/api/search?type=dash-db&limit=5000"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


def mask_apitokens(data):
    links = data.get("dashboard", {}).get("links", [])
    for link in links:
        url = link.get("url")
        if url:
            masked_url = re.sub(r"([?&]apitoken=)[^\"&]+", r"\1******", url)
            link["url"] = masked_url
    return data

def export_dashboard(uid, title):
    """Export a single dashboard by UID."""
    url = f"{GRAFANA_URL}/api/dashboards/uid/{uid}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    dashboard = mask_apitokens(response.json())

    # Sanitize title for filesystem
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)
    filepath = OUTPUT_DIR / f"{safe_title}.json"

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(dashboard, f, ensure_ascii=False, indent=2)

    print(f"✅ Exported: {filepath}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("📡 Fetching dashboards...")
    dashboards = fetch_all_dashboards()

    if not dashboards:
        print("⚠️  No dashboards found.")
        return

    for item in dashboards:
        uid = item.get("uid")
        title = item.get("title", "unnamed_dashboard")

        # Skip dashboards containing "Preview" in the title (case-insensitive)
        if "preview" in title.lower():
            print(f"⏭️  Skipped (preview): {title}")
            continue

        try:
            export_dashboard(uid, title)
        except Exception as e:
            print(f"❌ Failed to export {title}: {e}")

    print(f"\n🎉 Export complete! Files saved to: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
