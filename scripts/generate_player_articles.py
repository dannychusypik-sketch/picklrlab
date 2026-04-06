#!/usr/bin/env python3
"""
Daily Player Article Generator for PicklrLab.
Fetches players from Supabase, generates comprehensive profile articles via Claude.
Max 5 articles per run.

Usage:
    SUPABASE_URL=... SUPABASE_SERVICE_KEY=... ANTHROPIC_API_KEY=... python3 generate_player_articles.py
    python3 generate_player_articles.py --dry-run
    python3 generate_player_articles.py --max 3
"""

import json
import logging
import os
import random
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import anthropic
import requests
from slugify import slugify
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
CLAUDE_MODEL = "claude-sonnet-4-20250514"
MAX_ARTICLES_PER_RUN = 5
DELAY_BETWEEN_CALLS = 5  # seconds
IMAGE_SEARCH_TIMEOUT = 10

# Authors for variety
AUTHORS = [
    "PicklrLab Editorial",
    "Sarah Chen",
    "Marcus Rodriguez",
    "Jake Thompson",
    "PicklrLab Editorial",
]

# Country to article category mapping
COUNTRY_CATEGORY_MAP = {
    "VN": "vietnam",
    "TH": "sea",
    "JP": "sea",
    "KR": "sea",
    "PH": "sea",
    "MY": "sea",
    "ID": "sea",
    "SG": "sea",
    "TW": "sea",
    "CN": "sea",
    "IN": "sea",
}

# ---------------------------------------------------------------------------
# Claude Prompt for Player Articles
# ---------------------------------------------------------------------------
PLAYER_ARTICLE_PROMPT = """\
You are writing for PicklrLab.com, the world's #1 pickleball authority.

Write a comprehensive player profile article about {name} from {country_name}.
Current world ranking: #{rank} in {category_label}
Sponsor: {sponsor}
Paddle: {paddle}
Birth year: {birth_year}
Player bio: {bio}

Write 1000-1500 words covering:
1. Introduction & Current Status — who they are, current ranking, why they matter
2. Early Career & Background — how they got into pickleball, athletic background
3. Playing Style & Strengths — what makes their game unique, key shots, tendencies
4. Career Highlights & Achievements — tournament wins, notable performances, records
5. Equipment & Gear Setup — their paddle choice, why it suits their game
6. What Makes {name} Special — their impact on the sport, legacy, future outlook

Include 3 FAQ at the end using this format:
<details><summary>Question?</summary><p>Answer here.</p></details>

Title should be SEO-friendly: "{name}: [compelling descriptor]"

IMPORTANT FORMAT RULES:
- Use proper HTML: <h2>, <h3>, <p>, <ul>, <li>, <strong>, <em>, <blockquote>, <details>, <summary>
- DO NOT use markdown — only HTML tags
- Include internal linking mentions like "Check our latest rankings page for updated standings" and "See our in-depth paddle reviews for more gear analysis"
- Write like an experienced sports journalist, NOT like an AI
- Be authoritative but conversational
- Use active voice and vary sentence length

Respond in EXACTLY this JSON format (no markdown fences, just raw JSON):
{{
  "title": "SEO title here (include player name)",
  "excerpt": "Compelling 1-2 sentence excerpt for article cards",
  "content": "FULL HTML content here (1000-1500 words)",
  "meta_description": "Meta description for SEO, 150-160 chars, include player name",
  "category": "{category}"
}}
"""

# Category labels for display
CATEGORY_LABELS = {
    "mens_singles": "Men's Singles",
    "womens_singles": "Women's Singles",
    "mens_doubles": "Men's Doubles",
    "womens_doubles": "Women's Doubles",
    "mixed_doubles": "Mixed Doubles",
    "ppa_asia": "PPA Asia",
}


# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------
def get_supabase():
    # type: () -> object
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        log.error("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY env vars")
        sys.exit(1)
    return create_client(url, key)


def get_claude():
    # type: () -> anthropic.Anthropic
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        log.error("Missing ANTHROPIC_API_KEY env var")
        sys.exit(1)
    return anthropic.Anthropic(api_key=api_key)


