"""
Deduplicator — City Beautiful Buzz
Removes duplicate news items across multiple sources using URL normalization
and fuzzy title matching.
"""

import hashlib
import re
import logging

logger = logging.getLogger(__name__)


def _normalize_url(url: str) -> str:
    """Strip tracking parameters and normalize URL for dedup comparison."""
    # Remove common UTM and tracking params
    url = re.sub(r"[?&](utm_[^&]+|ref=[^&]+|source=[^&]+|fbclid=[^&]+)", "", url)
    url = url.rstrip("/?#").lower().strip()
    return url


def _url_hash(url: str) -> str:
    """Short MD5 hash of normalized URL."""
    return hashlib.md5(_normalize_url(url).encode()).hexdigest()[:12]


def _title_fingerprint(title: str) -> str:
    """
    Create a rough fingerprint from title for near-duplicate detection.
    Strips punctuation, lowercases, removes stopwords, takes first 8 words.
    """
    stopwords = {
        "a", "an", "the", "is", "in", "on", "at", "to", "of", "and",
        "or", "for", "with", "by", "as", "was", "are", "be", "has",
        "have", "had", "will", "from", "that", "this", "it", "he",
        "she", "they", "we", "you", "i", "its", "their",
    }
    words = re.sub(r"[^\w\s]", " ", title.lower()).split()
    meaningful = [w for w in words if w not in stopwords and len(w) > 2]
    fingerprint = " ".join(meaningful[:8])
    return hashlib.md5(fingerprint.encode()).hexdigest()[:12]


def deduplicate(items: list[dict]) -> list[dict]:
    """
    Remove duplicate news items.

    Strategy:
    1. Exact URL dedup (after normalization)
    2. Near-duplicate title dedup (fuzzy fingerprint match)

    Items from higher-tier sources (tier 1) are preferred over lower-tier
    when duplicates are found.
    """
    logger.info(f"Deduplicating {len(items)} items...")

    # Sort by tier ascending (tier 1 first = preferred)
    sorted_items = sorted(items, key=lambda x: (x.get("tier", 9), x.get("published_at", "")))

    seen_url_hashes = set()
    seen_title_fingerprints = set()
    unique_items = []

    for item in sorted_items:
        url = item.get("article_url", "")
        title = item.get("title", "")

        u_hash = _url_hash(url)
        t_fp = _title_fingerprint(title)

        if u_hash in seen_url_hashes:
            logger.debug(f"  Dedup (URL): {title[:60]}")
            continue
        if t_fp in seen_title_fingerprints:
            logger.debug(f"  Dedup (title): {title[:60]}")
            continue

        seen_url_hashes.add(u_hash)
        seen_title_fingerprints.add(t_fp)
        unique_items.append(item)

    logger.info(f"  → {len(unique_items)} unique items after dedup (removed {len(items) - len(unique_items)})")
    return unique_items
