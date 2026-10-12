"""
City Beautiful Buzz — Main Scraper Orchestrator
================================================
Coordinates all data sources, processors, and output generation.
Run this script directly or via GitHub Actions cron.

Usage:
    python3 scraper.py               # run everything
    python3 scraper.py --rss-only    # RSS feeds only (faster)
    python3 scraper.py --web-only    # web scraping only
    python3 scraper.py --test        # dry run, print to stdout only
"""

import json
import logging
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone

# ── Local modules ──────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))

from sources.rss_sources import fetch_all_rss
from sources.web_sources import fetch_all_web
from processors.chandigarh_filter import filter_chandigarh_only
from processors.deduplicator import deduplicate
from processors.categorizer import categorize_all
from processors.normalizer import normalize_all

# ── Constants ──────────────────────────────────────────────────────────────────
OUTPUT_PATH = Path(__file__).parent / "data" / "news.json"
MAX_ITEMS = 120         # max items in final feed (extensive coverage)
LOG_LEVEL = logging.INFO

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s  %(levelname)-8s  %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("scraper")


def build_output(items: list[dict]) -> dict:
    """Wrap final items in the top-level JSON envelope."""
    return {
        "schema_version": "1.0",
        "project": "City Beautiful Buzz",
        "city": "Chandigarh",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "item_count": len(items),
        "items": items,
    }


def run(rss_only: bool = False, web_only: bool = False, test: bool = False):
    logger.info("=" * 60)
    logger.info("  City Beautiful Buzz — Scraper Starting")
    logger.info("=" * 60)

    raw_items: list[dict] = []

    # ── Step 1: Fetch ──────────────────────────────────────────────────────
    if not web_only:
        logger.info("\n📡  Fetching RSS feeds...")
        rss_items = fetch_all_rss()
        logger.info(f"   Got {len(rss_items)} items from RSS feeds")
        raw_items.extend(rss_items)

    if not rss_only:
        logger.info("\n🕷️   Web scraping...")
        web_items = fetch_all_web()
        logger.info(f"   Got {len(web_items)} items from web scraping")
        raw_items.extend(web_items)

    logger.info(f"\n📊  Total raw items: {len(raw_items)}")

    if not raw_items:
        logger.error("❌  No items fetched. Aborting.")
        sys.exit(1)

    # ── Step 2: Strict Chandigarh Geographic Filter ───────────────────────
    logger.info("\n📍  Filtering for Chandigarh / Tri-city relevance...")
    chd_items = filter_chandigarh_only(raw_items)

    if not chd_items:
        logger.error("❌  No Chandigarh-specific items passed the filter. Aborting.")
        sys.exit(1)

    # ── Step 3: Deduplicate ────────────────────────────────────────────────
    logger.info("\n🔍  Deduplicating...")
    unique_items = deduplicate(chd_items)

    # ── Step 4: Categorize ─────────────────────────────────────────────────
    logger.info("\n🏷️   Categorizing...")
    categorized = categorize_all(unique_items)

    # ── Step 4: Normalize & Sort ───────────────────────────────────────────
    logger.info("\n✨  Normalizing and sorting...")
    final_items = normalize_all(categorized)
    final_items = final_items[:MAX_ITEMS]

    # ── Step 5: Output ─────────────────────────────────────────────────────
    output = build_output(final_items)

    if test:
        logger.info("\n[DRY RUN] Output JSON:")
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        logger.info(f"\n✅  Saved {len(final_items)} items → {OUTPUT_PATH}")

    # ── Summary ────────────────────────────────────────────────────────────
    logger.info("\n" + "=" * 60)
    logger.info(f"  Done! {len(final_items)} items saved.")

    # Category breakdown
    from collections import Counter
    cats = Counter(item.get("category_id", "general") for item in final_items)
    for cat, count in cats.most_common():
        logger.info(f"    {cat}: {count} items")

    logger.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="City Beautiful Buzz — News Scraper")
    parser.add_argument("--rss-only", action="store_true", help="Only fetch RSS feeds")
    parser.add_argument("--web-only", action="store_true", help="Only do web scraping")
    parser.add_argument("--test", action="store_true", help="Dry run, print to stdout")
    args = parser.parse_args()

    run(rss_only=args.rss_only, web_only=args.web_only, test=args.test)
