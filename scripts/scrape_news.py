#!/usr/bin/env python3
"""
Crawl REAL pickleball news from The Dink (Ghost Content API) + PPA Tour.
Usage: python scrape_news.py --output /tmp/news_raw.json
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone

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

# ── Category detection keywords ────────────────────────────────
CATEGORY_KEYWORDS = {
    "tournament": ["ppa", "mlp", "tournament", "open", "championship", "final", "semifinal", "bracket", "draw"],
    "rankings": ["ranking", "ranked", "ratings", "dupr", "standings"],
    "review": ["review", "paddle", "tested", "lab test", "score"],
    "gear": ["paddle", "gear", "equipment", "technology", "carbon fiber", "selkirk", "joola", "engage"],
    "training": ["drill", "training", "practice", "improve", "lesson", "coaching", "technique"],
    "vietnam": ["vietnam", "vietnamese", "hanoi", "ho chi minh"],
    "sea": ["southeast asia", "sea", "thailand", "singapore", "malaysia", "philippines", "bangkok"],
    "opinion": ["opinion", "analysis", "why", "should", "think", "debate"],
}


def detect_category(title: str, tags: list[str] = []) -> str:
    text = (title + " " + " ".join(tags)).lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return cat
    return "tournament"


def fetch_dink_articles(limit: int = 20) -> list[dict]:
    """Fetch real articles from The Dink via Ghost Content API."""
    log.info("Fetching from The Dink Ghost API (limit=%d)...", limit)
    try:
        resp = requests.get(
            DINK_API,
            params={
                "key": DINK_KEY,
                "limit": limit,
                "fields": "title,url,excerpt,published_at,slug",
                "include": "tags",
                "order": "published_at desc",
            },
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
            articles.append({
                "title": post["title"].strip(),
                "excerpt": (post.get("excerpt") or "").strip()[:300],
                "source_url": post.get("url", ""),
                "published_at": post.get("published_at", ""),
                "category": category,
                "source": "thedink",
                "tags": tags,
            })
        return articles
    except Exception as e:
        log.warning("Failed to fetch from The Dink: %s", e)
        return []


def fetch_ppa_rankings_news() -> list[dict]:
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
                timeout=10,
            )
            data = resp.json()
            rankings = data.get("rankings", [])
            if rankings:
                log.info("Got %d %s rankings from PPA", len(rankings), label)
                # Generate a news item about top rankings
                top_names = [r.get("player_name", "Unknown") for r in rankings[:5]]
                articles.append({
                    "title": f"PPA {label} Rankings Update: {top_names[0]} Leads",
                    "excerpt": f"Current top 5 in {label}: {', '.join(top_names)}",
                    "source_url": "https://www.ppatour.com/player-rankings/",
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="/tmp/news_raw.json")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    log.info("=== scrape_news.py starting (REAL sources) ===")

    all_articles = []

    # 1. The Dink — primary source
    dink_articles = fetch_dink_articles(args.limit)
    all_articles.extend(dink_articles)

    # 2. PPA Tour — rankings news
    ppa_articles = fetch_ppa_rankings_news()
    all_articles.extend(ppa_articles)

    # Deduplicate by title similarity
    seen_titles = set()
    unique = []
    for a in all_articles:
        key = a["title"].lower()[:50]
        if key not in seen_titles:
            seen_titles.add(key)
            unique.append(a)

    log.info("Total unique articles: %d (Dink: %d, PPA: %d)", len(unique), len(dink_articles), len(ppa_articles))

    for a in unique[:5]:
        log.info("  [%s] %s", a["category"], a["title"][:70])

    if args.output == "-":
        json.dump(unique, sys.stdout, indent=2, default=str)
    else:
        with open(args.output, "w") as f:
            json.dump(unique, f, indent=2, default=str)
        log.info("Saved to %s", args.output)

    log.info("=== scrape_news.py done ===")


if __name__ == "__main__":
    main()
