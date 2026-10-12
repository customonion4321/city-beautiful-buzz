"""
Normalizer — City Beautiful Buzz
Converts raw scraped items into the final, clean JSON schema
consumed by the macOS widget.
"""

import hashlib
import re
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# GitHub Pages base URL — live API endpoint
GITHUB_PAGES_BASE = "https://customonion4321.github.io/city-beautiful-buzz"
LOGOS_BASE = f"{GITHUB_PAGES_BASE}/logos"

# Source metadata (logo colors for display in widget)
SOURCE_COLORS: dict[str, str] = {
    "hindustan_times":    "#E8001D",
    "indian_express":     "#E43131",
    "ndtv_chandigarh":    "#D81920",
    "tribune_india":      "#0047AB",
    "tricity_tribune":    "#0047AB",
    "jagran_chandigarh":  "#FF6200",
    "punjab_kesari":      "#FF0000",
    "amar_ujala":         "#DD0000",
    "chandigarh_media":   "#1A73E8",
    "chandigarh_bytes":   "#2C3E50",
    "allevents":          "#7B68EE",
}

DEFAULT_COLOR = "#555555"


def _generate_id(item: dict) -> str:
    """Generate a stable, unique ID for a news item."""
    raw = (item.get("_raw_id", "") or item.get("article_url", "")).encode()
    return "cbb-" + hashlib.md5(raw).hexdigest()[:10]


def _importance(item: dict) -> str:
    """
    Assign importance level based on category.
    Alerts and governance are high; lifestyle is low.
    """
    high = {"alerts", "governance", "infrastructure"}
    medium = {"events", "important_dates", "education", "health", "safety", "sports"}

    cat = item.get("category_id", "general")
    if cat in high:
        return "high"
    elif cat in medium:
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
        "title":     _sanitize_text(item.get("title", "Untitled")),
        "summary":   _sanitize_text(item.get("summary", "")),
        # ── Category ──────────────────────────────────────────────────────
        "category_id":       item.get("category_id", "general"),
        "category_label_en": item.get("category_label_en", "📰 General"),
        "category_label_hi": item.get("category_label_hi", "📰 सामान्य"),
        # ── Source ────────────────────────────────────────────────────────
        "source": {
            "id":          source_id,
            "name":        item.get("source_name", "Unknown"),
            "logo_url":    f"{LOGOS_BASE}/{item.get('source_logo', 'default.png')}",
            "color":       SOURCE_COLORS.get(source_id, DEFAULT_COLOR),
            "article_url": item.get("article_url", ""),
            "language":    item.get("language", "en"),
            "tier":        item.get("tier", 3),
        },
        # ── Metadata ──────────────────────────────────────────────────────
        "published_at": item.get("published_at", datetime.now(timezone.utc).isoformat()),
        "importance":   _importance(item),
    }


def normalize_all(items: list[dict]) -> list[dict]:
    """Normalize a list of raw items and sort by importance + recency."""
    normalized = [normalize(item) for item in items]

    # Sort: high importance first, then by published_at desc
    importance_order = {"high": 0, "medium": 1, "low": 2}
    normalized.sort(
        key=lambda x: (
            importance_order.get(x.get("importance", "low"), 2),
            x.get("published_at", ""),
        ),
        reverse=False,
    )

    # Re-sort published_at descending within same importance
    from itertools import groupby
    final = []
    for _, group in groupby(normalized, key=lambda x: x.get("importance")):
        group_list = sorted(list(group), key=lambda x: x.get("published_at", ""), reverse=True)
        final.extend(group_list)

    return final
