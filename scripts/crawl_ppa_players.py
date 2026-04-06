#!/usr/bin/env python3
"""
Crawl ALL PPA Tour athletes from WordPress API and save to Supabase.

Fetches ~160 athletes with photos, bios, countries, sponsors, divisions.
Generates approximate rankings from division membership order.

Usage:
    SUPABASE_URL=... SUPABASE_SERVICE_KEY=... python3 crawl_ppa_players.py
    python3 crawl_ppa_players.py --dry-run
"""

import html
import logging
import os
import re
import sys
import time
from typing import Dict, List, Optional

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
# Constants
# ---------------------------------------------------------------------------
PPA_API = "https://propb.flywheelsites.com/wp-json/wp/v2"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PicklrLab/1.0)"}
RATE_LIMIT = 0.3  # seconds between API calls

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "public", "images", "players")
PUBLIC_PATH = "/images/players"

# Country name -> ISO 2-char code
COUNTRY_MAP = {
    "United States": "US", "USA": "US", "U.S.A.": "US", "US": "US",
    "Canada": "CA",
    "Argentina": "AR",
    "Great Britain": "GB", "UK": "GB", "United Kingdom": "GB", "England": "GB",
    "Spain": "ES",
    "Germany": "DE",
    "France": "FR",
    "Italy": "IT",
    "Australia": "AU",
    "Japan": "JP",
    "South Korea": "KR", "Korea": "KR",
    "China": "CN",
    "India": "IN",
    "Thailand": "TH",
    "Vietnam": "VN",
    "Philippines": "PH",
    "Malaysia": "MY",
    "Indonesia": "ID",
    "Singapore": "SG",
    "Taiwan": "TW",
    "Brazil": "BR",
    "Colombia": "CO",
    "Mexico": "MX",
    "Romania": "RO",
    "Czech Republic": "CZ", "Czechia": "CZ",
    "Georgia": "GE",
    "Israel": "IL",
    "Netherlands": "NL", "The Netherlands": "NL",
    "Poland": "PL",
    "Sweden": "SE",
    "Switzerland": "CH",
    "Belgium": "BE",
    "Peru": "PE",
    "New Zealand": "NZ",
    "Ireland": "IE",
    "Portugal": "PT",
    "Austria": "AT",
    "Denmark": "DK",
    "Norway": "NO",
    "Finland": "FI",
    "Puerto Rico": "PR",
    "Chile": "CL",
    "Croatia": "HR",
    "Serbia": "RS",
    "Hungary": "HU",
    "Ukraine": "UA",
    "Russia": "RU",
    "Turkey": "TR",
    "South Africa": "ZA",
    "Egypt": "EG",
    "Morocco": "MA",
    "Costa Rica": "CR",
    "Dominican Republic": "DO",
    "Ecuador": "EC",
    "Venezuela": "VE",
    "Uruguay": "UY",
    "Paraguay": "PY",
    "Bolivia": "BO",
    "Panama": "PA",
    "Guatemala": "GT",
    "Honduras": "HN",
    "El Salvador": "SV",
    "Nicaragua": "NI",
    "Jamaica": "JM",
    "Trinidad and Tobago": "TT",
    "Bahamas": "BS",
    "Cuba": "CU",
}

