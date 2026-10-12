"""
RSS Sources — City Beautiful Buzz
Fetches structured news from RSS feeds of major Chandigarh news outlets.
"""

import feedparser
import logging
import ssl
import certifi
from datetime import datetime, timezone
from dateutil import parser as date_parser

# ── macOS SSL fix ─────────────────────────────────────────────────────────────
# Python 3 on macOS doesn't use system root certs by default.
# Patch the default SSL context to use certifi's trusted CA bundle.
ssl._create_default_https_context = lambda: ssl.create_default_context(
    cafile=certifi.where()
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Registered RSS Feeds — Chandigarh / Tricity
# ─────────────────────────────────────────────────────────────────────────────
RSS_FEEDS = [
    {
        "source_id": "hindustan_times",
        "name": "Hindustan Times",
        "logo": "ht.png",
        "url": "https://www.hindustantimes.com/feeds/rss/cities/chandigarh-news/rssfeed.xml",
        "language": "en",
        "tier": 1,
    },
    {
        "source_id": "indian_express",
        "name": "Indian Express",
        "logo": "ie.png",
        "url": "https://indianexpress.com/section/cities/chandigarh/feed/",
        "language": "en",
        "tier": 1,
    },
    {
        "source_id": "ndtv_chandigarh",
        "name": "NDTV Chandigarh",
        "logo": "ndtv.png",
        "url": "https://feeds.feedburner.com/ndtvnews-city-chandigarh",
        "language": "en",
        "tier": 1,
    },
    {
        "source_id": "tribune_india",
        "name": "The Tribune",
        "logo": "tribune.png",
        "url": "https://www.tribuneindia.com/rss/feed?id=11",  # Chandigarh section
        "language": "en",
        "tier": 1,
    },
    {
        "source_id": "jagran_chandigarh",
        "name": "Dainik Jagran",
        "logo": "jagran.png",
        "url": "https://www.jagran.com/rss/news-city-chandigarh.xml",
        "language": "hi",
        "tier": 2,
    },
    {
        "source_id": "punjab_kesari",
        "name": "Punjab Kesari",
        "logo": "punjabkesari.png",
        "url": "https://www.punjabkesari.in/rss/chandigarh-news.xml",
        "language": "hi",
        "tier": 2,
    },
    {
        "source_id": "amar_ujala",
        "name": "Amar Ujala",
        "logo": "amarujala.png",
        "url": "https://www.amarujala.com/rss/chandigarh.xml",
        "language": "hi",
        "tier": 2,
    },
]


def _parse_date(entry) -> str:
    """Try multiple date fields and return ISO 8601 string in IST (+05:30)."""
    raw = (
        getattr(entry, "published", None)
        or getattr(entry, "updated", None)
        or getattr(entry, "created", None)
    )
    if not raw:
        return datetime.now(timezone.utc).isoformat()
    try:
        dt = date_parser.parse(raw)
        return dt.isoformat()
    except Exception:
        return datetime.now(timezone.utc).isoformat()


def _clean_html(text: str) -> str:
    """Strip basic HTML tags from summary text."""
    import re
    clean = re.sub(r"<[^>]+>", "", text or "")
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:500]  # cap at 500 chars for widget display


def fetch_all_rss() -> list[dict]:
    """
    Fetch and parse all configured RSS feeds.
    Returns a list of normalized news item dicts.
    """
    items = []

    for feed_config in RSS_FEEDS:
        source_id = feed_config["source_id"]
        url = feed_config["url"]
        logger.info(f"Fetching RSS: {feed_config['name']} → {url}")

        try:
            feed = feedparser.parse(url, request_headers={
                "User-Agent": "CityBeautifulBuzz/1.0 (personal news aggregator; +https://github.com/customonion4321/city-beautiful-buzz)",
                "Accept": "application/rss+xml, application/xml, text/xml",
            })

            if feed.bozo and not feed.entries:
                logger.warning(f"  ⚠️  Feed error for {source_id}: {feed.bozo_exception}")
                continue

            logger.info(f"  ✅  Got {len(feed.entries)} entries from {source_id}")

            for entry in feed.entries[:15]:  # max 15 per source
                title = _clean_html(getattr(entry, "title", ""))
                summary = _clean_html(
                    getattr(entry, "summary", "")
                    or getattr(entry, "description", "")
                )
                link = getattr(entry, "link", "")

                if not title or not link:
                    continue

                items.append({
                    "title": title,
                    "summary": summary,
                    "article_url": link,
                    "source_id": source_id,
                    "source_name": feed_config["name"],
                    "source_logo": feed_config["logo"],
                    "language": feed_config["language"],
                    "tier": feed_config["tier"],
                    "published_at": _parse_date(entry),
                    "_raw_id": getattr(entry, "id", link),
                })

        except Exception as e:
            logger.error(f"  ❌  Failed to fetch {source_id}: {e}")
            continue

    return items
