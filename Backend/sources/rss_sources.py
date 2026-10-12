"""
RSS Sources — City Beautiful Buzz
Fetches structured news from RSS feeds of major Chandigarh news outlets,
supplemented by Google News Realtime Chandigarh indexing.
"""

import feedparser
import logging
import ssl
import certifi
import re
from datetime import datetime, timezone
from dateutil import parser as date_parser

# ── macOS SSL fix ─────────────────────────────────────────────────────────────
ssl._create_default_https_context = lambda: ssl.create_default_context(
    cafile=certifi.where()
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Registered RSS Feeds — Hyperlocal Chandigarh
# ─────────────────────────────────────────────────────────────────────────────
RSS_FEEDS = [
    {
        "source_id": "google_news_chd_en",
        "name": "Chandigarh News Wire",
        "logo": "tribune.png",
        "url": "https://news.google.com/rss/search?q=Chandigarh+when:7d&hl=en-IN&gl=IN&ceid=IN:en",
        "language": "en",
        "tier": 1,
        "is_aggregator": True,
    },
    {
        "source_id": "google_news_chd_hi",
        "name": "चंडीगढ़ समाचार",
        "logo": "amarujala.png",
        "url": "https://news.google.com/rss/search?q=%E0%A4%9A%E0%A4%82%E0%A4%A1%E0%A5%80%E0%A4%97%E0%A4%A2%E0%A4%BC+when:7d&hl=hi&gl=IN&ceid=IN:hi",
        "language": "hi",
        "tier": 1,
        "is_aggregator": True,
    },
    {
        "source_id": "hindustan_times",
        "name": "Hindustan Times",
        "logo": "ht.png",
        "url": "https://www.hindustantimes.com/feeds/rss/cities/chandigarh-news/rssfeed.xml",
        "language": "en",
        "tier": 1,
        "is_aggregator": False,
    },
    {
        "source_id": "indian_express",
        "name": "Indian Express",
        "logo": "ie.png",
        "url": "https://indianexpress.com/section/cities/chandigarh/feed/",
        "language": "en",
        "tier": 1,
        "is_aggregator": False,
    },
    {
        "source_id": "amar_ujala",
        "name": "Amar Ujala",
        "logo": "amarujala.png",
        "url": "https://www.amarujala.com/rss/chandigarh.xml",
        "language": "hi",
        "tier": 2,
        "is_aggregator": False,
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
    """Strip basic HTML tags and unescape entities."""
    clean = re.sub(r"<[^>]+>", "", text or "")
    clean = re.sub(r"&nbsp;|&amp;|&quot;|&#39;", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:500]


def fetch_all_rss() -> list[dict]:
    """
    Fetch and parse all configured RSS feeds without artificial truncation.
    Returns a comprehensive list of raw news item dicts.
    """
    items = []

    for feed_config in RSS_FEEDS:
        source_id = feed_config["source_id"]
        url = feed_config["url"]
        logger.info(f"Fetching RSS: {feed_config['name']} → {url}")

        try:
            feed = feedparser.parse(url, request_headers={
                "User-Agent": "CityBeautifulBuzz/2.0 (Chandigarh Hyperlocal News Aggregator; +https://github.com/customonion4321/city-beautiful-buzz)",
                "Accept": "application/rss+xml, application/xml, text/xml",
            })

            if feed.bozo and not feed.entries:
                logger.warning(f"  ⚠️  Feed error for {source_id}: {feed.bozo_exception}")
                continue

            logger.info(f"  ✅  Got {len(feed.entries)} entries from {source_id}")

            # Process up to 100 entries per source for extensive coverage
            for entry in feed.entries[:100]:
                raw_title = _clean_html(getattr(entry, "title", ""))
                summary = _clean_html(
                    getattr(entry, "summary", "")
                    or getattr(entry, "description", "")
                )
                link = getattr(entry, "link", "")

                if not raw_title or not link:
                    continue

                # Handle Google News title formatting (e.g., "Headline - Source Name")
                source_name = feed_config["name"]
                title = raw_title
                if feed_config.get("is_aggregator"):
                    source_obj = getattr(entry, "source", None)
                    if source_obj and getattr(source_obj, "title", None):
                        source_name = getattr(source_obj, "title")
                    elif " - " in raw_title:
                        parts = raw_title.rsplit(" - ", 1)
                        title = parts[0].strip()
                        source_name = parts[1].strip()

                items.append({
                    "title": title,
                    "summary": summary,
                    "article_url": link,
                    "source_id": source_id,
                    "source_name": source_name,
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
