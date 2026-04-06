#!/usr/bin/env python3
"""
Auto-submit URLs to Google, Bing, and IndexNow for indexing.

Usage:
    python google_indexer.py --submit-sitemap
    python google_indexer.py --submit-url https://picklrlab.com/news/some-slug
    python google_indexer.py --submit-all-new
"""

import argparse
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import requests
from supabase import create_client

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SITE_URL = "https://picklrlab.com"
SITEMAP_URL = "%s/sitemap.xml" % SITE_URL

# IndexNow key — generate once and store
INDEXNOW_KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".indexnow_key")
INDEXNOW_API = "https://api.indexnow.org/indexnow"

# Search engine ping URLs
GOOGLE_PING = "https://www.google.com/ping"
BING_PING = "https://www.bing.com/ping"


# ---------------------------------------------------------------------------
# IndexNow Key Management
# ---------------------------------------------------------------------------
def get_or_create_indexnow_key() -> str:
    """Get existing IndexNow key or generate a new one."""
    if os.path.exists(INDEXNOW_KEY_FILE):
        with open(INDEXNOW_KEY_FILE, "r") as f:
            key = f.read().strip()
            if key:
                return key

    # Generate a new key
    key = uuid.uuid4().hex
    with open(INDEXNOW_KEY_FILE, "w") as f:
        f.write(key)
    log.info("Generated new IndexNow key: %s", key)
    log.info("IMPORTANT: You must place a file named '%s.txt' at %s/%s.txt", key, SITE_URL, key)
    log.info("The file should contain just the key: %s", key)
    return key


# ---------------------------------------------------------------------------
# Supabase
# ---------------------------------------------------------------------------
def get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        log.error("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY env vars")
        sys.exit(1)
    return create_client(url, key)


# ---------------------------------------------------------------------------
# Submission Methods
# ---------------------------------------------------------------------------
def ping_sitemap_google() -> bool:
    """Ping Google with sitemap URL."""
    try:
        resp = requests.get(
            GOOGLE_PING,
            params={"sitemap": SITEMAP_URL},
            timeout=10,
        )
        log.info("Google sitemap ping: HTTP %d", resp.status_code)
        return resp.status_code == 200
    except Exception as exc:
        log.error("Google ping failed: %s", exc)
        return False


def ping_sitemap_bing() -> bool:
    """Ping Bing with sitemap URL."""
    try:
        resp = requests.get(
            BING_PING,
            params={"sitemap": SITEMAP_URL},
            timeout=10,
        )
        log.info("Bing sitemap ping: HTTP %d", resp.status_code)
        return resp.status_code == 200
    except Exception as exc:
        log.error("Bing ping failed: %s", exc)
        return False


def submit_indexnow(urls: List[str]) -> bool:
    """Submit URLs via IndexNow API (works with Bing, Yandex, Seznam, Naver)."""
    if not urls:
        log.info("No URLs to submit to IndexNow")
        return True

    key = get_or_create_indexnow_key()

    payload = {
        "host": "picklrlab.com",
        "key": key,
        "keyLocation": "%s/%s.txt" % (SITE_URL, key),
        "urlList": urls,
    }

    try:
        resp = requests.post(
            INDEXNOW_API,
            json=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=15,
        )
        log.info("IndexNow submission: HTTP %d for %d URLs", resp.status_code, len(urls))

        if resp.status_code in (200, 202):
            log.info("IndexNow accepted %d URLs", len(urls))
            return True
        elif resp.status_code == 422:
            log.warning("IndexNow rejected URLs (key validation issue). "
                        "Ensure %s/%s.txt exists on your server.", SITE_URL, key)
            return False
        else:
            log.warning("IndexNow returned HTTP %d: %s", resp.status_code, resp.text[:200])
            return False

    except Exception as exc:
        log.error("IndexNow submission failed: %s", exc)
        return False


def submit_single_url(url: str):
    """Submit a single URL to all search engines."""
    log.info("Submitting URL: %s", url)

    # 1. IndexNow (most effective for Bing/Yandex)
    submit_indexnow([url])

    # 2. Ping sitemap (triggers recrawl)
    ping_sitemap_google()
    ping_sitemap_bing()

    log.info("Done submitting: %s", url)


def submit_all_new():
    """Submit all articles published in the last 24 hours."""
    sb = get_supabase()

    cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()

    try:
        result = (
            sb.table("articles")
            .select("slug, title, published_at")
            .gte("published_at", cutoff)
            .order("published_at", desc=True)
            .execute()
        )
        articles = result.data
    except Exception as exc:
        log.error("Failed to fetch recent articles: %s", exc)
        return

    if not articles:
        log.info("No articles published in the last 24 hours")
        return

    log.info("Found %d articles from last 24h:", len(articles))

    urls = []
    for article in articles:
        url = "%s/news/%s" % (SITE_URL, article["slug"])
        urls.append(url)
        log.info("  - %s (%s)", article["title"][:50], article["published_at"][:10])

    # Submit all at once to IndexNow
    submit_indexnow(urls)

    # Also ping sitemaps
    ping_sitemap_google()
    ping_sitemap_bing()

    log.info("Submitted %d URLs to search engines", len(urls))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Submit PicklrLab URLs to search engines")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--submit-sitemap", action="store_true", help="Ping Google & Bing with sitemap")
    group.add_argument("--submit-url", type=str, help="Submit a specific URL")
    group.add_argument("--submit-all-new", action="store_true", help="Submit all articles from last 24h")
    group.add_argument("--show-key", action="store_true", help="Show IndexNow key and setup instructions")
    args = parser.parse_args()

    log.info("=== google_indexer.py starting ===")

    if args.submit_sitemap:
        log.info("Pinging search engines with sitemap: %s", SITEMAP_URL)
        g = ping_sitemap_google()
        b = ping_sitemap_bing()
        log.info("Results — Google: %s, Bing: %s", "OK" if g else "FAIL", "OK" if b else "FAIL")

    elif args.submit_url:
        submit_single_url(args.submit_url)

    elif args.submit_all_new:
        submit_all_new()

    elif args.show_key:
        key = get_or_create_indexnow_key()
        print("\nIndexNow Key: %s" % key)
        print("\nSetup instructions:")
        print("1. Create a file on your server: %s/%s.txt" % (SITE_URL, key))
        print("2. The file should contain just the key: %s" % key)
        print("3. Verify it's accessible: curl %s/%s.txt" % (SITE_URL, key))
        print("\nThis enables Bing, Yandex, Seznam, and Naver to instantly discover new content.")

    log.info("=== google_indexer.py done ===")


if __name__ == "__main__":
    main()