# ---------------------------------------------------------------------------
# Fetch players and check which need articles
# ---------------------------------------------------------------------------
def fetch_all_players_with_rankings(sb):
    # type: (object) -> List[Dict]
    """Fetch all players joined with their best ranking."""
    log.info("Fetching all players from Supabase...")

    # Get all players
    result = sb.table("players").select("*").execute()
    players = result.data
    log.info("Found %d players total", len(players))

    # Get all rankings
    rankings_result = sb.table("rankings").select("*").order("rank").execute()
    rankings = rankings_result.data

    # Build player_id -> best ranking map
    player_rankings = {}  # type: Dict[str, Dict]
    for r in rankings:
        pid = r["player_id"]
        if pid not in player_rankings or r["rank"] < player_rankings[pid]["rank"]:
            player_rankings[pid] = r

    # Merge
    for player in players:
        pid = player["id"]
        if pid in player_rankings:
            player["ranking"] = player_rankings[pid]
        else:
            player["ranking"] = None

    # Sort by ranking (ranked players first, then unranked)
    def sort_key(p):
        # type: (Dict) -> tuple
        r = p.get("ranking")
        if r:
            return (0, r.get("rank", 999))
        return (1, 999)

    players.sort(key=sort_key)
    return players


def find_players_without_articles(sb, players):
    # type: (object, List[Dict]) -> List[Dict]
    """Find players that don't have an article yet."""
    log.info("Checking which players already have articles...")

    # Get all article titles to check for player names
    articles_result = sb.table("articles").select("title, slug").execute()
    existing_articles = articles_result.data

    # Build set of player names found in article titles/slugs
    covered_names = set()  # type: set
    for article in existing_articles:
        title_lower = article.get("title", "").lower()
        slug_lower = article.get("slug", "").lower()
        for player in players:
            name_lower = player["name"].lower()
            name_slug = slugify(player["name"])
            if name_lower in title_lower or name_slug in slug_lower:
                covered_names.add(player["name"])

    # Filter out players who already have articles
    needs_article = []
    for player in players:
        if player["name"] not in covered_names:
            needs_article.append(player)
        else:
            log.info("  Already has article: %s", player["name"])

    log.info("Players needing articles: %d (out of %d total)",
             len(needs_article), len(players))
    return needs_article


# ---------------------------------------------------------------------------
# Image search (YouTube thumbnail or placeholder)
# ---------------------------------------------------------------------------
def find_player_image(player_name):
    # type: (str) -> Optional[str]
    """Try to find a relevant image for the player via YouTube search."""
    try:
        # Try YouTube oEmbed to get a thumbnail
        search_query = "%s pickleball" % player_name
        yt_search_url = "https://www.youtube.com/results?search_query=%s" % (
            requests.utils.quote(search_query)
        )

        resp = requests.get(
            yt_search_url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; PicklrLab/1.0)"},
            timeout=IMAGE_SEARCH_TIMEOUT,
        )
        if resp.status_code == 200:
            # Extract first video ID from page
            video_match = re.search(r'"videoId":"([^"]+)"', resp.text)
            if video_match:
                video_id = video_match.group(1)
                thumbnail_url = "https://img.youtube.com/vi/%s/hqdefault.jpg" % video_id
                log.info("  Found YouTube thumbnail for %s: %s", player_name, thumbnail_url)
                return thumbnail_url
    except Exception as e:
        log.warning("  Image search failed for %s: %s", player_name, e)

    return None


# ---------------------------------------------------------------------------
# Article generation
# ---------------------------------------------------------------------------
def get_country_name(country_code):
    # type: (str) -> str
    """Convert country code to full name."""
    names = {
        "US": "United States", "CA": "Canada", "AR": "Argentina",
        "GB": "Great Britain", "ES": "Spain", "RO": "Romania",
        "GE": "Georgia", "MX": "Mexico", "AU": "Australia",
        "BR": "Brazil", "FR": "France", "DE": "Germany",
        "VN": "Vietnam", "TH": "Thailand", "JP": "Japan",
        "KR": "South Korea", "CN": "China", "PH": "Philippines",
        "MY": "Malaysia", "IN": "India", "ID": "Indonesia",
        "SG": "Singapore", "TW": "Taiwan",
    }
    return names.get(country_code, country_code)


