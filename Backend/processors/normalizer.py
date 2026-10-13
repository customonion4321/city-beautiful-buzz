"""
Normalizer — City Beautiful Buzz
Converts raw scraped items into the final, clean JSON schema
consumed by the macOS widget and companion app.
ENFORCES STRICT 24-HOUR AGE GATE (max 24 hours old).
Ranks stories by hyperlocal civic urgency and recency.
"""

import hashlib
import re
import logging
from datetime import datetime, timezone
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

# GitHub Pages base URL — live API endpoint
GITHUB_PAGES_BASE = "https://customonion4321.github.io/city-beautiful-buzz"
LOGOS_BASE = f"{GITHUB_PAGES_BASE}/logos"

# Maximum age permitted in the live feed (24.0 hours)
MAX_AGE_HOURS = 24.0

# Source metadata (logo colors for display in widget)
SOURCE_COLORS: dict[str, str] = {
    "google_news_chd_wire":      "#0047AB",
    "google_news_chd_sectors":   "#0047AB",
    "google_news_chd_mc":        "#1A73E8",
    "google_news_chd_admin":     "#2C3E50",
    "google_news_chd_police":    "#E43131",
    "google_news_chd_traffic":   "#E43131",
    "google_news_chd_civic":     "#E8001D",
    "google_news_chd_hi_wire":   "#DD0000",
    "google_news_chd_hi_sectors":"#E8001D",
    "google_news_chd_hi_mc":     "#DD0000",
    "google_news_chd_hi_admin":  "#FF6200",
    "hindustan_times":           "#E8001D",
    "indian_express":            "#E43131",
    "tribune_india":             "#0047AB",
    "amar_ujala":                "#DD0000",
    "chandigarh_media":          "#1A73E8",
    "chandigarh_bytes":          "#2C3E50",
    "allevents":                 "#7B68EE",
}

DEFAULT_COLOR = "#555555"


def _generate_id(item: dict) -> str:
    """Generate a stable, unique ID for a news item."""
    raw = (item.get("_raw_id", "") or item.get("article_url", "")).encode()
    return "cbb-" + hashlib.md5(raw).hexdigest()[:10]


def _importance(item: dict) -> str:
    """
    Assign importance level based on category and hyperlocal score.
    """
    score = item.get("hyperlocal_score", 10)
    cat = item.get("category_id", "governance")

    if cat == "alerts" or score >= 45:
        return "high"
    elif cat in {"governance", "infrastructure"} or score >= 25:
        return "medium"
    return "low"


def _sanitize_text(text: str) -> str:
    """Final cleanup of text fields."""
    text = re.sub(r"\s+", " ", text or "").strip()
    text = re.sub(r"[^\x20-\x7E\u0900-\u097F]", "", text)  # keep ASCII + Devanagari
    return text


def normalize(item: dict) -> dict:
    """
    Convert a raw scraper item into the canonical CBB news item format.
    """
    source_id = item.get("source_id", "unknown")

    return {
        # ── Identity ──────────────────────────────────────────────────────
        "id": _generate_id(item),
        # ── Content ───────────────────────────────────────────────────────
        "title":             _sanitize_text(item.get("title", "Untitled")),
        "summary":           _sanitize_text(item.get("summary", "")),
        "sector_tag":        item.get("sector_tag", "CHANDIGARH"),
        # ── Category ──────────────────────────────────────────────────────
        "category_id":       item.get("category_id", "governance"),
        "category_label_en": item.get("category_label_en", "🏛️ Civic"),
        "category_label_hi": item.get("category_label_hi", "🏛️ प्रशासन"),
        # ── Source ────────────────────────────────────────────────────────
        "source": {
            "id":          source_id,
            "name":        item.get("source_name", "Unknown"),
            "logo_url":    f"{LOGOS_BASE}/{item.get('source_logo', 'default.png')}",
            "color":       SOURCE_COLORS.get(source_id, DEFAULT_COLOR),
            "article_url": item.get("article_url", ""),
            "language":    item.get("language", "en"),
            "tier":        item.get("tier", 1),
        },
        # ── Metadata ──────────────────────────────────────────────────────
        "published_at":     item.get("published_at", datetime.now(timezone.utc).isoformat()),
        "importance":       _importance(item),
        "hyperlocal_score": item.get("hyperlocal_score", 10),
    }


def filter_strictly_last_24_hours(items: list[dict]) -> list[dict]:
    """
    Enforces the strict requirement: Only show news at most 24 hours old.
    Items older than 24 hours are completely discarded.
    """
    now = datetime.now(timezone.utc)
    fresh_items = []
    stale_count = 0

    for item in items:
        pub_str = item.get("published_at")
        if not pub_str:
            continue
        try:
            dt = date_parser.parse(pub_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            age_hours = (now - dt).total_seconds() / 3600.0

            # Allow up to MAX_AGE_HOURS (24.0h), with -15m tolerance for slight clock skew
            if -0.25 <= age_hours <= MAX_AGE_HOURS:
                fresh_items.append(item)
            else:
                stale_count += 1
        except Exception:
            continue

    logger.info(f"⏱️ 24h Freshness Gate: Retained {len(fresh_items)} items | Discarded {stale_count} items older than 24 hours.")
    return fresh_items


def normalize_all(items: list[dict]) -> list[dict]:
    """
    Normalize items, apply the strict 24-hour freshness filter,
    and sort by civic urgency:
    Primary: High importance / high hyperlocal score first.
    Secondary: Publication timestamp descending.
    """
    normalized = [normalize(item) for item in items]

    # Enforce strict maximum 24h age
    fresh = filter_strictly_last_24_hours(normalized)

    # Sort descending by civic score + alerts boost, then by recency
    def sort_key(item: dict):
        cat = item.get("category_id", "")
        cat_boost = 100 if cat == "alerts" else 0
        score = item.get("hyperlocal_score", 10) + cat_boost
        pub_at = item.get("published_at", "")
        return (score, pub_at)

    fresh.sort(key=sort_key, reverse=True)
    return fresh
