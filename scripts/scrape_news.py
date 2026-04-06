#!/usr/bin/env python3
"""
Crawl pickleball news from web sources and output as JSON.
Usage: python scrape_news.py --output /tmp/news_raw.json
"""

import argparse
import json
import logging
import random
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

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
# News sources
# ---------------------------------------------------------------------------
NEWS_SOURCES = [
    {
        "name": "The Dink",
        "url": "https://www.thedinkpickleball.com/news/",
        "selector": "article",
        "title_selector": "h2, h3",
        "link_selector": "a",
    },
    {
        "name": "Pickleball Central Blog",
        "url": "https://blog.pickleballcentral.com/",
        "selector": "article",
        "title_selector": "h2, h3",
        "link_selector": "a",
    },
]

# Category keywords for auto-detection
CATEGORY_KEYWORDS = {
    "tournament": ["tournament", "open", "championship", "finals", "bracket", "ppa", "mlp", "app tour"],
    "player_news": ["signs", "contract", "injury", "retire", "comeback", "sponsor", "deal"],
    "gear": ["paddle", "shoe", "gear", "equipment", "review", "ball", "court"],
    "strategy": ["tips", "strategy", "drill", "technique", "how to", "improve", "lesson"],
    "community": ["community", "growth", "park", "facility", "league", "club"],
    "scores": ["score", "result", "wins", "defeats", "beats", "match", "upset"],
}

# Fallback mock headlines
MOCK_NEWS = [
    {
        "title": "Ben Johns Dominates PPA Masters with Flawless Singles Run",
        "source_url": "https://example.com/ppa-masters-johns",
        "source_name": "Mock Source",
        "snippet": "Ben Johns went undefeated through the entire singles bracket at the PPA Masters, dropping only two games across five matches.",
    },
    {
        "title": "Anna Leigh Waters Signs Record-Breaking Sponsorship Deal",
        "source_url": "https://example.com/waters-sponsor",
        "source_name": "Mock Source",
        "snippet": "19-year-old Anna Leigh Waters has signed the largest sponsorship deal in pickleball history with a major sports brand.",
    },
    {
        "title": "New MLP Expansion Teams Announced for 2026 Season",
        "source_url": "https://example.com/mlp-expansion",
        "source_name": "Mock Source",
        "snippet": "Major League Pickleball reveals four new expansion teams as the league continues its rapid growth trajectory.",
    },
    {
        "title": "Top 5 Paddle Technologies Changing the Game in 2026",
        "source_url": "https://example.com/paddle-tech-2026",
        "source_name": "Mock Source",
        "snippet": "From thermoformed edges to carbon fiber weaves, these paddle innovations are transforming how pros play.",
    },
    {
        "title": "Pickleball Officially Added to 2028 LA Olympics Exhibition Schedule",
        "source_url": "https://example.com/olympics-pickleball",
        "source_name": "Mock Source",
        "snippet": "The International Olympic Committee has confirmed pickleball as an exhibition sport at the 2028 Los Angeles Olympics.",
    },
    {
        "title": "Federico Staksrud Upsets Tyson McGuffin in Desert Ridge Semifinal",
        "source_url": "https://example.com/staksrud-upset",
        "source_name": "Mock Source",
        "snippet": "Argentinian star Federico Staksrud pulled off a stunning three-game upset against the number-two seed.",
    },
    {
        "title": "Selkirk Labs Releases Project 004 Paddle with AI-Optimized Design",
        "source_url": "https://example.com/selkirk-004",
        "source_name": "Mock Source",
        "snippet": "Selkirk's latest paddle uses machine learning to optimize core density distribution for maximum spin and power.",
    },
    {
        "title": "Catherine Parenteau and Lea Jansen Form New Doubles Partnership",
        "source_url": "https://example.com/parenteau-jansen-doubles",
        "source_name": "Mock Source",
        "snippet": "Two of the top women's players have announced they will team up for the remainder of the 2026 doubles season.",
    },
]


# ---------------------------------------------------------------------------
# Category detection
# ---------------------------------------------------------------------------
def detect_category(title: str, snippet: str = "") -> str:
    """Auto-detect news category from title and snippet text."""
    text = (title + " " + snippet).lower()
    best_category = "general"
    best_score = 0
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best_category = cat
    return best_category


# ---------------------------------------------------------------------------
# Scraping
# ---------------------------------------------------------------------------
def scrape_source(source: dict) -> list[dict]:
    """Try to scrape news from a single source."""
    articles = []
    try:
        log.info("Scraping %s (%s)...", source["name"], source["url"])
        resp = requests.get(source["url"], timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (PicklrLab News Crawler/1.0)",
        })
        if resp.status_code != 200:
            log.warning("Got status %d from %s", resp.status_code, source["url"])
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(source["selector"])
        log.info("Found %d article elements on %s", len(items), source["name"])

        for item in items[:20]:
            title_el = item.select_one(source["title_selector"])
            link_el = item.select_one(source["link_selector"])

            if not title_el:
                continue

            title = title_el.get_text(strip=True)
            if not title or len(title) < 10:
                continue

            href = ""
            if link_el and link_el.get("href"):
                href = link_el["href"]
                if href.startswith("/"):
                    href = source["url"].rstrip("/") + href

            snippet = ""
            p_el = item.select_one("p")
            if p_el:
                snippet = p_el.get_text(strip=True)[:300]

            articles.append({
                "title": title,
                "source_url": href,
                "source_name": source["name"],
                "snippet": snippet,
                "category": detect_category(title, snippet),
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            })

    except Exception as exc:
        log.warning("Error scraping %s: %s", source["name"], exc)

    return articles


def fetch_news() -> list[dict]:
    """Fetch news from all sources, fall back to mock if none found."""
    all_articles = []

    for source in NEWS_SOURCES:
        articles = scrape_source(source)
        all_articles.extend(articles)

    if all_articles:
        log.info("Scraped %d articles from live sources", len(all_articles))
        return all_articles

    log.info("No live articles found, using mock data")
    now = datetime.now(timezone.utc).isoformat()
    mock_articles = []
    for item in MOCK_NEWS:
        mock_articles.append({
            **item,
            "category": detect_category(item["title"], item.get("snippet", "")),
            "scraped_at": now,
        })
    return mock_articles


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Scrape pickleball news")
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output JSON file path (default: stdout)",
    )
    args = parser.parse_args()

    log.info("=== scrape_news.py starting ===")

    articles = fetch_news()
    log.info("Total articles: %d", len(articles))

    for a in articles:
        log.info("  [%s] %s", a["category"], a["title"][:80])

    output_json = json.dumps(articles, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        log.info("Saved to %s", args.output)
    else:
        print(output_json)

    log.info("=== scrape_news.py done ===")


if __name__ == "__main__":
    main()
