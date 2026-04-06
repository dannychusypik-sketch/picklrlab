#!/usr/bin/env python3
"""
Generate 20 high-quality SEO-optimized articles for PicklrLab using Claude API.
Saves directly to Supabase with proper metadata.

Usage: python3 generate_batch_articles.py [--dry-run]

Env vars required: SUPABASE_URL, SUPABASE_SERVICE_KEY, ANTHROPIC_API_KEY
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
DELAY_BETWEEN_CALLS = 4  # seconds
MIN_SEO_SCORE = 85

# ---------------------------------------------------------------------------
# 20 Article Topics
# ---------------------------------------------------------------------------
TOPICS = [
    {
        "title": "Ben Johns Dominates PPA Tour 2025: Complete Season Analysis",
        "category": "tournament",
        "image": "tournament-01.jpg",
    },
    {
        "title": "Top 10 Pickleball Paddles of 2025: Lab-Tested Rankings",
        "category": "review",
        "image": "gear-01.jpg",
    },
    {
        "title": "Anna Leigh Waters: The Making of Pickleball's Youngest Champion",
        "category": "tournament",
        "image": "pickleball-01.jpg",
    },
    {
        "title": "Complete Beginner's Guide to Pickleball: Rules, Gear, and Tips",
        "category": "training",
        "image": "training-01.jpg",
    },
    {
        "title": "PPA Tour Rankings April 2025: 15 Major Position Changes",
        "category": "rankings",
        "image": "rankings-01.jpg",
    },
    {
        "title": "JOOLA Perseus Carbon 14mm Review: Why Pros Love This Paddle",
        "category": "review",
        "image": "gear-02.jpg",
    },
    {
        "title": "Vietnam Pickleball Explosion: 500% Growth in Two Years",
        "category": "vietnam",
        "image": "vietnam-01.jpg",
    },
    {
        "title": "5 Dinking Drills That Will Transform Your Kitchen Game",
        "category": "training",
        "image": "training-02.jpg",
    },
    {
        "title": "MLP 2025 Season Preview: Teams, Players, and Predictions",
        "category": "tournament",
        "image": "tournament-02.jpg",
    },
    {
        "title": "Selkirk vs JOOLA: Which Pro Paddle Brand Wins in 2025?",
        "category": "review",
        "image": "gear-01.jpg",
    },
    {
        "title": "Southeast Asia Pickleball Championships: Full Results and Analysis",
        "category": "sea",
        "image": "sea-01.jpg",
    },
    {
        "title": "How to Master the Third Shot Drop: Pro Tips and Drills",
        "category": "training",
        "image": "training-03.jpg",
    },
    {
        "title": "Pickleball Court Construction Guide: Costs, Materials, and Design",
        "category": "gear",
        "image": "pickleball-03.jpg",
    },
    {
        "title": "Christian Alshon's Rise: From Unknown to Top 10 in One Season",
        "category": "tournament",
        "image": "tournament-03.jpg",
    },
    {
        "title": "Carbon Fiber vs Fiberglass Paddles: Complete Comparison Guide",
        "category": "review",
        "image": "gear-02.jpg",
    },
    {
        "title": "Pickleball Scoring System Explained: Traditional vs Rally Scoring",
        "category": "training",
        "image": "pickleball-04.jpg",
    },
    {
        "title": "Federico Staksrud: Argentina's Gift to Professional Pickleball",
        "category": "tournament",
        "image": "pickleball-02.jpg",
    },
    {
        "title": "Best Pickleball Courts in Southeast Asia: A Complete Guide",
        "category": "sea",
        "image": "sea-01.jpg",
    },
    {
        "title": "How Pickleball Became America's Fastest Growing Sport in 2025",
        "category": "opinion",
        "image": "news-01.jpg",
    },
    {
        "title": "Pickleball Injury Prevention: 7 Essential Stretches and Warmups",
        "category": "training",
        "image": "training-01.jpg",
    },
]

# ---------------------------------------------------------------------------
# Authors (rotate for variety)
# ---------------------------------------------------------------------------
AUTHORS = [
    "PicklrLab Editorial",
    "Sarah Chen",
    "Marcus Rodriguez",
    "PicklrLab Editorial",
    "Jake Thompson",
]

# ---------------------------------------------------------------------------
# SEO-Optimized Claude Prompt (from auto_news.py)
# ---------------------------------------------------------------------------
ARTICLE_PROMPT = """\
You are a senior pickleball journalist and SEO content strategist writing for PicklrLab.com — \
a trusted authority on pickleball news, rankings, gear reviews, and training tips.

Write a COMPREHENSIVE, SEO-optimized article on this topic:

Topic: {title}
Category: {category}

Respond in EXACTLY this JSON format (no markdown fences, just raw JSON):
{{
  "title": "SEO title here (50-60 characters, include primary keyword)",
  "excerpt": "1-2 compelling sentences that hook the reader and include a call-to-action hint",
  "meta_description": "Meta description for SEO, 150-160 chars, include primary keyword and CTA",
  "content": "FULL HTML content here (see requirements below)",
  "category": "{category}"
}}

