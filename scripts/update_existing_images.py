#!/usr/bin/env python3
"""
One-time script: Update existing articles in Supabase with real images from The Dink.
For each article, searches The Dink Ghost API for a matching article by title,
downloads the feature_image, and updates image_url in Supabase.
Also extracts YouTube video URLs and prepends them to article content.

Usage: python3 update_existing_images.py
Env vars: SUPABASE_URL, SUPABASE_SERVICE_KEY
"""

import logging
import os
import re
import sys
import time

import requests
from supabase import create_client

from download_article_image import download_image

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# The Dink Ghost Content API
DINK_API = "https://thedinkpickleball.com/ghost/api/content/posts/"
DINK_KEY = "5b252543f0374235fec6fad8b5"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PicklrLab/1.0)"
}


def get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        log.error("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY env vars")
        sys.exit(1)
    return create_client(url, key)


def search_dink_by_title(title):
    """Search The Dink Ghost API for an article matching the given title."""
    # Extract a few key words from the title for searching
    # Ghost API supports filter by title (partial match not great), so we fetch
    # a larger batch and match locally
    try:
        resp = requests.get(
            DINK_API,
            params={
                "key": DINK_KEY,
                "limit": 50,
                "fields": "title,slug,feature_image,html,url",
                "order": "published_at desc",
            },
            headers=HEADERS,
            timeout=15,
        )
        resp.raise_for_status()
        posts = resp.json().get("posts", [])

        title_lower = title.lower().strip()
        # Try exact-ish match first
        for post in posts:
            post_title = post.get("title", "").lower().strip()
            if post_title == title_lower:
                return post

        # Try fuzzy: check if significant words overlap
        title_words = set(re.findall(r'[a-z]{3,}', title_lower))
        best_match = None
        best_score = 0
        for post in posts:
            post_title = post.get("title", "").lower().strip()
            post_words = set(re.findall(r'[a-z]{3,}', post_title))
            if not title_words or not post_words:
                continue
            overlap = len(title_words & post_words)
            score = overlap / max(len(title_words), len(post_words))
            if score > best_score and score >= 0.5:
                best_score = score
                best_match = post

        if best_match:
            log.info("  Fuzzy match (%.0f%%): '%s'",
                     best_score * 100, best_match.get("title", "")[:60])
        return best_match

    except Exception as e:
        log.warning("Failed to search Dink API: %s", e)
        return None


def extract_youtube_url(html):
    """Extract first YouTube embed URL from HTML content."""
    if not html:
        return None
    patterns = [
        r'<iframe[^>]+src=["\']([^"\']*youtube\.com/embed/[^"\']+)["\']',
        r'<iframe[^>]+src=["\']([^"\']*youtu\.be/[^"\']+)["\']',
        r'https?://(?:www\.)?youtube\.com/embed/[\w\-]+(?:\?[^"\'\s]*)?',
    ]
    for pat in patterns:
        match = re.search(pat, html, re.IGNORECASE)
        if match:
            url = match.group(1) if match.lastindex else match.group(0)
            video_id_match = re.search(r'(?:embed/|watch\?v=|youtu\.be/)([\w\-]+)', url)
            if video_id_match:
                return "https://www.youtube.com/embed/" + video_id_match.group(1)
            return url
    return None


def make_slug_from_title(title):
    """Create a simple slug from title for image filename."""
    slug = re.sub(r'[^a-z0-9\s\-]', '', title.lower())
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:80]


def main():
    log.info("=== update_existing_images.py starting ===")

    sb = get_supabase()

    # Fetch all articles
    result = sb.table("articles").select("*").order("published_at", desc=True).execute()
    articles = result.data
    log.info("Found %d articles in Supabase", len(articles))

    updated = 0
    skipped = 0

    for article in articles:
        title = article.get("title", "")
        article_id = article.get("id")
        current_image = article.get("image_url", "")
        slug = article.get("slug", "") or make_slug_from_title(title)

        log.info("Processing: %s", title[:70])

        # Search The Dink for matching article
        dink_post = search_dink_by_title(title)

        if not dink_post:
            log.info("  No match found on The Dink, skipping")
            skipped += 1
            continue

        feature_image = dink_post.get("feature_image", "")
        html_content = dink_post.get("html", "")

        update_data = {}

        # Download feature image
        if feature_image:
            local_path = download_image(feature_image, slug)
            if local_path:
                update_data["image_url"] = local_path
                log.info("  Downloaded image: %s", local_path)
            else:
                log.info("  Failed to download image, keeping current")
        else:
            log.info("  No feature image on Dink post")

        # Extract YouTube video and prepend to content
        video_url = extract_youtube_url(html_content)
        if video_url:
            content = article.get("content", "")
            # Check if video is already embedded
            if video_url not in content and "video-embed" not in content:
                video_html = (
                    '<div class="video-embed">'
                    '<iframe src="{src}" width="100%" height="400" '
                    'frameborder="0" allowfullscreen></iframe>'
                    '</div>\n'
                ).format(src=video_url)
                # Insert after first </p> or prepend
                first_p_end = content.find("</p>")
                if first_p_end != -1:
                    insert_pos = first_p_end + len("</p>")
                    content = content[:insert_pos] + "\n" + video_html + content[insert_pos:]
                else:
                    content = video_html + content
                update_data["content"] = content
                log.info("  Embedded video: %s", video_url)
            else:
                log.info("  Video already embedded or present")

        # Update in Supabase
        if update_data:
            try:
                sb.table("articles").update(update_data).eq("id", article_id).execute()
                log.info("  Updated article ID %s", article_id)
                updated += 1
            except Exception as e:
                log.error("  Failed to update: %s", e)
        else:
            log.info("  Nothing to update")
            skipped += 1

        # Be nice to APIs
        time.sleep(0.5)

    log.info("=== Done: %d updated, %d skipped ===", updated, skipped)


if __name__ == "__main__":
    main()