def determine_article_category(player):
    # type: (Dict) -> str
    """Determine the article category based on player country."""
    country = player.get("country", "US")
    if country in COUNTRY_CATEGORY_MAP:
        return COUNTRY_CATEGORY_MAP[country]
    return "tournament"


def generate_player_article(claude_client, player):
    # type: (anthropic.Anthropic, Dict) -> Optional[Dict]
    """Generate a comprehensive player profile article using Claude."""
    ranking_data = player.get("ranking")
    rank = ranking_data["rank"] if ranking_data else "Unranked"
    category = ranking_data["category"] if ranking_data else "mens_singles"
    category_label = CATEGORY_LABELS.get(category, category.replace("_", " ").title())
    article_category = determine_article_category(player)

    prompt = PLAYER_ARTICLE_PROMPT.format(
        name=player["name"],
        country_name=get_country_name(player.get("country", "US")),
        rank=rank,
        category_label=category_label,
        sponsor=player.get("sponsor", "Unknown"),
        paddle=player.get("paddle", "Unknown"),
        birth_year=player.get("birth_year", "Unknown"),
        bio=player.get("bio", "Professional pickleball player."),
        category=article_category,
    )

    try:
        log.info("Generating article for: %s", player["name"])
        message = claude_client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=6000,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text.strip()

        # Handle case where Claude wraps in ```json ... ```
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            response_text = "\n".join(lines)

        article = json.loads(response_text)

        # Validate required fields
        required = ["title", "excerpt", "content", "meta_description", "category"]
        for field in required:
            if field not in article:
                log.warning("Missing field '%s' in generated article for %s", field, player["name"])
                return None

        # Validate content length
        text_only = re.sub(r"<[^>]+>", "", article["content"])
        word_count = len(text_only.split())
        if word_count < 300:
            log.warning("Article too short (%d words) for %s", word_count, player["name"])
            return None

        log.info("  Generated %d words for %s", word_count, player["name"])
        return article

    except json.JSONDecodeError as exc:
        log.error("Failed to parse Claude response as JSON for %s: %s", player["name"], exc)
        return None
    except anthropic.APIError as exc:
        log.error("Claude API error for %s: %s", player["name"], exc)
        return None
    except Exception as exc:
        log.error("Unexpected error for %s: %s", player["name"], exc)
        return None


def calculate_views_from_rank(rank):
    # type: (int) -> int
    """Higher ranked players get more views."""
    if isinstance(rank, str) or rank is None:
        return random.randint(50, 200)
    if rank <= 3:
        return random.randint(3000, 8000)
    elif rank <= 5:
        return random.randint(1500, 4000)
    elif rank <= 10:
        return random.randint(800, 2000)
    elif rank <= 20:
        return random.randint(300, 1000)
    else:
        return random.randint(100, 500)


