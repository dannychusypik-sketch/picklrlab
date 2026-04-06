#!/usr/bin/env python3
"""
MEGA Pickleball News Scraper — crawls from ALL working sources.
Primary: The Dink (Ghost Content API)
Secondary: Pickleball Kitchen (RSS), Pickleball Fire (RSS), Pickleball Effect (RSS), PPA Tour
Usage: python scrape_news.py --output /tmp/news_raw.json
"""

import argparse
import json
import logging
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Dict, List, Optional

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── The Dink — Ghost Content API (public key) ──────────────────
DINK_API = "https://thedinkpickleball.com/ghost/api/content/posts/"
DINK_KEY = "5b252543f0374235fec6fad8b5"

# ── PPA Tour AJAX API ──────────────────────────────────────────
PPA_AJAX = "https://www.ppatour.com/wp-admin/admin-ajax.php"

# ── RSS Feed Sources ──────────────────────────────────────────
RSS_SOURCES = [
    {
        "name": "pickleballkitchen",
        "label": "Pickleball Kitchen",
        "feed_url": "https://www.pickleballkitchen.com/feed/",
    },
    {
        "name": "pickleballfire",
        "label": "Pickleball Fire",
        "feed_url": "https://pickleballfire.com/feed/",
    },
    {
        "name": "pickleballeffect",
        "label": "Pickleball Effect",
        "feed_url": "https://pickleballeffect.com/feed/",
    },
]

# ── Category detection keywords ────────────────────────────────
CATEGORY_KEYWORDS = {
    "tournament": ["ppa", "mlp", "tournament", "open", "championship", "final",
                    "semifinal", "bracket", "draw", "major league"],
    "rankings": ["ranking", "ranked", "ratings", "dupr", "standings"],
    "review": ["review", "paddle", "tested", "lab test", "score", "compared"],
    "gear": ["paddle", "gear", "equipment", "technology", "carbon fiber",
             "selkirk", "joola", "engage", "franklin", "onix", "head"],
    "training": ["drill", "training", "practice", "improve", "lesson",
                  "coaching", "technique", "tips", "strategy", "shot",
                  "dink", "drop", "drive", "serve", "return", "backhand",
                  "forehand", "volley", "lob"],
    "vietnam": ["vietnam", "vietnamese", "hanoi", "ho chi minh"],
    "sea": ["southeast asia", "sea", "thailand", "singapore", "malaysia",
            "philippines", "bangkok"],
    "opinion": ["opinion", "analysis", "why", "should", "think", "debate"],
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PicklrLab/1.0)"
}


def detect_category(title, tags=None):
    # type: (str, Optional[List[str]]) -> str
    if tags is None:
        tags = []
    text = (title + " " + " ".join(tags)).lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return cat
    return "tournament"


def extract_youtube_url(html):
    # type: (str) -> Optional[str]
    """Extract first YouTube embed URL from HTML content."""
    if not html:
        return None
    # Match iframe src with youtube
    patterns = [
        r'<iframe[^>]+src=["\']([^"\']*youtube\.com/embed/[^"\']+)["\']',
        r'<iframe[^>]+src=["\']([^"\']*youtu\.be/[^"\']+)["\']',
        r'https?://(?:www\.)?youtube\.com/embed/[\w\-]+(?:\?[^"\'\s]*)?',
        r'https?://(?:www\.)?youtube\.com/watch\?v=[\w\-]+',
        r'https?://youtu\.be/[\w\-]+',
    ]
    for pat in patterns:
        match = re.search(pat, html, re.IGNORECASE)
        if match:
            url = match.group(1) if match.lastindex else match.group(0)
            # Normalize to embed URL
            video_id_match = re.search(r'(?:embed/|watch\?v=|youtu\.be/)([\w\-]+)', url)
            if video_id_match:
                return "https://www.youtube.com/embed/" + video_id_match.group(1)
            return url
    return None


def extract_first_image_from_html(html):
    # type: (str) -> Optional[str]
    """Extract first <img> src from HTML."""
    if not html:
        return None
    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def strip_html(html):
    # type: (str) -> str
    """Remove HTML tags and return plain text."""
    if not html:
        return ""
    text = re.sub(r'<[^>]+>', '', html)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ── The Dink — Ghost Content API ──────────────────────────────
