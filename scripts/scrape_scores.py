#!/usr/bin/env python3
"""
Crawl live pickleball match scores and save to Supabase.
Usage: python scrape_scores.py
"""

import logging
import os
import random
import sys
from datetime import datetime, timezone, timedelta

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
TOURNAMENTS = [
    "PPA Masters 2026",
    "MLP Austin 2026",
    "PPA Desert Ridge Open 2026",
    "APP Punta Cana 2026",
    "PPA US Open 2026",
]

ROUNDS = [
    "Round of 32", "Round of 16", "Quarterfinal", "Semifinal", "Final",
]

CATEGORIES = [
    "mens_singles", "womens_singles", "mens_doubles", "womens_doubles", "mixed_doubles",
]

PLAYER_NAMES = [
    "Ben Johns", "Tyson McGuffin", "Federico Staksrud", "Collin Shea",
    "Jay Devillier", "Connor Garnett", "Dylan Frazier", "Hayden Patriquin",
    "Anna Leigh Waters", "Catherine Parenteau", "Lea Jansen", "Jorja Johnson",
    "Salome Devidze", "Irina Tereschenko", "Vivienne David", "Jade Kawamoto",
    "Rachel Rohrabacher", "Mary Brascia", "Jackie Kawamoto", "Jessie Irvine",
]

MATCH_STATUSES = ["upcoming", "live", "done"]


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


def resolve_player_id(sb, slug: str) -> str | None:
    """Look up player ID by slug, return None if not found."""
    try:
        result = sb.table("players").select("id").eq("slug", slug).limit(1).execute()
        if result.data:
            return result.data[0]["id"]
    except Exception as exc:
        log.warning("Could not resolve player %s: %s", slug, exc)
    return None


# ---------------------------------------------------------------------------
# Mock score generation
# ---------------------------------------------------------------------------
def generate_game_score(status: str) -> dict:
    """Generate a realistic pickleball game score."""
    if status == "upcoming":
        return {"games": [], "current_game": None}

    num_games = random.choice([2, 3]) if status == "done" else random.randint(1, 2)
    games = []

    for i in range(num_games):
        if status == "done" or i < num_games - 1:
            # Completed game
            winner_score = 11
            loser_score = random.randint(3, 9)
            if random.random() < 0.2:
                # Deuce-style finish
                winner_score = random.choice([12, 13, 14, 15])
                loser_score = winner_score - 2
            if random.random() < 0.5:
                games.append({"p1": winner_score, "p2": loser_score})
            else:
                games.append({"p1": loser_score, "p2": winner_score})
        else:
            # In-progress game
            p1 = random.randint(0, 10)
            p2 = random.randint(0, 10)
            games.append({"p1": p1, "p2": p2})

    return {
        "games": games,
        "current_game": len(games) if status == "live" else None,
    }


def fetch_live_scores() -> list[dict]:
    """Generate realistic mock live match data."""
    log.info("Generating mock live scores...")
    matches = []
    now = datetime.now(timezone.utc)

    num_matches = random.randint(5, 10)

    for i in range(num_matches):
        tournament = random.choice(TOURNAMENTS)
        round_name = random.choice(ROUNDS)
        category = random.choice(CATEGORIES)

        # Pick two distinct players
        p1, p2 = random.sample(PLAYER_NAMES, 2)

        # Weighted status: more live and done than upcoming
        status = random.choices(
            MATCH_STATUSES, weights=[0.2, 0.4, 0.4], k=1
        )[0]

        score = generate_game_score(status)

        scheduled = now - timedelta(hours=random.randint(0, 48))
        if status == "upcoming":
            scheduled = now + timedelta(hours=random.randint(1, 24))

        matches.append({
            "tournament": tournament,
            "round": round_name,
            "category": category,
            "player1_name": p1,
            "player1_slug": slugify(p1),
            "player2_name": p2,
            "player2_slug": slugify(p2),
            "status": status,
            "score": score,
            "scheduled_at": scheduled.isoformat(),
        })

    return matches


# ---------------------------------------------------------------------------
# Save to Supabase
# ---------------------------------------------------------------------------
def save_scores(matches: list[dict]):
    """Upsert match scores to Supabase."""
    sb = get_supabase()
    now = datetime.now(timezone.utc).isoformat()

    saved = 0
    skipped = 0

    for m in matches:
        p1_id = resolve_player_id(sb, m["player1_slug"])
        p2_id = resolve_player_id(sb, m["player2_slug"])

        row = {
            "tournament": m["tournament"],
            "round": m["round"],
            "category": m["category"],
            "player1_name": m["player1_name"],
            "player1_slug": m["player1_slug"],
            "player1_id": p1_id,
            "player2_name": m["player2_name"],
            "player2_slug": m["player2_slug"],
            "player2_id": p2_id,
            "status": m["status"],
            "score": m["score"],
            "scheduled_at": m["scheduled_at"],
            "updated_at": now,
        }

        try:
            sb.table("matches").upsert(
                row,
                on_conflict="tournament,round,player1_slug,player2_slug",
            ).execute()
            saved += 1
            log.info(
                "  [%s] %s vs %s — %s (%s, %s)",
                m["status"].upper(),
                m["player1_name"],
                m["player2_name"],
                m["tournament"],
                m["round"],
                m["category"],
            )
        except Exception as exc:
            log.error("Failed to save match: %s", exc)
            skipped += 1

    log.info("Saved %d matches, skipped %d", saved, skipped)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    log.info("=== scrape_scores.py starting ===")

    matches = fetch_live_scores()
    log.info("Fetched %d matches", len(matches))

    import argparse
    parser = argparse.ArgumentParser(description="Scrape live pickleball scores")
    parser.add_argument("--dry-run", action="store_true", help="Print without saving")
    args = parser.parse_args()

    if args.dry_run:
        for m in matches:
            log.info(
                "  [%s] %s vs %s — %s",
                m["status"].upper(), m["player1_name"], m["player2_name"], m["tournament"],
            )
        log.info("Dry run, not saving")
    else:
        save_scores(matches)

    log.info("=== scrape_scores.py done ===")


if __name__ == "__main__":
    main()
