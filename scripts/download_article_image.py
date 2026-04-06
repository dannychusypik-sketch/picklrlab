#!/usr/bin/env python3
"""
Download article images from source URLs and save to public/images/articles/.
Returns the local path for use in Supabase.

Usage:
  python download_article_image.py --url "https://example.com/image.jpg" --slug "article-slug"

Or import as module:
  from download_article_image import download_image
  local_path = download_image(url, slug)
"""

import argparse
import hashlib
import logging
import os
import re
import sys
from urllib.parse import urlparse

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
log = logging.getLogger(__name__)

# Where to save images — relative to project root
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "public", "images", "articles")
# Public URL path
PUBLIC_PATH = "/images/articles"


def sanitize_filename(slug, ext=".jpg"):
    """Create a clean filename from slug."""
    clean = re.sub(r'[^a-z0-9\-]', '', slug.lower())[:80]
    return f"{clean}{ext}"


def download_image(image_url, slug, force=False):
    """
    Download image from URL, save locally, return public path.
    Returns None if download fails.
    """
    if not image_url:
        return None

    os.makedirs(IMAGES_DIR, exist_ok=True)

    # Determine file extension from URL
    parsed = urlparse(image_url)
    path = parsed.path.lower()
    if '.png' in path:
        ext = '.png'
    elif '.webp' in path:
        ext = '.webp'
    elif '.gif' in path:
        ext = '.gif'
    else:
        ext = '.jpg'

    filename = sanitize_filename(slug, ext)
    filepath = os.path.join(IMAGES_DIR, filename)
    public_url = f"{PUBLIC_PATH}/{filename}"

    # Skip if already exists
    if os.path.exists(filepath) and not force:
        log.info("Image already exists: %s", filename)
        return public_url

    try:
        log.info("Downloading: %s", image_url[:80])
        resp = requests.get(image_url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (compatible; PicklrLab/1.0)"
        })
        resp.raise_for_status()

        # Check it's actually an image
        content_type = resp.headers.get("content-type", "")
        if "image" not in content_type and len(resp.content) < 1000:
            log.warning("Not an image (content-type: %s), skipping", content_type)
            return None

        with open(filepath, "wb") as f:
            f.write(resp.content)

        size_kb = len(resp.content) / 1024
        log.info("Saved: %s (%.1f KB)", filename, size_kb)
        return public_url

    except Exception as e:
        log.warning("Failed to download %s: %s", image_url[:60], e)
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Image URL to download")
    parser.add_argument("--slug", required=True, help="Article slug for filename")
    parser.add_argument("--force", action="store_true", help="Re-download even if exists")
    args = parser.parse_args()

    result = download_image(args.url, args.slug, args.force)
    if result:
        print(result)
    else:
        print("FAILED", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
