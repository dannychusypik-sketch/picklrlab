#!/usr/bin/env python3
"""
Basic backlink and SEO audit tool for PicklrLab.

Usage:
    python backlink_checker.py --audit
    python backlink_checker.py --check-index
    python backlink_checker.py --check-links
"""

import argparse
import logging
import re
import sys
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests

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
USER_AGENT = "PicklrLab-SEO-Checker/1.0 (+https://picklrlab.com)"

HEADERS = {
    "User-Agent": USER_AGENT,
}


# ---------------------------------------------------------------------------
# Sitemap parsing
# ---------------------------------------------------------------------------
def fetch_sitemap_urls() -> List[str]:
    """Fetch all URLs from the sitemap."""
    log.info("Fetching sitemap: %s", SITEMAP_URL)
    urls = []

    try:
        resp = requests.get(SITEMAP_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()

        # Parse XML
        root = ET.fromstring(resp.content)

        # Handle namespace
        ns = ""
        match = re.match(r"\{(.+?)\}", root.tag)
        if match:
            ns = match.group(1)

        if ns:
            loc_tag = "{%s}loc" % ns
            url_tag = "{%s}url" % ns
            sitemap_tag = "{%s}sitemap" % ns
        else:
            loc_tag = "loc"
            url_tag = "url"
            sitemap_tag = "sitemap"

        # Check if this is a sitemap index
        sitemap_refs = root.findall(".//%s/%s" % (sitemap_tag, loc_tag))
        if sitemap_refs:
            log.info("Found sitemap index with %d sub-sitemaps", len(sitemap_refs))
            for ref in sitemap_refs:
                sub_url = ref.text.strip() if ref.text else ""
                if sub_url:
                    sub_urls = _fetch_sub_sitemap(sub_url)
                    urls.extend(sub_urls)
        else:
            # Direct sitemap
            for url_elem in root.findall(".//%s" % url_tag):
                loc = url_elem.find(loc_tag)
                if loc is not None and loc.text:
                    urls.append(loc.text.strip())

        log.info("Found %d URLs in sitemap", len(urls))

    except requests.RequestException as exc:
        log.error("Failed to fetch sitemap: %s", exc)
    except ET.ParseError as exc:
        log.error("Failed to parse sitemap XML: %s", exc)

    return urls


def _fetch_sub_sitemap(url: str) -> List[str]:
    """Fetch URLs from a sub-sitemap."""
    urls = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)

        ns = ""
        match = re.match(r"\{(.+?)\}", root.tag)
        if match:
            ns = match.group(1)

        loc_tag = ("{%s}loc" % ns) if ns else "loc"
        url_tag = ("{%s}url" % ns) if ns else "url"

        for url_elem in root.findall(".//%s" % url_tag):
            loc = url_elem.find(loc_tag)
            if loc is not None and loc.text:
                urls.append(loc.text.strip())
    except Exception as exc:
        log.warning("Failed to fetch sub-sitemap %s: %s", url, exc)
    return urls


# ---------------------------------------------------------------------------
# HTTP Header Checks
# ---------------------------------------------------------------------------
def check_http_headers(url: str) -> Dict:
    """Check important SEO-related HTTP headers for a URL."""
    result = {
        "url": url,
        "status": None,
        "canonical": None,
        "robots_header": None,
        "content_type": None,
        "has_hsts": False,
        "has_gzip": False,
        "issues": [],
    }

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        result["status"] = resp.status_code

        headers = resp.headers
        result["content_type"] = headers.get("Content-Type", "")
        result["robots_header"] = headers.get("X-Robots-Tag", "")
        result["has_hsts"] = "Strict-Transport-Security" in headers
        result["has_gzip"] = "gzip" in headers.get("Content-Encoding", "")

        # Check for canonical in HTML
        if "text/html" in result["content_type"]:
            canonical_match = re.search(
                r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']',
                resp.text[:5000],
            )
            if canonical_match:
                result["canonical"] = canonical_match.group(1)
            else:
                result["issues"].append("Missing canonical tag")

            # Check for meta robots
            robots_match = re.search(
                r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)["\']',
                resp.text[:5000],
            )
            if robots_match:
                robots_content = robots_match.group(1).lower()
                if "noindex" in robots_content:
                    result["issues"].append("Page has noindex directive")
                if "nofollow" in robots_content:
                    result["issues"].append("Page has nofollow directive")

        # Check for noindex in X-Robots-Tag header
        if result["robots_header"] and "noindex" in result["robots_header"].lower():
            result["issues"].append("X-Robots-Tag contains noindex")

        if resp.status_code != 200:
            result["issues"].append("Non-200 status code: %d" % resp.status_code)

        if not result["has_hsts"]:
            result["issues"].append("Missing HSTS header")

    except requests.RequestException as exc:
        result["issues"].append("Request failed: %s" % str(exc))

    return result


