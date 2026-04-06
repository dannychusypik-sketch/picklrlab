#!/usr/bin/env python3
"""
AI-powered auto article writer using Claude API.
Reads raw news JSON, generates HIGH QUALITY SEO-optimized articles, saves to Supabase.
Usage: python auto_news.py --input /tmp/news_raw.json
"""

import argparse
import hashlib
import json
import logging
import os
import random
import re
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

import anthropic
from slugify import slugify
from supabase import create_client

from download_article_image import download_image

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
MAX_ARTICLES_PER_RUN = 3
DELAY_BETWEEN_CALLS = 3  # seconds
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# ---------------------------------------------------------------------------
# Curated Unsplash Images by Category
# ---------------------------------------------------------------------------
CATEGORY_IMAGES = {
    "tournament": [
        "https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=800&h=450&fit=crop",
        "https://images.unsplash.com/photo-1461896836934-bd45ba8f8e32?w=800&h=450&fit=crop",
        "https://images.unsplash.com/photo-1530549387789-4c1017266635?w=800&h=450&fit=crop",
    ],
    "training": [
        "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=800&h=450&fit=crop",
        "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=800&h=450&fit=crop",
    ],
    "review": [
        "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=800&h=450&fit=crop",
        "https://images.unsplash.com/photo-1612872087720-bb876e2e67d1?w=800&h=450&fit=crop",
    ],
    "gear": [
        "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=800&h=450&fit=crop",
        "https://images.unsplash.com/photo-1612872087720-bb876e2e67d1?w=800&h=450&fit=crop",
    ],
    "rankings": [
        "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=800&h=450&fit=crop",
        "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=450&fit=crop",
    ],
    "vietnam": [
        "https://images.unsplash.com/photo-1557750255-c76072a7aad1?w=800&h=450&fit=crop",
    ],
    "sea": [
        "https://images.unsplash.com/photo-1540611025311-01df3cde54b5?w=800&h=450&fit=crop",
    ],
    "opinion": [
        "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=800&h=450&fit=crop",
    ],
}

DEFAULT_IMAGES = [
    "https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=800&h=450&fit=crop",
    "https://images.unsplash.com/photo-1530549387789-4c1017266635?w=800&h=450&fit=crop",
    "https://images.unsplash.com/photo-1461896836934-bd45ba8f8e32?w=800&h=450&fit=crop",
]


