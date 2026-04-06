#!/usr/bin/env python3
"""
SEO quality checker for PicklrLab articles stored in Supabase.

Usage:
    python seo_checker.py --check-all
    python seo_checker.py --slug article-slug
    python seo_checker.py --check-all --min-score 70
"""

import argparse
import logging
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

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
# Supabase client
# ---------------------------------------------------------------------------
def get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        log.error("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY env vars")
        sys.exit(1)
    return create_client(url, key)


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------
def strip_html(html: str) -> str:
    """Remove all HTML tags and return plain text."""
    return re.sub(r"<[^>]+>", " ", html).strip()


def count_words(text: str) -> int:
    """Count words in plain text."""
    return len(text.split())


def extract_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    sentences = re.split(r"[.!?]+", text)
    return [s.strip() for s in sentences if s.strip()]


# ---------------------------------------------------------------------------
# SEO Checks — each returns (score, max_score, message)
# ---------------------------------------------------------------------------
def check_title_length(article: Dict) -> Tuple[int, int, str]:
    """Title should be 50-60 characters for optimal SEO."""
    title = article.get("title", "")
    length = len(title)
    max_score = 10

    if 50 <= length <= 60:
        return max_score, max_score, "Title length: %d chars (ideal 50-60)" % length
    elif 40 <= length <= 70:
        return 7, max_score, "Title length: %d chars (acceptable, ideal is 50-60)" % length
    elif length < 30:
        return 2, max_score, "Title TOO SHORT: %d chars (aim for 50-60)" % length
    elif length > 80:
        return 3, max_score, "Title TOO LONG: %d chars (will be truncated in SERPs, aim for 50-60)" % length
    else:
        return 5, max_score, "Title length: %d chars (slightly off, ideal is 50-60)" % length


def check_excerpt(article: Dict) -> Tuple[int, int, str]:
    """Excerpt/meta description should be 150-160 chars."""
    excerpt = article.get("excerpt", "")
    length = len(excerpt)
    max_score = 10

    if not excerpt:
        return 0, max_score, "NO excerpt/meta description found"
    elif 150 <= length <= 160:
        return max_score, max_score, "Excerpt length: %d chars (ideal 150-160)" % length
    elif 120 <= length <= 180:
        return 7, max_score, "Excerpt length: %d chars (acceptable, ideal is 150-160)" % length
    elif length < 80:
        return 3, max_score, "Excerpt TOO SHORT: %d chars (aim for 150-160)" % length
    else:
        return 5, max_score, "Excerpt length: %d chars (slightly off, ideal is 150-160)" % length


def check_content_length(article: Dict) -> Tuple[int, int, str]:
    """Content should be at least 800 words."""
    content = article.get("content", "")
    plain = strip_html(content)
    words = count_words(plain)
    max_score = 15

    if words >= 1000:
        return max_score, max_score, "Content: %d words (excellent)" % words
    elif words >= 800:
        return 12, max_score, "Content: %d words (good, 800+ target met)" % words
    elif words >= 500:
        return 7, max_score, "Content: %d words (thin content, aim for 800+)" % words
    elif words >= 300:
        return 4, max_score, "Content THIN: %d words (needs substantial expansion to 800+)" % words
    else:
        return 1, max_score, "Content VERY THIN: %d words (minimum 800 recommended)" % words


def check_h2_headings(article: Dict) -> Tuple[int, int, str]:
    """Should have at least 3 H2 headings for structure."""
    content = article.get("content", "")
    h2_count = len(re.findall(r"<h2[^>]*>", content, re.IGNORECASE))
    max_score = 10

    if h2_count >= 4:
        return max_score, max_score, "H2 headings: %d (excellent structure)" % h2_count
    elif h2_count >= 3:
        return 8, max_score, "H2 headings: %d (good)" % h2_count
    elif h2_count >= 1:
        return 4, max_score, "H2 headings: %d (needs more, aim for 3-5)" % h2_count
    else:
        return 0, max_score, "NO H2 headings found (add 3-5 for better structure)"


