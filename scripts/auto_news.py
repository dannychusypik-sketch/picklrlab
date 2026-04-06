#!/usr/bin/env python3
"""
AI-powered auto article writer using Claude API.
Reads raw news JSON, generates full articles, saves to Supabase.
Usage: python auto_news.py --input /tmp/news_raw.json
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone

import anthropic
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
MAX_ARTICLES_PER_RUN = 5
DELAY_BETWEEN_CALLS = 2  # seconds
CLAUDE_MODEL = "claude-sonnet-4-20250514"

ARTICLE_PROMPT = """\
You are a professional pickleball sports journalist writing for PicklrLab.com.

Based on this news headline and snippet, write a complete article.

Headline: {title}
Source: {source_name}
Snippet: {snippet}
Category: {category}

Respond in EXACTLY this JSON format (no markdown, just raw JSON):
{{
  "title": "SEO-optimized article title (may differ from headline)",
  "excerpt": "1-2 sentence summary for article cards",
  "content": "<p>Paragraph 1...</p><p>Paragraph 2...</p><p>Paragraph 3...</p><p>Paragraph 4...</p>",
  "meta_description": "Meta description for SEO (under 160 chars)",
  "category": "{category}"
}}

Requirements:
- Title should be catchy and SEO-friendly
- Content should be 300-400 words in HTML <p> tags
- Write in an engaging, informative tone
- Include context about pickleball for newer fans
- Do not fabricate specific statistics or quotes
- Keep the excerpt to 1-2 concise sentences
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
# Article generation
# ---------------------------------------------------------------------------
def generate_article(client: anthropic.Anthropic, news_item: dict) -> dict | None:
    """Call Claude to generate a full article from a news item."""
    prompt = ARTICLE_PROMPT.format(
        title=news_item["title"],
        source_name=news_item.get("source_name", "Unknown"),
        snippet=news_item.get("snippet", ""),
        category=news_item.get("category", "general"),
    )

    try:
        log.info("Generating article for: %s", news_item["title"][:60])
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text.strip()

        # Try to parse JSON from response
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
                log.warning("Missing field '%s' in generated article", field)
                return None

        # Add slug
        article["slug"] = slugify(article["title"])

        return article

    except json.JSONDecodeError as exc:
        log.error("Failed to parse Claude response as JSON: %s", exc)
        return None
    except anthropic.APIError as exc:
        log.error("Claude API error: %s", exc)
        return None
    except Exception as exc:
        log.error("Unexpected error generating article: %s", exc)
        return None


def check_duplicate(sb, slug: str) -> bool:
    """Check if article with this slug already exists."""
    try:
        result = sb.table("articles").select("id").eq("slug", slug).limit(1).execute()
        return len(result.data) > 0
    except Exception:
        return False


def save_article(sb, article: dict, source_url: str):
    """Save generated article to Supabase."""
    now = datetime.now(timezone.utc).isoformat()

    row = {
        "title": article["title"],
        "slug": article["slug"],
        "excerpt": article["excerpt"],
        "content": article["content"],
        "meta_description": article["meta_description"],
        "category": article["category"],
        "source_url": source_url,
        "status": "published",
        "auto_generated": True,
        "published_at": now,
        "created_at": now,
        "updated_at": now,
    }

    try:
        sb.table("articles").upsert(row, on_conflict="slug").execute()
        log.info("Saved article: %s", article["slug"])
        return True
    except Exception as exc:
        log.error("Failed to save article: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Auto-generate pickleball articles")
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to raw news JSON file (from scrape_news.py)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate articles but don't save to Supabase",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=MAX_ARTICLES_PER_RUN,
        help=f"Max articles per run (default: {MAX_ARTICLES_PER_RUN})",
    )
    args = parser.parse_args()

    log.info("=== auto_news.py starting ===")

    # Load raw news
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            news_items = json.load(f)
    except Exception as exc:
        log.error("Failed to load input file %s: %s", args.input, exc)
        sys.exit(1)

    log.info("Loaded %d news items from %s", len(news_items), args.input)

    claude = get_claude()
    sb = None if args.dry_run else get_supabase()

    generated = 0
    skipped = 0

    for item in news_items:
        if generated >= args.max:
            log.info("Reached max articles (%d), stopping", args.max)
            break

        # Check for duplicate
        slug_preview = slugify(item["title"])
        if not args.dry_run and check_duplicate(sb, slug_preview):
            log.info("Skipping duplicate: %s", slug_preview)
            skipped += 1
            continue

        article = generate_article(claude, item)
        if not article:
            skipped += 1
            continue

        if args.dry_run:
            log.info("  [DRY RUN] Title: %s", article["title"])
            log.info("  [DRY RUN] Slug: %s", article["slug"])
            log.info("  [DRY RUN] Excerpt: %s", article["excerpt"][:100])
            log.info("  [DRY RUN] Content length: %d chars", len(article["content"]))
        else:
            # Check again with the final slug (may differ from preview)
            if check_duplicate(sb, article["slug"]):
                log.info("Skipping duplicate (final slug): %s", article["slug"])
                skipped += 1
                continue
            save_article(sb, article, item.get("source_url", ""))

        generated += 1

        # Rate limiting
        if generated < args.max:
            log.info("Waiting %ds before next API call...", DELAY_BETWEEN_CALLS)
            time.sleep(DELAY_BETWEEN_CALLS)

    log.info("Generated %d articles, skipped %d", generated, skipped)
    log.info("=== auto_news.py done ===")


if __name__ == "__main__":
    main()
