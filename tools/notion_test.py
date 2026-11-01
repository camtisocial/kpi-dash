#!/usr/bin/env python3
"""
Patch the existing working embed with a different widget.
Usage: python3 tools/notion_test.py
"""
import os, json, requests
from dotenv import load_dotenv

load_dotenv()

TOKEN          = os.environ["NOTION_TOKEN"]
EMBED_BLOCK_ID = "376556b0-8847-8019-8cad-ed931975dd22"  # manually created, shows chart
HTML_FILE      = "v3-widgets/dist/w-annual.html"          # different widget to confirm update
# Note: no intermediate file block — upload then immediately PATCH the embed

HEADERS = {"Authorization": f"Bearer {TOKEN}", "Notion-Version": "2026-03-11"}

def step(label): print(f"\n{'─'*50}\n{label}")

# ── 1. Upload new widget ──────────────────────────────
step(f"1. Uploading {HTML_FILE}")
r = requests.post("https://api.notion.com/v1/file_uploads", headers=HEADERS,
                  json={"filename": "w-annual.html", "content_type": "text/html"})
uid      = r.json()["id"]
send_url = r.json()["upload_url"]
with open(HTML_FILE, "rb") as f:
    r2 = requests.post(send_url, headers=HEADERS,
                       files={"file": ("w-annual.html", f.read(), "text/html")})
print(f"File upload ID: {uid}  status: {r2.json().get('status')}")

# ── 2. Patch the working embed ────────────────────────
attachment_url = f"attachment:{uid}:w-annual.html"
step(f"2. Patching embed {EMBED_BLOCK_ID}")
print(f"New URL: {attachment_url}")
r = requests.patch(
    f"https://api.notion.com/v1/blocks/{EMBED_BLOCK_ID}",
    headers={**HEADERS, "Content-Type": "application/json"},
    json={"embed": {"url": attachment_url}},
)
print(f"Status: {r.status_code}")
print(f"Stored: {r.json().get('embed', {}).get('url')}")
print("\n→ Check Notion: does the embed still show a chart? (should now show Annual Volume Index)")