def save_article_to_supabase(sb, article, player, rank):
    # type: (object, Dict, Dict, int) -> bool
    """Save generated article to Supabase articles table."""
    slug = slugify(article["title"])

    # Check for duplicate
    try:
        existing = sb.table("articles").select("id").eq("slug", slug).limit(1).execute()
        if existing.data:
            log.info("  Article slug already exists: %s", slug)
            return False
    except Exception:
        pass

    # Determine is_featured and views
    is_featured = False
    if rank is not None and isinstance(rank, int) and rank <= 5:
        is_featured = True

    views = calculate_views_from_rank(rank)

    # Spread published_at across last 7 days
    days_ago = random.randint(0, 6)
    hours_ago = random.randint(0, 23)
    published_at = (
        datetime.now(timezone.utc) - timedelta(days=days_ago, hours=hours_ago)
    ).isoformat()

    author = random.choice(AUTHORS)

    row = {
        "title": article["title"],
        "slug": slug,
        "excerpt": article.get("excerpt", ""),
        "content": article["content"],
        "category": article.get("category", "tournament"),
        "author": author,
        "published_at": published_at,
        "is_featured": is_featured,
        "views": views,
    }

    try:
        sb.table("articles").upsert(row, on_conflict="slug").execute()
        log.info("  SAVED article: %s (views=%d, featured=%s)", slug, views, is_featured)
        return True
    except Exception as exc:
        log.error("  Failed to save article: %s", exc)
        # Retry without optional fields
        try:
            for optional in ["meta_description"]:
                row.pop(optional, None)
            sb.table("articles").upsert(row, on_conflict="slug").execute()
            log.info("  SAVED (retry): %s", slug)
            return True
        except Exception as exc2:
            log.error("  Retry also failed: %s", exc2)
            return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    # type: () -> None
    dry_run = "--dry-run" in sys.argv

    max_articles = MAX_ARTICLES_PER_RUN
    for i, arg in enumerate(sys.argv):
        if arg == "--max" and i + 1 < len(sys.argv):
            try:
                max_articles = int(sys.argv[i + 1])
            except ValueError:
                pass

    log.info("=== generate_player_articles.py starting ===")
    log.info("Mode: %s | Max articles: %d", "DRY RUN" if dry_run else "LIVE", max_articles)

    sb = get_supabase()
    claude = get_claude()

    # Step 1: Fetch all players with rankings
    players = fetch_all_players_with_rankings(sb)

    # Step 2: Find players without articles
    needs_article = find_players_without_articles(sb, players)

    if not needs_article:
        log.info("All players already have articles!")
        return

    # Limit to max_articles
    to_generate = needs_article[:max_articles]
    log.info("Will generate %d articles this run:", len(to_generate))
    for p in to_generate:
        r = p.get("ranking")
        rank_str = "#%d" % r["rank"] if r else "Unranked"
        log.info("  %s (%s) — %s", p["name"], p.get("country", "?"), rank_str)

    # Step 3: Generate articles
    generated = 0
    failed = 0

    for idx, player in enumerate(to_generate):
        log.info("\n--- Article %d/%d ---", idx + 1, len(to_generate))

        ranking_data = player.get("ranking")
        rank = ranking_data["rank"] if ranking_data else None

        # Generate article
        article = generate_player_article(claude, player)
        if not article:
            failed += 1
            if idx < len(to_generate) - 1:
                time.sleep(DELAY_BETWEEN_CALLS)
            continue

        # Try to find an image
        image_url = find_player_image(player["name"])
        if image_url and article.get("content"):
            # Prepend image to content
            alt_text = article["title"].replace('"', "&quot;")
            image_html = (
                '<img src="%s" alt="%s" '
                'width="800" height="450" '
                'style="width:100%%;height:auto;border-radius:8px;margin-bottom:1.5rem;" '
                'loading="lazy" />'
            ) % (image_url, alt_text)
            article["content"] = image_html + "\n" + article["content"]

        if dry_run:
            text_only = re.sub(r"<[^>]+>", "", article["content"])
            word_count = len(text_only.split())
            h2_count = article["content"].count("<h2>")
            has_faq = "<details>" in article["content"]
            log.info("  [DRY RUN] Title: %s", article["title"])
            log.info("  [DRY RUN] Words: %d | H2s: %d | FAQ: %s", word_count, h2_count, has_faq)
            log.info("  [DRY RUN] Category: %s", article.get("category", "?"))
            log.info("  [DRY RUN] Excerpt: %s", article.get("excerpt", "")[:100])
            generated += 1
        else:
            if save_article_to_supabase(sb, article, player, rank):
                generated += 1
            else:
                failed += 1

        # Rate limiting
        if idx < len(to_generate) - 1:
            log.info("  Waiting %ds...", DELAY_BETWEEN_CALLS)
            time.sleep(DELAY_BETWEEN_CALLS)

    log.info("\n=== DONE ===")
    log.info("Generated: %d | Failed: %d | Total attempted: %d",
             generated, failed, len(to_generate))
    log.info("=== generate_player_articles.py done ===")


if __name__ == "__main__":
    main()