=== CONTENT REQUIREMENTS (800-1200 words) ===

1. STRUCTURE — Use proper semantic HTML:
   - Opening hook paragraph (2-3 sentences that grab attention)
   - 3-5 H2 subheadings that break the article into scannable sections
   - Use H3 for sub-sections where appropriate
   - Use <ul> or <ol> lists for key points, stats, or tips
   - Use <blockquote> for notable quotes or key takeaways
   - Use <strong> and <em> for emphasis on important terms

2. HTML FORMAT — Use these tags:
   <h2>Section Heading</h2>
   <h3>Sub-section</h3>
   <p>Paragraph text</p>
   <ul><li>Bullet point</li></ul>
   <ol><li>Numbered item</li></ol>
   <blockquote><p>Key takeaway or quote</p></blockquote>

3. SEO BEST PRACTICES:
   - Include the primary keyword in the first 100 words
   - Use related keywords naturally throughout (pickleball, paddle, court, tournament, etc.)
   - Include approximate stats or numbers where relevant (e.g., "over 36 million players")
   - Add 1-2 internal linking suggestions as regular text like: \
"For the latest player standings, check our rankings page." or \
"See our in-depth paddle reviews for more gear analysis."

4. FAQ SECTION — End with exactly 3 Q&A pairs using this HTML:
   <h2>Frequently Asked Questions</h2>
   <details><summary>Question 1 here?</summary><p>Answer 1 here.</p></details>
   <details><summary>Question 2 here?</summary><p>Answer 2 here.</p></details>
   <details><summary>Question 3 here?</summary><p>Answer 3 here.</p></details>

5. TONE & STYLE:
   - Write like an experienced sports journalist, NOT like an AI
   - Be authoritative but conversational
   - Use active voice
   - Include context for newer pickleball fans
   - Vary sentence length — mix short punchy lines with longer explanatory ones
   - Avoid generic filler phrases like "In conclusion" or "It's worth noting"
   - Do NOT fabricate specific quotes, but you may reference well-known facts

