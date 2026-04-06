#!/usr/bin/env python3
"""
Download curated free Unsplash images for PicklrLab articles.
Images are free to use under the Unsplash license.

Usage: python3 download_images.py
"""

import os
import sys
import time
import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "public", "images", "articles",
)

# Curated Unsplash images (free, no API key needed)
IMAGES = [
    # Sports/tennis/racket sports (visually similar to pickleball)
    ("pickleball-01.jpg", "https://images.unsplash.com/photo-1554068865-24cecd4e34b8?w=800&q=80"),
    ("pickleball-02.jpg", "https://images.unsplash.com/photo-1622279457486-62dcc4a431d6?w=800&q=80"),
    ("pickleball-03.jpg", "https://images.unsplash.com/photo-1530549387789-4c1017266635?w=800&q=80"),
    ("pickleball-04.jpg", "https://images.unsplash.com/photo-1612872087720-bb876e2e67d1?w=800&q=80"),
    ("pickleball-05.jpg", "https://images.unsplash.com/photo-1599586120429-48281b6f0ece?w=800&q=80"),
    ("pickleball-06.jpg", "https://images.unsplash.com/photo-1526232761682-d26e03ac148e?w=800&q=80"),
    ("pickleball-07.jpg", "https://images.unsplash.com/photo-1521412644187-c49fa049e84d?w=800&q=80"),
    ("pickleball-08.jpg", "https://images.unsplash.com/photo-1592632789004-57d4354f2499?w=800&q=80"),
    # Tournament/arena
    ("tournament-01.jpg", "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=800&q=80"),
    ("tournament-02.jpg", "https://images.unsplash.com/photo-1587280501635-68a0e82cd5ff?w=800&q=80"),
    ("tournament-03.jpg", "https://images.unsplash.com/photo-1471295253337-3ceaaedca402?w=800&q=80"),
    ("tournament-04.jpg", "https://images.unsplash.com/photo-1546519638-68e109498ffc?w=800&q=80"),
    # Training/fitness
    ("training-01.jpg", "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=800&q=80"),
    ("training-02.jpg", "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=800&q=80"),
    ("training-03.jpg", "https://images.unsplash.com/photo-1549060279-7e168fcee0c2?w=800&q=80"),
    ("training-04.jpg", "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=800&q=80"),
    # Gear/equipment
    ("gear-01.jpg", "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=800&q=80"),
    ("gear-02.jpg", "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=800&q=80"),
    ("gear-03.jpg", "https://images.unsplash.com/photo-1612872087720-bb876e2e67d1?w=800&q=80"),
    # Rankings/data/analytics
    ("rankings-01.jpg", "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80"),
    ("rankings-02.jpg", "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=800&q=80"),
    ("rankings-03.jpg", "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80"),
    # News/general
    ("news-01.jpg", "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800&q=80"),
    ("news-02.jpg", "https://images.unsplash.com/photo-1495020689067-958852a7765e?w=800&q=80"),
    ("news-03.jpg", "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=800&q=80"),
    # Vietnam/SEA
    ("vietnam-01.jpg", "https://images.unsplash.com/photo-1557750255-c76072a7aad1?w=800&q=80"),
    ("vietnam-02.jpg", "https://images.unsplash.com/photo-1583417319070-4a69db38a482?w=800&q=80"),
    ("sea-01.jpg", "https://images.unsplash.com/photo-1528164344705-47542687000d?w=800&q=80"),
    ("sea-02.jpg", "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80"),
    # Review/comparison
    ("review-01.jpg", "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=800&q=80"),
    ("review-02.jpg", "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=800&q=80"),
    # Opinion/lifestyle
    ("opinion-01.jpg", "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800&q=80"),
    ("opinion-02.jpg", "https://images.unsplash.com/photo-1495020689067-958852a7765e?w=800&q=80"),
]


def download_image(filename, url, output_dir):
    # type: (str, str, str) -> bool
    """Download a single image from URL to output_dir/filename."""
    filepath = os.path.join(output_dir, filename)

    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        if size > 1000:  # Skip if already downloaded and not empty
            print("  SKIP %s (already exists, %d bytes)" % (filename, size))
            return True

    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/120.0.0.0 Safari/537.36",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()

        with open(filepath, "wb") as f:
            f.write(data)

        size_kb = len(data) / 1024.0
        print("  OK   %s (%.1f KB)" % (filename, size_kb))
        return True

    except urllib.error.HTTPError as e:
        print("  FAIL %s — HTTP %d" % (filename, e.code))
        return False
    except urllib.error.URLError as e:
        print("  FAIL %s — %s" % (filename, e.reason))
        return False
    except Exception as e:
        print("  FAIL %s — %s" % (filename, str(e)))
        return False


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Downloading %d images to: %s\n" % (len(IMAGES), OUTPUT_DIR))

    success = 0
    failed = 0

    for filename, url in IMAGES:
        ok = download_image(filename, url, OUTPUT_DIR)
        if ok:
            success += 1
        else:
            failed += 1
        # Small delay to be polite to Unsplash servers
        time.sleep(0.5)

    print("\nDone! %d downloaded, %d failed." % (success, failed))

    if failed > 0:
        print("Some images failed to download. Re-run script to retry.")
        sys.exit(1)


if __name__ == "__main__":
    main()