def fetch_dink_articles(limit=20):
    # type: (int) -> List[Dict]
    """Fetch real articles from The Dink via Ghost Content API."""
    log.info("Fetching from The Dink Ghost API (limit=%d)...", limit)
    try:
        resp = requests.get(
            DINK_API,
            params={
                "key": DINK_KEY,
                "limit": limit,
                "fields": "title,url,excerpt,published_at,slug,feature_image,html",
                "include": "tags",
                "order": "published_at desc",
            },
            headers=HEADERS,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        posts = data.get("posts", [])
        log.info("Got %d articles from The Dink", len(posts))

        articles = []
        for post in posts:
            tags = [t.get("name", "") for t in post.get("tags", [])]
            category = detect_category(post.get("title", ""), tags)
            html_content = post.get("html", "")
            video_url = extract_youtube_url(html_content)

            articles.append({
                "title": post["title"].strip(),
                "excerpt": (post.get("excerpt") or "").strip()[:300],
                "source_url": post.get("url", ""),
                "source_image": post.get("feature_image", ""),
                "video_url": video_url,
                "published_at": post.get("published_at", ""),
                "category": category,
                "source": "thedink",
                "tags": tags,
            })
        return articles
    except Exception as e:
        log.warning("Failed to fetch from The Dink: %s", e)
        return []


# ── RSS Feed Parser ───────────────────────────────────────────
def fetch_rss_articles(source_config, limit=15):
    # type: (Dict, int) -> List[Dict]
    """Fetch articles from an RSS feed."""
    name = source_config["name"]
    feed_url = source_config["feed_url"]
    log.info("Fetching RSS from %s: %s", source_config["label"], feed_url)

    try:
        resp = requests.get(feed_url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        xml_text = resp.text
        # Some feeds have BOM or leading whitespace — strip it
        xml_text = xml_text.lstrip('\ufeff \t\n\r')

        # Parse XML
        root = ET.fromstring(xml_text)
        # Handle RSS 2.0 namespaces
        ns = {
            "content": "http://purl.org/rss/1.0/modules/content/",
            "dc": "http://purl.org/dc/elements/1.1/",
            "media": "http://search.yahoo.com/mrss/",
        }

        channel = root.find("channel")
        if channel is None:
            log.warning("No channel element in RSS from %s", name)
            return []

        items = channel.findall("item")
        log.info("Got %d items from %s RSS", len(items), source_config["label"])

        articles = []
        for item in items[:limit]:
            title_el = item.find("title")
            link_el = item.find("link")
            desc_el = item.find("description")
            pub_el = item.find("pubDate")
            content_el = item.find("content:encoded", ns)

            title = title_el.text.strip() if title_el is not None and title_el.text else ""
            link = link_el.text.strip() if link_el is not None and link_el.text else ""
            description = desc_el.text.strip() if desc_el is not None and desc_el.text else ""
            pub_date = pub_el.text.strip() if pub_el is not None and pub_el.text else ""
            content_html = content_el.text if content_el is not None and content_el.text else ""

            if not title:
                continue

            # Extract categories/tags
            cat_els = item.findall("category")
            tags = [c.text for c in cat_els if c.text]

            # Detect category from title + tags
            category = detect_category(title, tags)

            # Try to find feature image: media:content, media:thumbnail, or first img in content
            source_image = ""
            media_content = item.find("media:content", ns)
            media_thumb = item.find("media:thumbnail", ns)
            if media_content is not None:
                source_image = media_content.get("url", "")
            elif media_thumb is not None:
                source_image = media_thumb.get("url", "")
            else:
                # Try extracting first image from content:encoded or description
                source_image = extract_first_image_from_html(content_html) or \
                    extract_first_image_from_html(description) or ""

            # Extract YouTube video if present in content
            video_url = extract_youtube_url(content_html)

            # Clean excerpt
            excerpt = strip_html(description)[:300]

            # Parse publication date
            published_at = ""
            if pub_date:
                try:
                    from email.utils import parsedate_to_datetime
                    dt = parsedate_to_datetime(pub_date)
                    published_at = dt.isoformat()
                except Exception:
                    published_at = pub_date

            articles.append({
                "title": title,
                "excerpt": excerpt,
                "source_url": link,
                "source_image": source_image,
                "video_url": video_url,
                "published_at": published_at,
                "category": category,
                "source": name,
                "tags": tags,
            })

        return articles

    except Exception as e:
        log.warning("Failed to fetch RSS from %s: %s", source_config["label"], e)
        return []


# ── PPA Tour Rankings ─────────────────────────────────────────
def fetch_ppa_rankings_news():
    # type: () -> List[Dict]
    """Try to get ranking changes from PPA Tour API as news items."""
    log.info("Checking PPA Tour API for rankings data...")
    articles = []
    try:
        for division, label in [(1, "Women's Singles"), (2, "Men's Singles")]:
            resp = requests.get(
                PPA_AJAX,
                params={
                    "action": "get_rankings",
                    "division_type": division,
                    "gender": "M" if division == 2 else "F",
                    "race": "false",
                    "bracket_level_id": 2,
                    "page": 1,
                    "page_size": 10,
                },
                headers=HEADERS,
                timeout=10,
            )
            data = resp.json()
            rankings = data.get("rankings", [])
            if rankings:
                log.info("Got %d %s rankings from PPA", len(rankings), label)
                top_names = [r.get("player_name", "Unknown") for r in rankings[:5]]
                articles.append({
                    "title": "PPA %s Rankings Update: %s Leads" % (label, top_names[0]),
                    "excerpt": "Current top 5 in %s: %s" % (label, ", ".join(top_names)),
                    "source_url": "https://www.ppatour.com/player-rankings/",
                    "source_image": "",
                    "video_url": None,
                    "published_at": datetime.now(timezone.utc).isoformat(),
                    "category": "rankings",
                    "source": "ppa",
                    "tags": ["rankings", label.lower()],
                })
            else:
                log.info("PPA API returned empty for %s", label)
    except Exception as e:
        log.warning("PPA API error: %s", e)
    return articles


# ── Deduplication ─────────────────────────────────────────────
def deduplicate_articles(all_articles):
    # type: (List[Dict]) -> List[Dict]
    """Deduplicate by title similarity (first 50 chars lowercase)."""
    seen = set()
    unique = []
    for a in all_articles:
        # Normalize title for dedup
        key = re.sub(r'[^a-z0-9\s]', '', a["title"].lower())[:50].strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(a)
    return unique


# ── Main ──────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="MEGA Pickleball News Scraper — all sources"
    )
    parser.add_argument("--output", default="/tmp/news_raw.json")
    parser.add_argument("--limit", type=int, default=20,
                        help="Max articles per source")
    args = parser.parse_args()

    log.info("=== scrape_news.py MEGA starting (all sources) ===")

    all_articles = []
    source_counts = {}

    # 1. The Dink — primary source (Ghost API)
    dink_articles = fetch_dink_articles(args.limit)
    all_articles.extend(dink_articles)
    source_counts["thedink"] = len(dink_articles)

    # 2. RSS Sources — secondary
    for rss_src in RSS_SOURCES:
        rss_articles = fetch_rss_articles(rss_src, args.limit)
        all_articles.extend(rss_articles)
        source_counts[rss_src["name"]] = len(rss_articles)

    # 3. PPA Tour — rankings news
    ppa_articles = fetch_ppa_rankings_news()
    all_articles.extend(ppa_articles)
    source_counts["ppa"] = len(ppa_articles)

    # Deduplicate
    unique = deduplicate_articles(all_articles)

    # Summary
    log.info("=== Source Summary ===")
    for src, count in source_counts.items():
        log.info("  %s: %d articles", src, count)
    log.info("Total raw: %d, After dedup: %d", len(all_articles), len(unique))

    # Preview
    for a in unique[:8]:
        vid = " [VIDEO]" if a.get("video_url") else ""
        img = " [IMG]" if a.get("source_image") else ""
        log.info("  [%s] %s%s%s", a["source"], a["title"][:60], img, vid)

    # Save
    if args.output == "-":
        json.dump(unique, sys.stdout, indent=2, default=str)
    else:
        with open(args.output, "w") as f:
            json.dump(unique, f, indent=2, default=str)
        log.info("Saved %d articles to %s", len(unique), args.output)

    log.info("=== scrape_news.py MEGA done ===")


if __name__ == "__main__":
    main()
