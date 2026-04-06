#!/usr/bin/env python3
"""
Auto-generate player bios using Claude API.
Fetches players without bios from Supabase and generates ~100 word bios.
Usage: python auto_player_bios.py
"""

import argparse
import logging
import os
import sys
import time
from datetime import datetime, timezone

import anthropic
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
MAX_PLAYERS_PER_RUN = 10
DELAY_BETWEEN_CALLS = 2  # seconds
CLAUDE_MODEL = "claude-sonnet-4-20250514"

BIO_PROMPT = """\
Write a brief biography (approximately 100 words) for a professional pickleball player.

Player details:
- Name: {name}
- Country: {country}
- Current ranking: {ranking}
- Paddle: {paddle}

Write in third person, present tense. Be factual and engaging. Focus on their playing style, \
achievements, and what makes them stand out. Do not fabricate specific tournament wins or exact \
statistics — keep it general but compelling. Write in a single paragraph, no headers or formatting.

Respond with ONLY the bio text, nothing else.
"""


# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------
def get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        log.error("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY env vars")
        sys.exit(1)
    return create_client(url, key)


def get_claude():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        log.error("Missing ANTHROPIC_API_KEY env var")
        sys.exit(1)
    return anthropic.Anthropic(api_key=api_key)


# ---------------------------------------------------------------------------
# Fetch players needing bios
# ---------------------------------------------------------------------------
def fetch_players_without_bios(sb, limit: int = MAX_PLAYERS_PER_RUN) -> list[dict]:
    """Get players where bio is NULL or empty string."""
    try:
        # Fetch players with no bio
        result = (
            sb.table("players")
            .select("id, slug, name, country, paddle")
            .or_("bio.is.null,bio.eq.")
            .limit(limit)
            .execute()
        )
        return result.data
    except Exception as exc:
        log.error("Failed to fetch players: %s", exc)
        return []


def get_player_ranking(sb, player_id: str) -> str:
    """Get best ranking for a player."""
    try:
        result = (
            sb.table("rankings")
            .select("rank, category")
            .eq("player_id", player_id)
            .order("rank")
            .limit(1)
            .execute()
        )
        if result.data:
            r = result.data[0]
            cat_label = r["category"].replace("_", " ").title()
            return f"#{r['rank']} in {cat_label}"
    except Exception:
        pass
    return "Unranked"


# ---------------------------------------------------------------------------
# Bio generation
# ---------------------------------------------------------------------------
def generate_bio(client: anthropic.Anthropic, player: dict, ranking: str) -> str | None:
    """Call Claude to generate a player bio."""
    prompt = BIO_PROMPT.format(
        name=player["name"],
        country=player.get("country", "Unknown"),
        ranking=ranking,
        paddle=player.get("paddle", "Unknown"),
    )

    try:
        log.info("Generating bio for: %s", player["name"])
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )

        bio = message.content[0].text.strip()

        # Basic validation
        if len(bio) < 30:
            log.warning("Bio too short (%d chars) for %s", len(bio), player["name"])
            return None

        # Trim if too long (should be ~100 words)
        words = bio.split()
        if len(words) > 150:
            bio = " ".join(words[:130]) + "."

        return bio

    except anthropic.APIError as exc:
        log.error("Claude API error for %s: %s", player["name"], exc)
        return None
    except Exception as exc:
        log.error("Unexpected error generating bio for %s: %s", player["name"], exc)
        return None


def update_player_bio(sb, player_id: str, bio: str) -> bool:
    """Update the player's bio in Supabase."""
    now = datetime.now(timezone.utc).isoformat()
    try:
        sb.table("players").update({
            "bio": bio,
            "updated_at": now,
        }).eq("id", player_id).execute()
        return True
    except Exception as exc:
        log.error("Failed to update bio for player %s: %s", player_id, exc)
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Auto-generate player bios")
    parser.add_argument(
        "--max",
        type=int,
        default=MAX_PLAYERS_PER_RUN,
        help=f"Max players per run (default: {MAX_PLAYERS_PER_RUN})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate bios but don't save to Supabase",
    )
    args = parser.parse_args()

    log.info("=== auto_player_bios.py starting ===")

    sb = get_supabase()
    claude = get_claude()

    players = fetch_players_without_bios(sb, limit=args.max)
    log.info("Found %d players without bios", len(players))

    if not players:
        log.info("No players need bios, exiting")
        return

    updated = 0
    failed = 0

    for player in players:
        ranking = get_player_ranking(sb, player["id"])
        log.info("  %s (%s, %s)", player["name"], player.get("country", "?"), ranking)

        bio = generate_bio(claude, player, ranking)
        if not bio:
            failed += 1
            continue

        if args.dry_run:
            log.info("  [DRY RUN] Bio (%d words): %s...", len(bio.split()), bio[:120])
        else:
            if update_player_bio(sb, player["id"], bio):
                updated += 1
                log.info("  Updated bio for %s (%d words)", player["name"], len(bio.split()))
            else:
                failed += 1

        # Rate limiting
        if updated + failed < len(players):
            time.sleep(DELAY_BETWEEN_CALLS)

    log.info("Updated %d bios, failed %d", updated, failed)
    log.info("=== auto_player_bios.py done ===")


if __name__ == "__main__":
    main()
