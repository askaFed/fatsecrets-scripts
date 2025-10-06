import re
import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# CONFIG
member_journal_base = "https://foods.fatsecret.com/Default.aspx"     # add ?pa=...&id=...
member_id = "81731212"
out_dir = "./fatsecret_images"
pages_to_scan = 1        # how many journal pages to scan (increase as needed)
delay_between_requests = 10.0  # polite delay, seconds

COOKIES = {}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
}

os.makedirs(out_dir, exist_ok=True)

# regex to find UUID-like token inside URLs like /food/<uuid>_...
uuid_regex = re.compile(r"/food/([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})")

session = requests.Session()
session.headers.update(HEADERS)
if COOKIES:
    session.cookies.update(COOKIES)

found = set()

for pg in range(1, pages_to_scan + 1):
    params = {"pa": "memn","pg": str(pg), "id": member_id}
    resp = session.get(member_journal_base, params=params, timeout=30)
    print("Fetched", resp.url, "status", resp.status_code)
    open(f"page_{pg}.html", "w").write(resp.text)
    if resp.status_code != 200:
        print(f"page {pg} returned {resp.status_code} — stopping")
        break

    soup = BeautifulSoup(resp.text, "html.parser")

    # Method A: find any <img> tags with src or data-src pointing to m.ftscrt.com
    for img in soup.find_all("img"):
        for attr in ("src", "data-src", "data-original", "data-lazy"):
            val = img.get(attr)
            if not val:
                continue
            m = uuid_regex.search(val)
            if m:
                found.add(m.group(1))

    # Method B: find <a> tags that link to image CDN or to a public post that contains images
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # absolute/relative
        if "ftscrt.com/food" in href or "/food/" in href:
            m = uuid_regex.search(href)
            if m:
                found.add(m.group(1))

    # Method C: search the raw HTML as fallback for any /food/<uuid> appearances
    for m in uuid_regex.finditer(resp.text):
        found.add(m.group(1))

    print(f"page {pg}: found {len(found)} unique uuids so far")
    time.sleep(delay_between_requests)

# Build and download image URLs (choose _original or other suffix)
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
                for chunk in r.iter_content(1024*8):
                    f.write(chunk)
            print("downloaded:", out_path)
        else:
            print("skipped (status):", img_url, r.status_code)
    except Exception as e:
        print("error downloading", img_url, e)
    time.sleep(0.2)