# ---------------------------------------------------------------------------
# Broken Link Checker
# ---------------------------------------------------------------------------
def check_broken_links(urls: List[str], max_check: int = 50) -> List[Dict]:
    """Check a list of URLs for broken links (404s)."""
    results = []
    checked = 0

    for url in urls[:max_check]:
        try:
            resp = requests.head(url, headers=HEADERS, timeout=10, allow_redirects=True)
            status = resp.status_code

            if status >= 400:
                results.append({
                    "url": url,
                    "status": status,
                    "broken": True,
                })
                log.warning("  BROKEN [%d] %s", status, url)
            else:
                log.info("  OK     [%d] %s", status, url[:80])

            checked += 1

        except requests.RequestException as exc:
            results.append({
                "url": url,
                "status": 0,
                "broken": True,
                "error": str(exc),
            })
            log.warning("  ERROR  %s — %s", url[:60], exc)
            checked += 1

    log.info("Checked %d URLs, found %d broken", checked, len(results))
    return results


# ---------------------------------------------------------------------------
# Google Index Check
# ---------------------------------------------------------------------------
def check_google_index() -> Optional[int]:
    """
    Check approximate number of indexed pages via Google search.
    Note: This uses Google search which may be rate-limited.
    For production use, prefer Google Search Console API.
    """
    query = "site:picklrlab.com"
    url = "https://www.google.com/search"

    log.info("Checking Google index for: %s", query)
    log.info("(Note: For accurate data, use Google Search Console)")

    try:
        resp = requests.get(
            url,
            params={"q": query},
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
            },
            timeout=10,
        )

        if resp.status_code == 200:
            # Try to extract result count
            match = re.search(r"About ([\d,]+) results", resp.text)
            if match:
                count = int(match.group(1).replace(",", ""))
                return count

            # Alternative pattern
            match = re.search(r"([\d,]+) results", resp.text)
            if match:
                count = int(match.group(1).replace(",", ""))
                return count

            # Check if any results at all
            if "did not match any documents" in resp.text:
                return 0

            log.warning("Could not parse result count from Google response")
            return None
        elif resp.status_code == 429:
            log.warning("Google rate-limited the request. Try again later or use Search Console.")
            return None
        else:
            log.warning("Google returned HTTP %d", resp.status_code)
            return None

    except Exception as exc:
        log.error("Google index check failed: %s", exc)
        return None


# ---------------------------------------------------------------------------
# robots.txt Check
# ---------------------------------------------------------------------------
def check_robots_txt() -> Dict:
    """Check robots.txt for SEO issues."""
    url = "%s/robots.txt" % SITE_URL
    result = {
        "url": url,
        "exists": False,
        "has_sitemap": False,
        "disallow_all": False,
        "content": "",
        "issues": [],
    }

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            result["exists"] = True
            result["content"] = resp.text[:2000]

            if "Sitemap:" in resp.text:
                result["has_sitemap"] = True
            else:
                result["issues"].append("robots.txt does not reference sitemap")

            if "Disallow: /" in resp.text and "Disallow: /api" not in resp.text:
                # Check if it's blocking everything
                lines = resp.text.split("\n")
                for line in lines:
                    stripped = line.strip()
                    if stripped == "Disallow: /":
                        result["disallow_all"] = True
                        result["issues"].append("robots.txt blocks all crawlers with 'Disallow: /'")
                        break
        else:
            result["issues"].append("robots.txt returned HTTP %d" % resp.status_code)

    except Exception as exc:
        result["issues"].append("Failed to fetch robots.txt: %s" % str(exc))

    return result


