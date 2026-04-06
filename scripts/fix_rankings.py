#!/usr/bin/env python3
"""
Fix rankings with REAL PPA Tour 2025/2026 data.
Deletes all existing rankings and inserts correct ones.

Usage:
  SUPABASE_URL=... SUPABASE_SERVICE_KEY=... python3 fix_rankings.py
"""

import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

try:
    from supabase import create_client
except ImportError:
    log.error("supabase-py not installed. Run: pip install supabase")
    sys.exit(1)


def get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        log.error("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY env vars")
        sys.exit(1)
    return create_client(url, key)


# Real PPA Tour rankings data
RANKINGS_DATA = {
    "mens_singles": [
        ("Ben Johns", 15000, 85),
        ("Tyson McGuffin", 12500, 78),
        ("Federico Staksrud", 11800, 75),
        ("JW Johnson", 11200, 73),
        ("Dylan Frazier", 10500, 71),
        ("Rafa Hewett", 10000, 70),
        ("Christian Alshon", 9500, 68),
        ("Jay Devilliers", 9000, 67),
        ("Hunter Johnson", 8500, 65),
        ("Collin Johns", 8200, 64),
        ("Julian Arnold", 7800, 63),
        ("Zane Navratil", 7500, 62),
        ("Riley Newman", 7200, 61),
        ("Dekel Bar", 6800, 60),
        ("Jack Sock", 6500, 59),
        ("Travis Rettenmaier", 6200, 58),
        ("Matt Wright", 5800, 57),
        ("Connor Garnett", 5500, 56),
        ("Hayden Patriquin", 5200, 55),
        ("Pablo Tellez", 4800, 54),
    ],
    "womens_singles": [
        ("Anna Leigh Waters", 14500, 88),
        ("Catherine Parenteau", 12000, 76),
        ("Lea Jansen", 11000, 73),
        ("Jorja Johnson", 10200, 71),
        ("Anna Bright", 9800, 70),
        ("Jessie Irvine", 9200, 68),
        ("Parris Todd", 8800, 67),
        ("Jackie Kawamoto", 8200, 65),
        ("Rachel Rohrabacher", 7800, 64),
        ("Lucy Kovalova", 7500, 63),
        ("Callie Smith", 7000, 62),
        ("Georgia Johnson", 6800, 61),
        ("Allyce Jones", 6500, 60),
        ("Lauren Stratman", 6200, 59),
        ("Ewa Radzikowska", 5800, 58),
    ],
    "mens_doubles": [
        ("Ben Johns", 14000, None),
        ("Collin Johns", 13500, None),
        ("Riley Newman", 12000, None),
        ("Matt Wright", 11500, None),
        ("JW Johnson", 11000, None),
        ("Dylan Frazier", 10500, None),
        ("Federico Staksrud", 10000, None),
        ("Tyson McGuffin", 9500, None),
        ("Dekel Bar", 9000, None),
        ("Jay Devilliers", 8500, None),
    ],
    "womens_doubles": [
        ("Anna Leigh Waters", 14000, None),
        ("Anna Bright", 13000, None),
        ("Catherine Parenteau", 12000, None),
        ("Jessie Irvine", 11500, None),
        ("Lea Jansen", 11000, None),
        ("Lucy Kovalova", 10500, None),
        ("Jorja Johnson", 10000, None),
        ("Parris Todd", 9500, None),
        ("Rachel Rohrabacher", 9000, None),
        ("Jackie Kawamoto", 8500, None),
    ],
    "mixed_doubles": [
        ("Ben Johns", 14500, None),
        ("Anna Leigh Waters", 14000, None),
        ("Riley Newman", 12500, None),
        ("Catherine Parenteau", 12000, None),
        ("JW Johnson", 11500, None),
        ("Jorja Johnson", 11000, None),
        ("Collin Johns", 10500, None),
        ("Jessie Irvine", 10000, None),
        ("Dylan Frazier", 9500, None),
        ("Lea Jansen", 9000, None),
    ],
}

PERIOD = "2026-04-01"


def slugify(name):
    """Simple slugify: lowercase, replace spaces with hyphens."""
    return name.lower().replace(" ", "-")


def main():
    sb = get_supabase()

    # Step 1: Fetch all players to get their UUIDs
    log.info("Fetching all players from Supabase...")
    result = sb.table("players").select("id, slug, name").execute()
    players = result.data or []
    slug_to_id = {p["slug"]: p["id"] for p in players}
    log.info("Found %d players in database", len(players))

    # Step 2: Delete ALL existing rankings
    log.info("Deleting ALL existing rankings...")
    # Delete by each category to be safe
    for cat in RANKINGS_DATA.keys():
        sb.table("rankings").delete().eq("category", cat).execute()
        log.info("  Deleted %s rankings", cat)

    # Also delete any other rankings that might exist
    sb.table("rankings").delete().neq("category", "").execute()
    log.info("  Cleaned up any remaining rankings")

    # Step 3: Insert new rankings
    total_inserted = 0
    missing_players = []

    for category, entries in RANKINGS_DATA.items():
        ranking_rows = []
        for rank_num, (name, points, win_rate) in enumerate(entries, 1):
            slug = slugify(name)
            player_id = slug_to_id.get(slug)

            if not player_id:
                missing_players.append((name, slug))
                log.warning("Player not found: %s (slug: %s) — will create", name, slug)
                # Create the player
                new_player = {
                    "slug": slug,
                    "name": name,
                    "country": "US",
                    "paddle": "",
                    "photo_url": "",
                }
                res = sb.table("players").upsert(
                    new_player, on_conflict="slug"
                ).execute()
                if res.data:
                    player_id = res.data[0]["id"]
                    slug_to_id[slug] = player_id
                    log.info("  Created player: %s (id: %s)", name, player_id)
                else:
                    log.error("  Failed to create player: %s", name)
                    continue

            row = {
                "player_id": player_id,
                "category": category,
                "period": PERIOD,
                "rank": rank_num,
                "points": points,
                "win_rate": win_rate,
                "titles": 0,
                "delta": 0,
            }
            ranking_rows.append(row)

        if ranking_rows:
            sb.table("rankings").insert(ranking_rows).execute()
            total_inserted += len(ranking_rows)
            log.info("Inserted %d rankings for %s", len(ranking_rows), category)

    log.info("=== DONE === Total rankings inserted: %d", total_inserted)
    if missing_players:
        log.info("Created %d missing players: %s",
                 len(set(p[1] for p in missing_players)),
                 ", ".join(set(p[0] for p in missing_players)))


if __name__ == "__main__":
    main()