# ---------------------------------------------------------------------------
# SEO-Optimized Claude Prompt
# ---------------------------------------------------------------------------
ARTICLE_PROMPT = """\
You are a senior pickleball journalist and SEO content strategist writing for PicklrLab.com — \
a trusted authority on pickleball news, rankings, gear reviews, and training tips.

Write a COMPREHENSIVE, SEO-optimized article based on this news source:

Headline: {title}
Source: {source_name}
Snippet: {snippet}
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
# Image Selection
# ---------------------------------------------------------------------------
def fetch_thumbnail(category, title, source_image="", slug=""):
    # type: (str, str, str, str) -> str
    """
    Download the source image locally if available; fall back to stock images.
    Returns a local path like /images/articles/slug.jpg or an Unsplash URL.
    """
    # Try to download the actual source image first
    if source_image and slug:
        local_path = download_image(source_image, slug)
        if local_path:
            return local_path

    # Fallback: use stock category images
    images = CATEGORY_IMAGES.get(category, DEFAULT_IMAGES)
    title_hash = int(hashlib.md5(title.encode()).hexdigest(), 16)
    idx = title_hash % len(images)
    return images[idx]


# ---------------------------------------------------------------------------
# JSON-LD Schema
# ---------------------------------------------------------------------------
def generate_schema_json(article: Dict, image_url: str) -> str:
    """Generate Article schema JSON-LD for SEO."""
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article["title"],
        "description": article.get("meta_description", article.get("excerpt", "")),
        "image": image_url,
        "author": {
            "@type": "Organization",
            "name": "PicklrLab Editorial",
            "url": "https://picklrlab.com",
        },
        "publisher": {
            "@type": "Organization",
            "name": "PicklrLab",
            "url": "https://picklrlab.com",
            "logo": {
                "@type": "ImageObject",
                "url": "https://picklrlab.com/logo.png",
            },
        },
        "datePublished": datetime.now(timezone.utc).isoformat(),
        "dateModified": datetime.now(timezone.utc).isoformat(),
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": "https://picklrlab.com/news/" + article.get("slug", ""),
        },
    }

    # Add FAQ schema if content has FAQ section
    if "<details>" in article.get("content", ""):
        faq_items = []
        # Extract Q&A from details/summary tags
        faq_pattern = r"<summary>(.*?)</summary>\s*<p>(.*?)</p>"
        matches = re.findall(faq_pattern, article["content"], re.DOTALL)
        for question, answer in matches:
            faq_items.append({
                "@type": "Question",
                "name": question.strip(),
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": answer.strip(),
                },
            })
        if faq_items:
            schema["@type"] = ["Article", "FAQPage"]
            schema["mainEntity"] = faq_items

    return json.dumps(schema, ensure_ascii=False)


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
def generate_article(client, news_item: Dict) -> Optional[Dict]:
    """Call Claude to generate a full SEO-optimized article from a news item."""
    category = news_item.get("category", "general")
    prompt = ARTICLE_PROMPT.format(
        title=news_item["title"],
        source_name=news_item.get("source", news_item.get("source_name", "Unknown")),
        snippet=news_item.get("excerpt", news_item.get("snippet", "")),
        category=category,
    )

    try:
        log.info("Generating SEO article for: %s", news_item["title"][:60])
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4000,  # increased for longer articles
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

        # Add slug
        article["slug"] = slugify(article["title"])

        # Select and prepend thumbnail image (prefer source image)
        source_image = news_item.get("source_image", "")
        image_url = fetch_thumbnail(
            category, article["title"],
            source_image=source_image,
            slug=article["slug"],
        )
        alt_text = article["title"].replace('"', "&quot;")
        image_html = (
            '<img src="{url}" alt="{alt}" '
            'width="800" height="450" '
            'style="width:100%;height:auto;border-radius:8px;margin-bottom:1.5rem;" '
            'loading="lazy" />'
        ).format(url=image_url, alt=alt_text)
        article["content"] = image_html + "\n" + article["content"]

        # Embed video after first paragraph if source has video_url
        video_url = news_item.get("video_url", "")
        if video_url:
            video_html = (
                '<div class="video-embed">'
                '<iframe src="{src}" width="100%" height="400" '
                'frameborder="0" allowfullscreen></iframe>'
                '</div>'
            ).format(src=video_url)
            # Insert after first </p> tag
            first_p_end = article["content"].find("</p>")
            if first_p_end != -1:
                insert_pos = first_p_end + len("</p>")
                article["content"] = (
                    article["content"][:insert_pos]
                    + "\n" + video_html + "\n"
                    + article["content"][insert_pos:]
                )
            else:
                article["content"] = article["content"] + "\n" + video_html

        # Generate JSON-LD schema
        article["schema_json"] = generate_schema_json(article, image_url)
        article["image_url"] = image_url

        # Log quality stats
        word_count = len(re.sub(r"<[^>]+>", "", article["content"]).split())
        h2_count = article["content"].count("<h2>")
        has_faq = "<details>" in article["content"]
        log.info(
            "  Quality: %d words, %d H2s, FAQ=%s, title=%d chars",
            word_count, h2_count, has_faq, len(article["title"]),
        )

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


def save_article(sb, article: Dict, source_url: str) -> bool:
    """Save generated article to Supabase."""
    now = datetime.now(timezone.utc).isoformat()

    row = {
        "title": article["title"],
        "slug": article["slug"],
        "excerpt": article["excerpt"],
        "content": article["content"],
        "category": article["category"],
        "image_url": article.get("image_url", ""),
        "author": "PicklrLab Editorial",
        "published_at": now,
        "is_featured": False,
        "views": 0,
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
    parser = argparse.ArgumentParser(description="Auto-generate SEO-optimized pickleball articles")
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
        help="Max articles per run (default: %d)" % MAX_ARTICLES_PER_RUN,
    )
    args = parser.parse_args()

    log.info("=== auto_news.py v2 (SEO Pipeline) starting ===")

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

        # Check for duplicate by preview slug
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
            log.info("  [DRY RUN] Image: %s", article.get("image_url", "N/A"))
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
    log.info("=== auto_news.py v2 done ===")


if __name__ == "__main__":
    main()