# ---------------------------------------------------------------------------
# Full Audit
# ---------------------------------------------------------------------------
def run_full_audit():
    """Run complete SEO audit."""
    print("\n" + "=" * 70)
    print("  PICKLRLAB SEO AUDIT REPORT")
    print("  Site: %s" % SITE_URL)
    print("=" * 70)

    # 1. robots.txt
    print("\n--- robots.txt ---")
    robots = check_robots_txt()
    if robots["exists"]:
        print("  Status: Found")
        print("  Has sitemap reference: %s" % ("Yes" if robots["has_sitemap"] else "No"))
        if robots["disallow_all"]:
            print("  WARNING: Blocking all crawlers!")
    else:
        print("  Status: NOT FOUND (create one!)")
    for issue in robots["issues"]:
        print("  Issue: %s" % issue)

    # 2. Sitemap
    print("\n--- Sitemap ---")
    sitemap_urls = fetch_sitemap_urls()
    if sitemap_urls:
        print("  Total URLs in sitemap: %d" % len(sitemap_urls))
        # Show a few
        for u in sitemap_urls[:5]:
            print("    - %s" % u)
        if len(sitemap_urls) > 5:
            print("    ... and %d more" % (len(sitemap_urls) - 5))
    else:
        print("  No URLs found in sitemap (or sitemap missing)")

    # 3. Homepage headers
    print("\n--- Homepage HTTP Headers ---")
    home_check = check_http_headers(SITE_URL)
    print("  Status: %s" % home_check["status"])
    print("  Canonical: %s" % (home_check["canonical"] or "Not set"))
    print("  X-Robots-Tag: %s" % (home_check["robots_header"] or "Not set"))
    print("  HSTS: %s" % ("Yes" if home_check["has_hsts"] else "No"))
    for issue in home_check["issues"]:
        print("  Issue: %s" % issue)

    # 4. Broken links
    if sitemap_urls:
        print("\n--- Broken Link Check (checking up to 50 URLs) ---")
        broken = check_broken_links(sitemap_urls, max_check=50)
        if broken:
            print("  Found %d broken URLs:" % len(broken))
            for b in broken:
                print("    [%s] %s" % (b.get("status", "ERR"), b["url"]))
        else:
            print("  All checked URLs are OK")

    # 5. Google index (optional, may be rate-limited)
    print("\n--- Google Index Status ---")
    count = check_google_index()
    if count is not None:
        print("  Approximately %d pages indexed" % count)
        if sitemap_urls:
            ratio = (count / len(sitemap_urls) * 100) if sitemap_urls else 0
            print("  Index coverage: ~%.0f%% of sitemap URLs" % ratio)
    else:
        print("  Could not determine index count (use Google Search Console for accurate data)")

    # Summary
    issues_total = len(robots["issues"]) + len(home_check["issues"])
    print("\n" + "=" * 70)
    print("  AUDIT COMPLETE")
    print("  Sitemap URLs: %d" % len(sitemap_urls))
    print("  Issues found: %d" % issues_total)
    if issues_total == 0:
        print("  Status: LOOKING GOOD")
    else:
        print("  Status: NEEDS ATTENTION — fix the issues above")
    print("=" * 70 + "\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="SEO audit tool for PicklrLab")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--audit", action="store_true", help="Run full SEO audit")
    group.add_argument("--check-index", action="store_true", help="Check Google index status")
    group.add_argument("--check-links", action="store_true", help="Check sitemap URLs for broken links")
    group.add_argument("--check-headers", type=str, metavar="URL", help="Check HTTP headers for a specific URL")
    args = parser.parse_args()

    if args.audit:
        run_full_audit()
    elif args.check_index:
        count = check_google_index()
        if count is not None:
            print("Google index: ~%d pages for picklrlab.com" % count)
        else:
            print("Could not determine. Use Google Search Console for accurate data.")
    elif args.check_links:
        urls = fetch_sitemap_urls()
        if urls:
            broken = check_broken_links(urls)
            if broken:
                print("\nBroken URLs:")
                for b in broken:
                    print("  [%s] %s" % (b.get("status", "ERR"), b["url"]))
            else:
                print("\nAll URLs OK!")
        else:
            print("No URLs found in sitemap")
    elif args.check_headers:
        result = check_http_headers(args.check_headers)
        print("\nHTTP Header Check: %s" % result["url"])
        print("  Status: %s" % result["status"])
        print("  Canonical: %s" % (result["canonical"] or "Not set"))
        print("  Robots: %s" % (result["robots_header"] or "Not set"))
        print("  HSTS: %s" % result["has_hsts"])
        for issue in result["issues"]:
            print("  Issue: %s" % issue)


if __name__ == "__main__":
    main()
