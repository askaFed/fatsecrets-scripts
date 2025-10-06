import re
import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import parser as dateparser  # pip install python-dateutil

# CONFIG
member_journal_base = "https://foods.fatsecret.com/Default.aspx"
member_id = "81731212"
out_dir = "./fatsecret_images"
pages_to_scan = 1         # increase as needed
delay_between_requests = 10.0
DAYS_LIMIT = 7            # download only photos for the last X days

COOKIES = {}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
}

os.makedirs(out_dir, exist_ok=True)

uuid_regex = re.compile(
    r"/food/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"
)
cutoff = datetime.now() - timedelta(days=DAYS_LIMIT)
print(f"Downloading only entries newer than: {cutoff.date()}")

session = requests.Session()
session.headers.update(HEADERS)
if COOKIES:
    session.cookies.update(COOKIES)

found = set()

# ---------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------
for pg in range(0, pages_to_scan + 1):
    params = {"pa": "memn", "pg": str(pg), "id": member_id}
    resp = session.get(member_journal_base, params=params, timeout=30)
    print("Fetched", resp.url, "status", resp.status_code)
    open(f"page_{pg}.html", "w").write(resp.text)

    if resp.status_code != 200:
        print(f"page {pg} returned {resp.status_code} — stopping")
        break

    soup = BeautifulSoup(resp.text, "html.parser")

    # Each journal entry is in a <tr>
    for tr in soup.find_all("tr"):
        # Step 1: find the date inside <h4> -> <a>
        date_tag = tr.find("h4")
        if not date_tag:
            continue
        date_text = date_tag.get_text(strip=True)
        if not date_text:
            continue

        try:
            post_date = dateparser.parse(date_text, fuzzy=True)
        except Exception:
            continue

        # Step 2: skip old posts
        if post_date < cutoff:
            print(f"Skipping entry from {post_date.date()} (older than cutoff)")
            continue

        # Step 3: find any food UUIDs in this entry
        tr_html = str(tr)
        for m in uuid_regex.finditer(tr_html):
            found.add(m.group(1))

    print(f"page {pg}: found {len(found)} unique uuids so far")
    time.sleep(delay_between_requests)

# ---------------------------------------------------------------------
# DOWNLOAD IMAGES
# ---------------------------------------------------------------------
suff = "_original.jpg"
for uuid in sorted(found):
    img_url = f"https://m.ftscrt.com/food/{uuid}{suff}"
    out_path = os.path.join(out_dir, f"{uuid}{suff}")
    if os.path.exists(out_path):
        print("exists:", out_path)
        continue
    try:
        r = session.get(img_url, stream=True, timeout=30)
        if r.status_code == 200:
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(1024 * 8):
                    f.write(chunk)
            print(f"downloaded {uuid} ({img_url})")
        else:
            print("skipped (status):", img_url, r.status_code)
    except Exception as e:
        print("error downloading", img_url, e)
    time.sleep(0.2)

print(f"Done. Downloaded {len(found)} images (filtered for last {DAYS_LIMIT} days).")