# Division name -> ranking category
DIVISION_MAP = {
    "Men's Singles": "mens_singles",
    "Women's Singles": "womens_singles",
    "Men's Doubles": "mens_doubles",
    "Women's Doubles": "womens_doubles",
    "Mixed Doubles": "mixed_doubles",
    "Men\u2019s Singles": "mens_singles",
    "Women\u2019s Singles": "womens_singles",
    "Men\u2019s Doubles": "mens_doubles",
    "Women\u2019s Doubles": "womens_doubles",
    "Mixed Doubles Pro": "mixed_doubles",
    "Senior Pro": "senior_pro",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def api_get(endpoint, params=None):
    """GET from PPA API with rate limiting."""
    url = "{}/{}".format(PPA_API, endpoint)
    time.sleep(RATE_LIMIT)
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log.warning("API error %s: %s", endpoint, e)
        return None


def strip_html(text):
    """Remove HTML tags and decode entities."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def sanitize_filename(slug, ext=".jpg"):
    """Create clean filename from slug."""
    clean = re.sub(r"[^a-z0-9\-]", "", slug.lower())[:80]
    return "{}{}".format(clean, ext)


def download_player_photo(image_url, slug):
    """Download photo and return public path, or None on failure."""
    if not image_url:
        return None

    os.makedirs(IMAGES_DIR, exist_ok=True)

    # Determine extension
    path_lower = image_url.lower()
    if ".png" in path_lower:
        ext = ".png"
    elif ".webp" in path_lower:
        ext = ".webp"
    else:
        ext = ".jpg"

    filename = sanitize_filename(slug, ext)
    filepath = os.path.join(IMAGES_DIR, filename)
    public_url = "{}/{}".format(PUBLIC_PATH, filename)

    if os.path.exists(filepath):
        return public_url

    try:
        resp = requests.get(image_url, timeout=15, headers=HEADERS)
        resp.raise_for_status()

        content_type = resp.headers.get("content-type", "")
        if "image" not in content_type and len(resp.content) < 1000:
            return None

        with open(filepath, "wb") as f:
            f.write(resp.content)

        return public_url
    except Exception as e:
        log.warning("Photo download failed for %s: %s", slug, e)
        return None


def extract_paddle_from_bio(bio_text):
    """Try to extract paddle brand/model from bio text."""
    # Common paddle brands
    brands = [
        "JOOLA", "Selkirk", "Franklin", "Engage", "ProKennex",
        "Paddletek", "Head", "Wilson", "CRBN", "Legacy Pro",
        "Electrum", "Six Zero", "Gearbox", "Vulcan", "Onix",
        "Diadem", "VATIC", "Bread & Butter",
    ]
    for brand in brands:
        if brand.lower() in bio_text.lower():
            return brand
    return ""


# ---------------------------------------------------------------------------
# Step 1: Fetch taxonomies
# ---------------------------------------------------------------------------
def fetch_taxonomies():
    """Fetch country, sponsor, division lookup tables."""
    lookups = {}
    for taxonomy in ["country", "sponsor", "division"]:
        log.info("Fetching taxonomy: %s", taxonomy)
        all_items = []
        page = 1
        while True:
            data = api_get(taxonomy, params={
                "per_page": 100,
                "_fields": "id,name",
                "page": page,
            })
            if not data or len(data) == 0:
                break
            all_items.extend(data)
            if len(data) < 100:
                break
            page += 1

        lookup = {}
        for item in all_items:
            lookup[item["id"]] = item["name"]
        lookups[taxonomy] = lookup
        log.info("  Found %d %s entries: %s", len(lookup), taxonomy,
                 ", ".join(list(lookup.values())[:10]))

    return lookups["country"], lookups["sponsor"], lookups["division"]


# ---------------------------------------------------------------------------
# Step 2: Fetch all athletes
# ---------------------------------------------------------------------------
def fetch_all_athletes():
    """Fetch all athletes from paginated API."""
    all_athletes = []
    page = 1
    while True:
        log.info("Fetching athletes page %d...", page)
        data = api_get("athlete", params={
            "per_page": 100,
            "page": page,
        })
        if not data or len(data) == 0:
            break
        all_athletes.extend(data)
        log.info("  Got %d athletes (total: %d)", len(data), len(all_athletes))
        if len(data) < 100:
            break
        page += 1

    log.info("Total athletes fetched: %d", len(all_athletes))
    return all_athletes


# ---------------------------------------------------------------------------
# Step 3: Resolve media URLs (batch)
# ---------------------------------------------------------------------------
def fetch_media_urls(media_ids):
    """Fetch photo URLs for a list of media IDs. Returns {id: url}."""
    media_map = {}
    unique_ids = list(set(mid for mid in media_ids if mid and mid != 0))

    if not unique_ids:
        return media_map

    log.info("Fetching %d media URLs...", len(unique_ids))

    # Batch fetch: WP API supports include param
    for i in range(0, len(unique_ids), 20):
        chunk = unique_ids[i:i + 20]
        ids_str = ",".join(str(x) for x in chunk)
        data = api_get("media", params={
            "include": ids_str,
            "per_page": 20,
            "_fields": "id,source_url",
        })
        if data:
            for item in data:
                media_map[item["id"]] = item.get("source_url", "")
        log.info("  Resolved %d/%d media URLs", len(media_map), len(unique_ids))

    return media_map


# ---------------------------------------------------------------------------
# Process athletes
# ---------------------------------------------------------------------------
def process_athletes(raw_athletes, countries, sponsors, divisions, media_map):
    """Process raw athlete data into clean player records."""
    players = []
    # Track division membership for ranking generation
    division_members = {}  # {division_name: [player_slugs]}

    for idx, athlete in enumerate(raw_athletes, 1):
        name = strip_html(athlete.get("title", {}).get("rendered", ""))
        slug = athlete.get("slug", slugify(name))

        # Country
        country_ids = athlete.get("country", [])
        country_name = ""
        iso_code = ""
        if country_ids:
            cid = country_ids[0] if isinstance(country_ids, list) else country_ids
            country_name = countries.get(cid, "")
            iso_code = COUNTRY_MAP.get(country_name, "")
            if not iso_code and country_name:
                # Try partial match
                for k, v in COUNTRY_MAP.items():
                    if k.lower() in country_name.lower() or country_name.lower() in k.lower():
                        iso_code = v
                        break
                if not iso_code:
                    log.warning("  Unknown country: %s (id=%s)", country_name, cid)

        # Sponsors
        sponsor_ids = athlete.get("sponsor", [])
        sponsor_names = []
        if isinstance(sponsor_ids, list):
            for sid in sponsor_ids:
                sname = sponsors.get(sid, "")
                if sname:
                    sponsor_names.append(sname)
        sponsor_str = ", ".join(sponsor_names) if sponsor_names else ""

        # Divisions
        div_ids = athlete.get("division", [])
        div_names = []
        if isinstance(div_ids, list):
            for did in div_ids:
                dname = divisions.get(did, "")
                if dname:
                    div_names.append(dname)
                    # Track for rankings
                    if dname not in division_members:
                        division_members[dname] = []
                    division_members[dname].append(slug)

        # Bio
        content_html = athlete.get("content", {}).get("rendered", "")
        bio_full = strip_html(content_html)
        bio = bio_full[:500] if bio_full else ""

        # SEO description as fallback bio
        if not bio:
            yoast = athlete.get("yoast_head_json", {})
            if yoast:
                bio = yoast.get("description", "")[:500]

        # Photo
        media_id = athlete.get("featured_media", 0)
        photo_source = media_map.get(media_id, "")
        photo_url = ""
        if photo_source:
            photo_url = download_player_photo(photo_source, slug)

        # Paddle
        paddle = extract_paddle_from_bio(bio_full or bio)

        photo_status = "photo ok" if photo_url else "no photo"
        log.info("[%d/%d] %s (%s) -- %s -- %s",
                 idx, len(raw_athletes), name,
                 iso_code or "??", sponsor_str or "no sponsor",
                 photo_status)

        players.append({
            "name": name,
            "slug": slug,
            "country": iso_code,
            "sponsor": sponsor_str,
            "paddle": paddle,
            "bio": bio,
            "photo_url": photo_url or "",
            "divisions": div_names,
        })

    return players, division_members


# ---------------------------------------------------------------------------
# Generate rankings
# ---------------------------------------------------------------------------
def generate_rankings(players, division_members):
    """Generate approximate rankings from division membership order."""
    rankings = []
    slug_lookup = {p["slug"]: p for p in players}

    for div_name, slugs in division_members.items():
        # Map to category
        category = None
        for key, val in DIVISION_MAP.items():
            if key.lower() == div_name.lower() or key.lower() in div_name.lower():
                category = val
                break
        if not category:
            # Try partial match
            dn = div_name.lower()
            if "men" in dn and "single" in dn and "women" not in dn:
                category = "mens_singles"
            elif "women" in dn and "single" in dn:
                category = "womens_singles"
            elif "men" in dn and "double" in dn and "women" not in dn and "mixed" not in dn:
                category = "mens_doubles"
            elif "women" in dn and "double" in dn and "mixed" not in dn:
                category = "womens_doubles"
            elif "mixed" in dn:
                category = "mixed_doubles"
            else:
                log.info("Skipping unknown division for rankings: %s", div_name)
                continue

        base_points = 10000
        for rank, slug in enumerate(slugs, 1):
            player = slug_lookup.get(slug)
            if not player:
                continue
            points = max(base_points - (rank - 1) * 200, 500)
            win_rate = max(85.0 - (rank - 1) * 1.5, 40.0)
            rankings.append({
                "player_slug": slug,
                "category": category,
                "rank": rank,
                "points": points,
                "win_rate": round(win_rate, 1),
                "titles": 0,
                "delta": 0,
                "period": "2026-04-01",
            })

    log.info("Generated %d ranking entries across %d divisions",
             len(rankings), len(division_members))
    return rankings


# ---------------------------------------------------------------------------
# Save to Supabase
# ---------------------------------------------------------------------------
def save_to_supabase(players, rankings):
    """Delete old data and insert all players + rankings."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        log.error("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY env vars")
        sys.exit(1)

    sb = create_client(url, key)

    # --- Delete existing data ---
    log.info("Deleting old rankings...")
    try:
        sb.table("rankings").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        log.info("Old rankings deleted")
    except Exception as e:
        log.warning("Failed to delete rankings: %s", e)

    log.info("Deleting old players...")
    try:
        sb.table("players").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        log.info("Old players deleted")
    except Exception as e:
        log.warning("Failed to delete players: %s", e)

    # --- Insert players ---
    player_rows = []
    for p in players:
        player_rows.append({
            "slug": p["slug"],
            "name": p["name"],
            "country": p["country"],
            "sponsor": p.get("sponsor", ""),
            "paddle": p.get("paddle", ""),
            "bio": p.get("bio", ""),
            "photo_url": p.get("photo_url", ""),
        })

    if player_rows:
        log.info("Inserting %d players...", len(player_rows))
        for i in range(0, len(player_rows), 50):
            chunk = player_rows[i:i + 50]
            sb.table("players").upsert(chunk, on_conflict="slug").execute()
            log.info("  Upserted players %d-%d", i + 1, min(i + 50, len(player_rows)))
        log.info("All players inserted OK")

    # --- Resolve player IDs for rankings ---
    slugs = [p["slug"] for p in players]
    slug_to_id = {}
    for i in range(0, len(slugs), 50):
        chunk = slugs[i:i + 50]
        result = sb.table("players").select("id, slug").in_("slug", chunk).execute()
        for r in result.data:
            slug_to_id[r["slug"]] = r["id"]
    log.info("Resolved %d player IDs", len(slug_to_id))

    # --- Insert rankings ---
    ranking_rows = []
    for r in rankings:
        pid = slug_to_id.get(r["player_slug"])
        if not pid:
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
        log.info("Inserting %d rankings...", len(ranking_rows))
        for i in range(0, len(ranking_rows), 50):
            chunk = ranking_rows[i:i + 50]
            sb.table("rankings").insert(chunk).execute()
            log.info("  Inserted rankings %d-%d", i + 1, min(i + 50, len(ranking_rows)))
        log.info("All rankings inserted OK")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    dry_run = "--dry-run" in sys.argv

    log.info("=" * 60)
    log.info("PPA Tour Player Crawler")
    log.info("Mode: %s", "DRY RUN" if dry_run else "LIVE")
    log.info("=" * 60)

    # Step 1: Fetch taxonomies
    log.info("--- Step 1: Fetching taxonomies ---")
    countries, sponsors, divisions = fetch_taxonomies()

    # Step 2: Fetch all athletes
    log.info("--- Step 2: Fetching all athletes ---")
    raw_athletes = fetch_all_athletes()

    if not raw_athletes:
        log.error("No athletes fetched! Aborting.")
        sys.exit(1)

    # Step 3: Resolve media URLs (batch)
    log.info("--- Step 3: Fetching media URLs ---")
    media_ids = [a.get("featured_media", 0) for a in raw_athletes]
    media_map = fetch_media_urls(media_ids)

    # Step 4: Process athletes
    log.info("--- Step 4: Processing athletes ---")
    players, division_members = process_athletes(
        raw_athletes, countries, sponsors, divisions, media_map
    )

    # Step 5: Generate rankings
    log.info("--- Step 5: Generating rankings ---")
    rankings = generate_rankings(players, division_members)

    # Summary
    photo_count = sum(1 for p in players if p["photo_url"])
    country_count = sum(1 for p in players if p["country"])
    sponsor_count = sum(1 for p in players if p["sponsor"])

    log.info("=" * 60)
    log.info("SUMMARY")
    log.info("  Total athletes: %d", len(players))
    log.info("  With photos: %d", photo_count)
    log.info("  With country: %d", country_count)
    log.info("  With sponsor: %d", sponsor_count)
    log.info("  Rankings generated: %d", len(rankings))
    log.info("  Divisions: %s", ", ".join(division_members.keys()))
    log.info("=" * 60)

    if dry_run:
        log.info("DRY RUN -- not saving to Supabase")
        for p in players[:5]:
            log.info("  %s (%s) - %s - %s", p["name"], p["country"],
                     p["sponsor"], p["photo_url"])
        return

    # Step 6: Save to Supabase
    log.info("--- Step 6: Saving to Supabase ---")
    save_to_supabase(players, rankings)

    log.info("=" * 60)
    log.info("DONE! %d players saved, %d rankings generated.",
             len(players), len(rankings))
    log.info("=" * 60)


if __name__ == "__main__":
    main()