6. LENGTH: Aim for 800-1200 words. The content field should be substantial.
"""


# ---------------------------------------------------------------------------
# SEO Score Checker
# ---------------------------------------------------------------------------
def calculate_seo_score(article):
    # type: (Dict) -> int
    """Calculate a simple SEO score (0-100) for the article."""
    score = 0
    content = article.get("content", "")
    title = article.get("title", "")
    excerpt = article.get("excerpt", "")
    meta_desc = article.get("meta_description", "")

    # Title length (50-60 chars ideal)
    title_len = len(title)
    if 45 <= title_len <= 65:
        score += 15
    elif 35 <= title_len <= 75:
        score += 10
    else:
        score += 5

    # Word count (800+ words)
    text_only = re.sub(r"<[^>]+>", "", content)
    word_count = len(text_only.split())
    if word_count >= 800:
        score += 20
    elif word_count >= 600:
        score += 15
    elif word_count >= 400:
        score += 10
    else:
        score += 5

    # H2 headings (3+ ideal)
    h2_count = content.count("<h2>")
    if h2_count >= 3:
        score += 15
    elif h2_count >= 2:
        score += 10
    else:
        score += 5

    # FAQ section present
    if "<details>" in content and "<summary>" in content:
        score += 15
    else:
        score += 0

    # Meta description (150-160 chars)
    meta_len = len(meta_desc)
    if 140 <= meta_len <= 165:
        score += 10
    elif 100 <= meta_len <= 200:
        score += 7
    else:
        score += 3

    # Has excerpt
    if len(excerpt) > 30:
        score += 5

    # Uses lists (<ul> or <ol>)
    if "<ul>" in content or "<ol>" in content:
        score += 5

    # Uses blockquote
    if "<blockquote>" in content:
        score += 5

    # Uses strong/em
    if "<strong>" in content or "<em>" in content:
        score += 5

    # Internal linking mentions
    if "rankings" in content.lower() or "reviews" in content.lower() or "check our" in content.lower():
        score += 5

    return min(score, 100)


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
# Article Generation
# ---------------------------------------------------------------------------
def generate_article(client, topic):
    # type: (anthropic.Anthropic, Dict) -> Optional[Dict]
    """Call Claude to generate a full SEO-optimized article."""
    prompt = ARTICLE_PROMPT.format(
        title=topic["title"],
        category=topic["category"],
    )

    try:
        log.info("Generating: %s", topic["title"][:70])
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4000,
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
                log.warning("Missing field '%s' in generated article", field)
                return None

        return article

    except json.JSONDecodeError as exc:
        log.error("Failed to parse Claude response as JSON: %s", exc)
        log.error("Response preview: %s", response_text[:200] if response_text else "empty")
        return None
    except anthropic.APIError as exc:
        log.error("Claude API error: %s", exc)
        return None
    except Exception as exc:
        log.error("Unexpected error: %s", exc)
        return None


def check_duplicate(sb, slug):
    # type: (object, str) -> bool
    """Check if article with this slug already exists."""
    try:
        result = sb.table("articles").select("id").eq("slug", slug).limit(1).execute()
        return len(result.data) > 0
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    dry_run = "--dry-run" in sys.argv

    log.info("=== PicklrLab Batch Article Generator ===")
    log.info("Mode: %s", "DRY RUN" if dry_run else "LIVE (saving to Supabase)")
    log.info("Articles to generate: %d", len(TOPICS))

    claude = get_claude()
    sb = None if dry_run else get_supabase()

    # Generate published_at dates spread across last 30 days
    now = datetime.now(timezone.utc)
    date_offsets = sorted(random.sample(range(1, 31), len(TOPICS)), reverse=True)

    generated = 0
    failed = 0

    for idx, topic in enumerate(TOPICS):
        log.info("\n--- Article %d/%d ---", idx + 1, len(TOPICS))

        # Generate article via Claude
        article = generate_article(claude, topic)
        if not article:
            log.error("Failed to generate article for: %s", topic["title"])
            failed += 1
            time.sleep(DELAY_BETWEEN_CALLS)
            continue

        # Add slug
        slug = slugify(article["title"])
        article["slug"] = slug

        # Prepend hero image
        image_path = "/images/articles/%s" % topic["image"]
        alt_text = article["title"].replace('"', "&quot;")
        image_html = (
            '<img src="%s" alt="%s" '
            'width="800" height="450" '
            'style="width:100%%;height:auto;border-radius:8px;margin-bottom:1.5rem;" '
            'loading="lazy" />'
        ) % (image_path, alt_text)
        article["content"] = image_html + "\n" + article["content"]

        # Calculate SEO score
        seo_score = calculate_seo_score(article)
        word_count = len(re.sub(r"<[^>]+>", "", article["content"]).split())
        h2_count = article["content"].count("<h2>")
        has_faq = "<details>" in article["content"]

        log.info("  Title: %s (%d chars)", article["title"], len(article["title"]))
        log.info("  Words: %d | H2s: %d | FAQ: %s | SEO Score: %d/100",
                 word_count, h2_count, has_faq, seo_score)

        if seo_score < MIN_SEO_SCORE:
            log.warning("  SEO score %d < %d minimum, SKIPPING", seo_score, MIN_SEO_SCORE)
            failed += 1
            time.sleep(DELAY_BETWEEN_CALLS)
            continue

        # Prepare row for Supabase
        published_at = (now - timedelta(days=date_offsets[idx])).isoformat()
        is_featured = idx < 3  # First 3 articles are featured
        author = AUTHORS[idx % len(AUTHORS)]
        views = random.randint(100, 5000)

        row = {
            "title": article["title"],
            "slug": slug,
            "excerpt": article["excerpt"],
            "content": article["content"],
            "category": topic["category"],
            "author": author,
            "published_at": published_at,
            "is_featured": is_featured,
            "views": views,
            "image_url": image_path,
        }

        # Add meta_description and schema_json if the table supports them
        if "meta_description" in article:
            row["meta_description"] = article["meta_description"]

        if dry_run:
            log.info("  [DRY RUN] Slug: %s", slug)
            log.info("  [DRY RUN] Author: %s | Views: %d | Featured: %s",
                     author, views, is_featured)
            log.info("  [DRY RUN] Published: %s", published_at)
            log.info("  [DRY RUN] Image: %s", image_path)
            log.info("  [DRY RUN] Excerpt: %s", article["excerpt"][:100])
        else:
            # Check for duplicate
            if check_duplicate(sb, slug):
                log.info("  Duplicate slug found, skipping: %s", slug)
                failed += 1
                time.sleep(DELAY_BETWEEN_CALLS)
                continue

            try:
                sb.table("articles").upsert(row, on_conflict="slug").execute()
                log.info("  SAVED to Supabase: %s", slug)
            except Exception as exc:
                log.error("  Failed to save: %s", exc)
                # Retry without optional fields that might not exist in table
                try:
                    for optional_field in ["meta_description", "schema_json"]:
                        row.pop(optional_field, None)
                    sb.table("articles").upsert(row, on_conflict="slug").execute()
                    log.info("  SAVED (without optional fields): %s", slug)
                except Exception as exc2:
                    log.error("  Retry also failed: %s", exc2)
                    failed += 1
                    time.sleep(DELAY_BETWEEN_CALLS)
                    continue

        generated += 1

        # Rate limiting between API calls
        if idx < len(TOPICS) - 1:
            log.info("  Waiting %ds...", DELAY_BETWEEN_CALLS)
            time.sleep(DELAY_BETWEEN_CALLS)

    log.info("\n=== DONE ===")
    log.info("Generated: %d | Failed/Skipped: %d | Total: %d",
             generated, failed, len(TOPICS))

    if generated > 0 and not dry_run:
        log.info("Articles are live on PicklrLab! Check Supabase to verify.")


if __name__ == "__main__":
    main()
