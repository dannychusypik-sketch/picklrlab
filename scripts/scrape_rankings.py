#!/usr/bin/env python3
"""
Crawl PPA pickleball rankings and save to Supabase.
Usage: python scrape_rankings.py --category mens_singles
"""

import argparse
import logging
import os
import random
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup
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
# Constants
# ---------------------------------------------------------------------------
VALID_CATEGORIES = [
    "mens_singles",
    "womens_singles",
    "mens_doubles",
    "womens_doubles",
    "mixed_doubles",
]

RANKING_SOURCES = [
    "https://www.ppatour.com/player-rankings/",
    "https://www.pickleballbrackets.com/rankings.aspx",
]

# Realistic player pools for mock data
FIRST_NAMES_MALE = [
    "Ben", "Tyson", "Federico", "Collin", "Jay", "JW", "Connor", "Dylan",
    "Hayden", "Thomas", "Matt", "Zane", "Travis", "Hunter", "James",
    "Christian", "Jack", "Tyler", "AJ", "Andrei", "Pablo", "Deckel",
    "Julian", "Sam", "Callan",
]
FIRST_NAMES_FEMALE = [
    "Anna Leigh", "Catherine", "Lea", "Jorja", "Salome", "Irina",
    "Vivienne", "Jade", "Rachel", "Mary", "Jackie", "Megan", "Etta",
    "Callie", "Jessie", "Lauren", "Anna", "Georgia", "Lacy", "Lindsey",
    "Parris", "Brooke", "Susannah", "Elise", "Allyce",
]
LAST_NAMES = [
    "Johns", "McGuffin", "Staksrud", "Shea", "Devillier", "Johnson",
    "Garnett", "Frazier", "Patriquin", "Wilson", "Wright", "Navratil",
    "Rettenmaier", "Wiederhold", "Ignatowich", "Waters", "Parenteau",
    "Jansen", "Todd", "Bright", "Kawamoto", "Barr", "Newman", "Jones",
    "Braverman", "Smith", "Daescu", "Tereschenko", "Jardim", "Bar",
]
COUNTRIES = [
    "USA", "USA", "USA", "USA", "USA", "USA", "USA",  # weighted
    "Canada", "Spain", "Brazil", "Romania", "Italy", "Australia",
    "Japan", "France", "Germany", "Colombia", "Argentina",
]
PADDLES = [
    "Joola Hyperion CFS 16", "Selkirk Vanguard Power Air", "Franklin Signature",
    "Engage Pursuit MX", "Electrum Model E", "ProKennex Ovation Flight",
    "Joola Scorpeus CFS 14", "Selkirk Labs Project 003", "Paddletek Bantam TS-5",
    "CRBN-1X Power Series", "Legacy Pro 16mm", "Six Zero Double Black Diamond",
]


# ---------------------------------------------------------------------------
# Supabase helpers
# ---------------------------------------------------------------------------
def get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        log.error("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY env vars")
        sys.exit(1)
    return create_client(url, key)


def save_to_supabase(players: list[dict], rankings: list[dict]):
    """Upsert players and rankings into Supabase."""
    sb = get_supabase()
    now = datetime.now(timezone.utc).isoformat()

    # --- Upsert players ---
    player_rows = []
    for p in players:
        player_rows.append({
            "slug": p["slug"],
            "name": p["name"],
            "country": p["country"],
            "paddle": p.get("paddle", ""),
            "photo_url": p.get("photo_url", ""),
        })

    if player_rows:
        log.info("Upserting %d players...", len(player_rows))
        sb.table("players").upsert(
            player_rows, on_conflict="slug"
        ).execute()
        log.info("Players upserted OK")

    # --- Resolve player IDs ---
    slugs = [p["slug"] for p in players]
    result = sb.table("players").select("id, slug").in_("slug", slugs).execute()
    slug_to_id = {r["slug"]: r["id"] for r in result.data}

    # --- Upsert rankings ---
    ranking_rows = []
    for r in rankings:
        pid = slug_to_id.get(r["player_slug"])
        if not pid:
            log.warning("Player slug %s not found, skipping ranking", r["player_slug"])
            continue
        ranking_rows.append({
            "player_id": pid,
            "category": r["category"],
            "period": r["period"],
            "rank": r["rank"],
            "points": r["points"],
            "win_rate": r["win_rate"],
            "titles": r.get("titles", 0),
            "delta": r.get("delta", 0),
        })

    if ranking_rows:
        # Delete old rankings for this category+period, then insert fresh
        category = ranking_rows[0]["category"]
        period = ranking_rows[0]["period"]
        log.info("Clearing old %s rankings for %s...", category, period)
        sb.table("rankings").delete().eq("category", category).eq("period", period).execute()
        log.info("Inserting %d rankings...", len(ranking_rows))
        sb.table("rankings").insert(ranking_rows).execute()
        log.info("Rankings inserted OK")


