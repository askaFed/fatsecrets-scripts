import os
import json
import uuid
import requests
import argparse
from pathlib import Path
import sys
import subprocess

GRAFANA_URL = os.environ.get("GRAFANA_URL")
GRAFANA_API_KEY = os.environ.get("GRAFANA_API_KEY")
GRAFANA_API_TOKEN = os.environ.get("GRAFANA_API_TOKEN")
INPUT_DIR = Path(os.getenv("INPUT_DIR", "./dashboards"))


def import_dashboard(file_path, overwrite=False):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    dashboard = data.get("dashboard", data)
    meta = data.get("meta", {})

    # Always remove ID to avoid conflicts
    # dashboard.pop("id", None)


    links = dashboard.get("links", [])

    for link in links:
            url = link.get("url")
            if url and "apitoken=******" in url:
                link["url"] = url.replace("apitoken=******", f"apitoken={GRAFANA_API_TOKEN}")
                print(link["url"])

    if overwrite:
        # Keep same UID if exists, overwrite=True
        dashboard["title"] = dashboard.get("title", "Unnamed")
        uid = dashboard["uid"]
    else:
        # Create preview version
        uid = generate_uid()
        dashboard["uid"] = uid
        dashboard["title"] = f"{dashboard.get('title', 'Unnamed')} (Preview) - {uid}"

    latest_commit = get_latest_commit()

    payload = {
        "dashboard": dashboard,
        "folderId": meta.get("folderId", 0),
        "overwrite": True,
        "message": f"GIT Import - {latest_commit}"
    }

    headers = {
        "Authorization": f"Bearer {GRAFANA_API_KEY}",
        "Content-Type": "application/json"
    }

    url = f"{GRAFANA_URL.rstrip('/')}/api/dashboards/db"
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        action = "Overwritten" if overwrite else "Imported (preview)"
        title = dashboard["title"]
        print(f"✅ {action}: '{title}' from {os.path.basename(file_path)}. UUID: {uid}")
    else:
        try:
            error = response.json()
        except Exception:
            error = response.text
        print(f"❌ Failed: {os.path.basename(file_path)} — {response.status_code} — {error}")


def generate_uid():
    """Generate a random Grafana-compatible UID."""
    return uuid.uuid4().hex[:40]

def validate_env():
    if not GRAFANA_URL:
        print("❌ Environment variable GRAFANA_URL is not set.")
        sys.exit(1)
    if not GRAFANA_API_KEY:
        print("❌ Environment variable GRAFANA_API_KEY is not set.")
        sys.exit(1)


def get_latest_commit():
    """Return the latest short git commit hash."""
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
        return commit
    except Exception:
        return "unknown"


def main():
    validate_env()

    parser = argparse.ArgumentParser(description="Import Grafana dashboards via API.")
    parser.add_argument("path", nargs="?", default=INPUT_DIR, help="Path to dashboard file or directory")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing dashboards (default: False)")
    args = parser.parse_args()
    print(f"overwrite {args.overwrite}")

    path = Path(args.path)
    if path.is_dir():
        for file in sorted(path.glob("*.json")):
            import_dashboard(file, overwrite=args.overwrite)
    elif path.is_file():
        import_dashboard(path, overwrite=args.overwrite)
    else:
        print("❌ Error: path is neither file nor directory")

if __name__ == "__main__":
    main()