def check_images(article: Dict) -> Tuple[int, int, str]:
    """Should have at least 1 image."""
    content = article.get("content", "")
    img_count = len(re.findall(r"<img[^>]+>", content, re.IGNORECASE))
    max_score = 10

    if img_count >= 2:
        return max_score, max_score, "Images: %d found (great)" % img_count
    elif img_count == 1:
        return 7, max_score, "Images: 1 found (consider adding more)"
    else:
        return 0, max_score, "NO images found (add at least 1 featured image)"


def check_internal_links(article: Dict) -> Tuple[int, int, str]:
    """Should have internal linking suggestions or actual links."""
    content = article.get("content", "")
    max_score = 10

    # Check for actual links
    link_count = len(re.findall(r'<a[^>]+href=', content, re.IGNORECASE))
    # Check for internal linking text suggestions
    link_phrases = [
        "check our", "see our", "rankings page", "paddle reviews",
        "read more", "explore our", "browse our", "our guide",
    ]
    suggestion_count = sum(1 for phrase in link_phrases if phrase.lower() in content.lower())

    total = link_count + suggestion_count
    if total >= 3:
        return max_score, max_score, "Internal links/suggestions: %d links + %d suggestions" % (link_count, suggestion_count)
    elif total >= 1:
        return 5, max_score, "Internal links/suggestions: %d links + %d suggestions (add more)" % (link_count, suggestion_count)
    else:
        return 0, max_score, "NO internal links or linking suggestions found"


def check_faq_section(article: Dict) -> Tuple[int, int, str]:
    """Should have FAQ section with details/summary tags."""
    content = article.get("content", "")
    max_score = 15

    details_count = len(re.findall(r"<details>", content, re.IGNORECASE))
    has_faq_heading = bool(re.search(r"<h2[^>]*>.*(?:FAQ|Frequently Asked).*</h2>", content, re.IGNORECASE))

    if details_count >= 3 and has_faq_heading:
        return max_score, max_score, "FAQ section: %d Q&As with heading (excellent)" % details_count
    elif details_count >= 1:
        return 8, max_score, "FAQ section: %d Q&As found (aim for 3 with heading)" % details_count
    elif has_faq_heading:
        return 4, max_score, "FAQ heading found but no <details> tags for Q&A"
    else:
        return 0, max_score, "NO FAQ section found (add 3 Q&As in <details> tags)"


def check_keyword_density(article: Dict) -> Tuple[int, int, str]:
    """Title keywords should appear in content."""
    title = article.get("title", "")
    content = article.get("content", "")
    plain_content = strip_html(content).lower()
    max_score = 10

    # Extract meaningful keywords from title (skip stop words)
    stop_words = {
        "the", "a", "an", "in", "on", "at", "to", "for", "of", "and",
        "is", "are", "was", "were", "be", "been", "being", "have", "has",
        "had", "do", "does", "did", "will", "would", "could", "should",
        "may", "might", "can", "with", "from", "by", "as", "or", "but",
        "not", "no", "its", "it", "this", "that", "how", "what", "why",
        "who", "when", "where", "which", "new", "top",
    }
    title_words = [
        w for w in re.findall(r"\w+", title.lower())
        if w not in stop_words and len(w) > 2
    ]

    if not title_words:
        return 5, max_score, "Could not extract keywords from title"

    found = 0
    missing = []
    for word in title_words:
        if word in plain_content:
            found += 1
        else:
            missing.append(word)

    ratio = found / len(title_words) if title_words else 0

    if ratio >= 0.8:
        return max_score, max_score, "Keyword density: %d/%d title keywords found in content" % (found, len(title_words))
    elif ratio >= 0.5:
        return 6, max_score, "Keyword density: %d/%d (missing: %s)" % (found, len(title_words), ", ".join(missing))
    else:
        return 2, max_score, "LOW keyword density: %d/%d (missing: %s)" % (found, len(title_words), ", ".join(missing))


def check_readability(article: Dict) -> Tuple[int, int, str]:
    """Check average sentence length for readability."""
    content = article.get("content", "")
    plain = strip_html(content)
    sentences = extract_sentences(plain)
    max_score = 10

    if not sentences:
        return 0, max_score, "Could not analyze readability (no sentences found)"

    avg_words = sum(count_words(s) for s in sentences) / len(sentences)

    if 12 <= avg_words <= 20:
        return max_score, max_score, "Readability: avg %.1f words/sentence (ideal 12-20)" % avg_words
    elif 8 <= avg_words <= 25:
        return 7, max_score, "Readability: avg %.1f words/sentence (acceptable)" % avg_words
    elif avg_words > 25:
        return 3, max_score, "Readability: avg %.1f words/sentence (too complex, shorten sentences)" % avg_words
    else:
        return 4, max_score, "Readability: avg %.1f words/sentence (too choppy, vary length)" % avg_words


