#!/usr/bin/env python3
"""
Generate HOT pickleball articles from crawled news data.
Prioritizes tournaments, controversies, gear news over training tips.
Saves to Supabase with featured flags, varied views, and spread dates.

Usage:
    SUPABASE_URL=... SUPABASE_SERVICE_KEY=... ANTHROPIC_API_KEY=... python3 generate_hot_articles.py
"""

import hashlib
import json
import logging
import os
import random
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

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
INPUT_FILE = "/tmp/news_hot.json"
TOTAL_ARTICLES = 20
DELAY_BETWEEN_CALLS = 4  # seconds
CLAUDE_MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4000

# Priority order for category selection
CATEGORY_PRIORITY = [
    # (category_list, max_count, label)
    (["tournament"], 6, "Tournament/Controversy"),
    (["rankings"], 3, "Player/Rankings"),
    (["review", "gear"], 4, "Gear/Reviews"),
    (["opinion"], 2, "Business/Opinion"),
    (["vietnam", "sea"], 2, "Vietnam/SEA"),
    (["training"], 3, "Training/Tips"),
]

# ---------------------------------------------------------------------------
# Curated Unsplash Images by Category (fallback)
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
# SEO-Optimized Claude Prompt (enhanced for hot topics)
# ---------------------------------------------------------------------------
ARTICLE_PROMPT = """\
You are a senior pickleball journalist and SEO content strategist writing for PicklrLab.com — \
a trusted authority on pickleball news, rankings, gear reviews, and training tips.

Write a COMPREHENSIVE, SEO-optimized article based on this news source:

Headline: {title}
Source: {source_name}
Snippet: {snippet}
Category: {category}

IMPORTANT INSTRUCTIONS:
- Write about the LATEST developments. Include specific names, dates, and details.
- If this is about a controversy or scandal, be balanced but engaging.
- Make the content feel FRESH and TIMELY — reference current season/year (2026).
- Include real player names, tournament names, and specific details from the source.

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
# Article selection — prioritize hot topics
# ---------------------------------------------------------------------------
def select_articles(all_articles, total=20):
    # type: (List[Dict], int) -> List[Dict]
    """Select articles prioritizing hot topics over training."""
    selected = []  # type: List[Dict]
    used_titles = set()  # type: set

    def title_key(title):
        # type: (str) -> str
        return re.sub(r'[^a-z0-9\s]', '', title.lower())[:50].strip()

    for cat_list, max_count, label in CATEGORY_PRIORITY:
        if len(selected) >= total:
            break

        # Find articles matching this category group
        candidates = []
        for a in all_articles:
            if a["category"] in cat_list:
                key = title_key(a["title"])
                if key not in used_titles:
                    candidates.append(a)

        # Prioritize articles with images and videos
        candidates.sort(key=lambda x: (
            bool(x.get("video_url")),
            bool(x.get("source_image")),
        ), reverse=True)

        count = 0
        for a in candidates:
            if count >= max_count or len(selected) >= total:
                break
            key = title_key(a["title"])
            used_titles.add(key)
            selected.append(a)
            count += 1

        log.info("Selected %d/%d for %s", count, max_count, label)

    # If we still need more, fill from remaining
    if len(selected) < total:
        for a in all_articles:
            if len(selected) >= total:
                break
            key = title_key(a["title"])
            if key not in used_titles:
                used_titles.add(key)
                selected.append(a)

    log.info("Total selected: %d articles", len(selected))
    return selected


# ---------------------------------------------------------------------------
# Image handling
# ---------------------------------------------------------------------------
def fetch_thumbnail(category, title, source_image="", slug=""):
    # type: (str, str, str, str) -> str
    """Download source image or fall back to stock."""
    if source_image and slug:
        local_path = download_image(source_image, slug)
        if local_path:
            return local_path

    images = CATEGORY_IMAGES.get(category, DEFAULT_IMAGES)
    title_hash = int(hashlib.md5(title.encode()).hexdigest(), 16)
    idx = title_hash % len(images)
    return images[idx]


# ---------------------------------------------------------------------------
# JSON-LD Schema
# ---------------------------------------------------------------------------
def generate_schema_json(article, image_url):
    # type: (Dict, str) -> str
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

    if "<details>" in article.get("content", ""):
        faq_items = []
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
def generate_article(client, news_item):
    # type: (anthropic.Anthropic, Dict) -> Optional[Dict]
    """Call Claude to generate a full SEO-optimized article."""
    category = news_item.get("category", "tournament")
    prompt = ARTICLE_PROMPT.format(
        title=news_item["title"],
        source_name=news_item.get("source", "Unknown"),
        snippet=news_item.get("excerpt", ""),
        category=category,
    )

    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text.strip()

        # Handle markdown code fences
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

        # Download/select thumbnail image
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

        # Embed video after first paragraph if available
        video_url = news_item.get("video_url", "")
        if video_url:
            video_html = (
                '<div class="video-embed">'
                '<iframe src="{src}" width="100%" height="400" '
                'frameborder="0" allowfullscreen></iframe>'
                '</div>'
            ).format(src=video_url)
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


# ---------------------------------------------------------------------------
# Save to Supabase
# ---------------------------------------------------------------------------
def save_article(sb, article, index, total):
    # type: (...) -> bool
    """Save article to Supabase with tiered featured/views/dates."""
    now = datetime.now(timezone.utc)

    # Spread published_at across last 14 days
    days_back = int((index / max(total - 1, 1)) * 13)  # 0 to 13 days back
    hours_offset = random.randint(0, 23)
    minutes_offset = random.randint(0, 59)
    pub_date = now - timedelta(days=days_back, hours=hours_offset, minutes=minutes_offset)

    # Tiered featured/views
    if index < 5:
        is_featured = True
        views = random.randint(2000, 8000)
    elif index < 15:
        is_featured = False
        views = random.randint(500, 2000)
    else:
        is_featured = False
        views = random.randint(100, 500)

    row = {
        "title": article["title"],
        "slug": article["slug"],
        "excerpt": article["excerpt"],
        "content": article["content"],
        "category": article["category"],
        "image_url": article.get("image_url", ""),
        "author": "PicklrLab Editorial",
        "published_at": pub_date.isoformat(),
        "is_featured": is_featured,
        "views": views,
    }

    try:
        sb.table("articles").upsert(row, on_conflict="slug").execute()
        return True
    except Exception as exc:
        log.error("Failed to save article: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    log.info("=" * 60)
    log.info("  GENERATE HOT ARTICLES — PicklrLab")
    log.info("=" * 60)

    # Load crawled news
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            all_articles = json.load(f)
    except Exception as exc:
        log.error("Failed to load %s: %s", INPUT_FILE, exc)
        sys.exit(1)

    log.info("Loaded %d crawled articles from %s", len(all_articles), INPUT_FILE)

    # Select prioritized articles
    selected = select_articles(all_articles, TOTAL_ARTICLES)

    if not selected:
        log.error("No articles selected!")
        sys.exit(1)

    # Show selection preview
    log.info("\n--- SELECTED ARTICLES ---")
    for i, a in enumerate(selected):
        vid = " [VIDEO]" if a.get("video_url") else ""
        img = " [IMG]" if a.get("source_image") else ""
        log.info("  %2d. [%s] %s%s%s", i + 1, a["category"], a["title"][:65], img, vid)

    # Initialize clients
    claude = get_claude()
    sb = get_supabase()

    # Generate and save
    generated = 0
    failed = 0
    category_counts = {}  # type: Dict[str, int]

    for i, news_item in enumerate(selected):
        idx = i + 1
        title_preview = news_item["title"][:55]
        log.info("\n[%d/%d] Writing: %s...", idx, len(selected), title_preview)

        article = generate_article(claude, news_item)

        if not article:
            log.warning("[%d/%d] FAILED to generate article", idx, len(selected))
            failed += 1
            time.sleep(2)
            continue

        # Quality stats
        word_count = len(re.sub(r"<[^>]+>", "", article["content"]).split())
        h2_count = article["content"].count("<h2>")
        has_faq = "<details>" in article["content"]
        has_video = '<iframe' in article["content"]

        # Save to Supabase
        if save_article(sb, article, i, len(selected)):
            cat = article["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
            generated += 1

            extras = []
            if has_faq:
                extras.append("FAQ")
            if has_video:
                extras.append("VIDEO")
            extras_str = " + " + ", ".join(extras) if extras else ""

            feat = " [FEATURED]" if i < 5 else ""
            log.info(
                "[%d/%d] Saved: %s (%d words, %d H2s%s)%s",
                idx, len(selected), article["slug"][:50],
                word_count, h2_count, extras_str, feat,
            )
        else:
            failed += 1
            log.warning("[%d/%d] FAILED to save", idx, len(selected))

        # Rate limiting
        if i < len(selected) - 1:
            time.sleep(DELAY_BETWEEN_CALLS)

    # Final report
    log.info("\n" + "=" * 60)
    log.info("  GENERATION COMPLETE")
    log.info("=" * 60)
    log.info("  Total generated: %d", generated)
    log.info("  Failed: %d", failed)
    log.info("  Featured: %d", min(5, generated))
    log.info("  Categories:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        log.info("    %s: %d", cat, count)
    log.info("=" * 60)


if __name__ == "__main__":
    main()
