import re
import os
import time
from datetime import datetime, timedelta
from dateutil import parser as dateparser
import requests
from bs4 import BeautifulSoup
from clients import ensure_bucket_exists, object_exists, upload_to_s3

# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------
member_journal_base = "https://foods.fatsecret.com/Default.aspx"
member_id = "81731212"
out_dir = "./fatsecret_images"
pages_to_scan = 10
delay_between_requests = 1.0
DAYS_LIMIT = 5

S3_REGION = "us-east-1"           # MinIO ignores this, but boto3 needs it
S3_PREFIX = "uploads"            # optional path prefix inside bucket
S3_BUCKET = "fatsecret"            # optional path prefix inside bucket

# ---------------------------------------------------------------------
COOKIES = {}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
}

os.makedirs(out_dir, exist_ok=True)
uuid_regex = re.compile(
    r"/food/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})"
)

cutoff = datetime.now() - timedelta(days=DAYS_LIMIT)
print(f"📅 Downloading only entries newer than {cutoff.date()}")

# ---------------------------------------------------------------------
# HTTP SESSION
# ---------------------------------------------------------------------
session = requests.Session()
session.headers.update(HEADERS)
if COOKIES:
    session.cookies.update(COOKIES)

# ---------------------------------------------------------------------
# STEP 1: PARSE JOURNAL PAGES AND COLLECT (uuid, post_date)
# ---------------------------------------------------------------------
found = {}  # uuid -> post_date
date_limit_reached = False

for pg in range(0, pages_to_scan):
    if date_limit_reached:
        print(f"⚠️ Date limit reached. Won't move further: page {pg} is not loaded")
        break

    params = {"pa": "memn", "pg": str(pg), "id": member_id}
    resp = session.get(member_journal_base, params=params, timeout=30)
    print("Fetched", resp.url, "status", resp.status_code)

    if resp.status_code != 200:
        print(f"page {pg} returned {resp.status_code} — stopping")
        break

    soup = BeautifulSoup(resp.text, "html.parser")

    # Each <tr> block represents a journal entry
    for tr in soup.find_all("tr"):
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

        if post_date < cutoff:
            print(f"⏭️ Skipping {post_date.date()} (older than cutoff)")
            date_limit_reached = True
            break

        for m in uuid_regex.finditer(str(tr)):
            uuid = m.group(1)
            found[uuid] = post_date.date().isoformat()

    print(f"Page {pg}: found {len(found)} unique uuids so far")
    time.sleep(delay_between_requests)

# ---------------------------------------------------------------------
# STEP 2: ENSURE S3 BUCKET EXISTS
# ---------------------------------------------------------------------
ensure_bucket_exists(S3_BUCKET)

# ---------------------------------------------------------------------
# STEP 3: STREAM IMAGES DIRECTLY TO S3 UNDER post_date PREFIX
# ---------------------------------------------------------------------
suff = "_original.jpg"
uploaded = 0

for uuid, post_date_str in sorted(found.items()):
    img_url = f"https://m.ftscrt.com/food/{uuid}{suff}"
    s3_key = f"{S3_PREFIX}/post_date={post_date_str}/{uuid}{suff}"

    # Skip if already exists
    if object_exists(s3_key):
        print(f"🟡 Already exists on S3: {s3_key}")
        continue

    try:
        with session.get(img_url, stream=True, timeout=30) as r:
            if r.status_code == 200:
                if upload_to_s3(r.raw, s3_key, extra_args={"ContentType": "image/jpeg"}):
                    print(f"✅ Uploaded {uuid} ({post_date_str}) → {s3_key}")
                    uploaded += 1
            else:
                print(f"⚠️ Skipped (status {r.status_code}): {img_url}")
    except Exception as e:
        print(f"❌ Error uploading {img_url}: {e}")
        continue

    time.sleep(delay_between_requests)

print(f"\n✅ Done. Uploaded {uploaded}/{len(found)} images (last {DAYS_LIMIT} days).")
