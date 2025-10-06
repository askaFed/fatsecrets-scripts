import re
import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timedelta
from dateutil import parser as dateparser
import boto3
from botocore.client import Config

# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------
member_journal_base = "https://foods.fatsecret.com/Default.aspx"
member_id = "81731212"
out_dir = "./fatsecret_images"
pages_to_scan = 1
delay_between_requests = 10.0
DAYS_LIMIT = 7

# --- S3 CONFIG ---
S3_ENDPOINT = "http://192.168.1.136:9000"
S3_BUCKET = "fatsecret"           # create beforehand if doesn’t exist
AWS_ACCESS_KEY = ""
AWS_SECRET_KEY = ""

S3_REGION = "us-east-1"           # MinIO ignores this, but boto3 needs it
S3_PREFIX = "uploads/"            # optional path prefix inside bucket

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
print(f"Downloading only entries newer than: {cutoff.date()}")

# ---------------------------------------------------------------------
# HTTP SESSION
# ---------------------------------------------------------------------
session = requests.Session()
session.headers.update(HEADERS)
if COOKIES:
    session.cookies.update(COOKIES)

found = set()

# ---------------------------------------------------------------------
# PARSE MEMBER JOURNAL
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
            print(f"Skipping entry from {post_date.date()} (older than cutoff)")
            continue

        for m in uuid_regex.finditer(str(tr)):
            found.add(m.group(1))

    print(f"page {pg}: found {len(found)} unique uuids so far")
    time.sleep(delay_between_requests)

# ---------------------------------------------------------------------
# S3 CLIENT
# ---------------------------------------------------------------------
s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=S3_REGION,
    config=Config(signature_version="s3v4"),
)

# Ensure bucket exists
try:
    s3.head_bucket(Bucket=S3_BUCKET)
except Exception:
    print(f"Bucket {S3_BUCKET} not found — creating...")
    s3.create_bucket(Bucket=S3_BUCKET)

# ---------------------------------------------------------------------
# DOWNLOAD AND UPLOAD
# ---------------------------------------------------------------------
suff = "_original.jpg"
uploaded = 0

for uuid in sorted(found):
    img_url = f"https://m.ftscrt.com/food/{uuid}{suff}"
    out_path = os.path.join(out_dir, f"{uuid}{suff}")
    if not os.path.exists(out_path):
        try:
            r = session.get(img_url, stream=True, timeout=30)
            if r.status_code == 200:
                with open(out_path, "wb") as f:
                    for chunk in r.iter_content(1024 * 8):
                        f.write(chunk)
                print(f"downloaded {uuid}")
            else:
                print("skipped (status):", img_url, r.status_code)
        except Exception as e:
            print("error downloading", img_url, e)
            continue
        time.sleep(0.2)

    # Upload to S3
    try:
        s3_key = f"{S3_PREFIX}{uuid}{suff}"
        s3.upload_file(out_path, S3_BUCKET, s3_key)
        print(f"uploaded to S3: s3://{S3_BUCKET}/{s3_key}")
        uploaded += 1
    except Exception as e:
        print("S3 upload failed for", out_path, ":", e)

print(f"\nDone. Uploaded {uploaded}/{len(found)} images (last {DAYS_LIMIT} days).")