# ---------------------------------------------------------------------------
# Main scoring
# ---------------------------------------------------------------------------
ALL_CHECKS = [
    check_title_length,
    check_excerpt,
    check_content_length,
    check_h2_headings,
    check_images,
    check_internal_links,
    check_faq_section,
    check_keyword_density,
    check_readability,
]


def score_article(article: Dict) -> Tuple[int, List[str]]:
    """Run all SEO checks and return total score (0-100) with details."""
    total_score = 0
    total_max = 0
    details = []

    for check_fn in ALL_CHECKS:
        score, max_score, message = check_fn(article)
        total_score += score
        total_max += max_score
        status = "PASS" if score >= max_score * 0.7 else ("WARN" if score >= max_score * 0.4 else "FAIL")
        details.append("[%s] %s (%d/%d)" % (status, message, score, max_score))

    # Normalize to 0-100
    normalized = int((total_score / total_max) * 100) if total_max > 0 else 0
    return normalized, details


def print_report(article: Dict, score: int, details: List[str]):
    """Pretty print SEO report for an article."""
    grade = "A+" if score >= 90 else ("A" if score >= 80 else ("B" if score >= 70 else ("C" if score >= 60 else ("D" if score >= 50 else "F"))))

    print("\n" + "=" * 70)
    print("  ARTICLE: %s" % article.get("title", "Unknown")[:65])
    print("  SLUG:    %s" % article.get("slug", "N/A"))
    print("  SCORE:   %d/100 (Grade: %s)" % (score, grade))
    print("=" * 70)

    for detail in details:
        if detail.startswith("[PASS]"):
            print("  %s" % detail)
        elif detail.startswith("[WARN]"):
            print("  %s" % detail)
        else:
            print("  %s" % detail)

    # Suggestions
    suggestions = [d.split("] ", 1)[1] for d in details if d.startswith("[FAIL]")]
    if suggestions:
        print("\n  SUGGESTIONS:")
        for i, s in enumerate(suggestions, 1):
            msg = s.split(" (")[0]
            print("    %d. Fix: %s" % (i, msg))

    print("")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="SEO quality checker for PicklrLab articles")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check-all", action="store_true", help="Check all articles")
    group.add_argument("--slug", type=str, help="Check a specific article by slug")
    parser.add_argument("--min-score", type=int, default=0, help="Only show articles below this score")
    parser.add_argument("--limit", type=int, default=50, help="Max articles to check (default: 50)")
    args = parser.parse_args()

    sb = get_supabase()

    if args.slug:
        result = sb.table("articles").select("*").eq("slug", args.slug).limit(1).execute()
        if not result.data:
            log.error("Article not found: %s", args.slug)
            sys.exit(1)
        articles = result.data
    else:
        result = (
            sb.table("articles")
            .select("*")
            .order("published_at", desc=True)
            .limit(args.limit)
            .execute()
        )
        articles = result.data

    log.info("Checking SEO for %d articles...\n", len(articles))

    scores = []
    for article in articles:
        score, details = score_article(article)
        scores.append((article, score, details))

        if args.check_all and args.min_score > 0 and score >= args.min_score:
            continue

        print_report(article, score, details)

    # Summary
    if len(scores) > 1:
        avg = sum(s for _, s, _ in scores) / len(scores)
        best = max(scores, key=lambda x: x[1])
        worst = min(scores, key=lambda x: x[1])
        print("\n" + "=" * 70)
        print("  SUMMARY: %d articles checked" % len(scores))
        print("  Average score: %.1f/100" % avg)
        print("  Best:  %d/100 — %s" % (best[1], best[0].get("slug", "")))
        print("  Worst: %d/100 — %s" % (worst[1], worst[0].get("slug", "")))
        print("=" * 70)


if __name__ == "__main__":
    main()