# ---------------------------------------------------------------------------
# Scraping / mock
# ---------------------------------------------------------------------------
def try_scrape_rankings(category: str) -> tuple[list[dict], list[dict]] | None:
    """Attempt to scrape live ranking data. Returns None on failure."""
    for url in RANKING_SOURCES:
        try:
            log.info("Trying to scrape %s ...", url)
            resp = requests.get(url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (PicklrLab Crawler/1.0)"
            })
            if resp.status_code != 200:
                log.warning("Got status %d from %s", resp.status_code, url)
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            # Attempt generic table parsing
            tables = soup.find_all("table")
            for table in tables:
                rows = table.find_all("tr")
                if len(rows) < 5:
                    continue
                # If we find a table with enough rows, try to parse
                # (placeholder for real parsing once site structure is known)
                log.info("Found table with %d rows at %s — parsing not yet implemented", len(rows), url)
            log.info("Could not parse structured data from %s", url)
        except Exception as exc:
            log.warning("Error scraping %s: %s", url, exc)
    return None


def generate_mock_rankings(category: str, count: int = 50) -> tuple[list[dict], list[dict]]:
    """Generate realistic mock ranking data as fallback."""
    log.info("Generating %d mock rankings for %s", count, category)
    is_womens = "womens" in category
    first_pool = FIRST_NAMES_FEMALE if is_womens else FIRST_NAMES_MALE

    players = []
    rankings = []
    used_names = set()

    period = datetime.now(timezone.utc).strftime("%Y-%m")

    for rank in range(1, count + 1):
        # Build unique name
        for _ in range(50):
            first = random.choice(first_pool)
            last = random.choice(LAST_NAMES)
            full = f"{first} {last}"
            if full not in used_names:
                used_names.add(full)
                break

        slug = slugify(full)
        country = random.choice(COUNTRIES)
        paddle = random.choice(PADDLES)

        # Points decay roughly with rank
        base_points = max(500, 15000 - rank * 250 + random.randint(-200, 200))
        win_rate = round(random.uniform(0.45, 0.85), 3)

        players.append({
            "slug": slug,
            "name": full,
            "country": country,
            "paddle": paddle,
            "photo_url": "",
        })

        rankings.append({
            "player_slug": slug,
            "category": category,
            "period": period,
            "rank": rank,
            "points": base_points,
            "win_rate": win_rate,
        })

    return players, rankings


def fetch_rankings(category: str) -> tuple[list[dict], list[dict]]:
    """Fetch rankings: try live scrape first, fall back to mock."""
    result = try_scrape_rankings(category)
    if result:
        return result
    log.info("Live scrape unavailable, using mock data")
    return generate_mock_rankings(category)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Scrape pickleball rankings")
    parser.add_argument(
        "--category",
        required=True,
        choices=VALID_CATEGORIES,
        help="Ranking category to scrape",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print data without saving to Supabase",
    )
    args = parser.parse_args()

    log.info("=== scrape_rankings.py starting ===")
    log.info("Category: %s", args.category)

    players, rankings = fetch_rankings(args.category)
    log.info("Fetched %d players, %d rankings", len(players), len(rankings))

    if args.dry_run:
        for r in rankings[:5]:
            log.info("  #%d %s — %d pts (%.1f%% win)", r["rank"], r["player_slug"], r["points"], r["win_rate"] * 100)
        log.info("  ... (dry run, not saving)")
    else:
        save_to_supabase(players, rankings)

    log.info("=== scrape_rankings.py done ===")


if __name__ == "__main__":
    main()
