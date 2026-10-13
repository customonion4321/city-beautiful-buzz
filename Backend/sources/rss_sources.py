"""
RSS Sources — City Beautiful Buzz
Fetches structured news from targeted hyperlocal Chandigarh RSS feeds,
constrained strictly to the last 24 hours (when:1d).
"""

import feedparser
import logging
import ssl
import certifi
import re
import requests
from datetime import datetime, timezone
from dateutil import parser as date_parser

# ── macOS SSL fix ─────────────────────────────────────────────────────────────
ssl._create_default_https_context = lambda: ssl.create_default_context(
    cafile=certifi.where()
)

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
}

# ─────────────────────────────────────────────────────────────────────────────
# Hyperlocal Chandigarh Feeds: Strictly Last 24 Hours (when:1d)
# ─────────────────────────────────────────────────────────────────────────────
RSS_FEEDS = [
    # ── 1. City Realtime Wire (Past 24h) ─────────────────────────────────────
    {
        "source_id": "google_news_chd_wire",
        "name": "Chandigarh 24h Wire",
        "logo": "tribune.png",
        "url": "https://news.google.com/rss/search?q=Chandigarh+when:1d&hl=en-IN&gl=IN&ceid=IN:en",
        "language": "en",
        "tier": 1,
        "is_aggregator": True,
    },
    # ── 2. Sector-Specific Deep Wire (Past 24h) ──────────────────────────────
    {
        "source_id": "google_news_chd_sectors",
        "name": "Chandigarh Sector Wire",
        "logo": "tribune.png",
        "url": "https://news.google.com/rss/search?q=Chandigarh+Sector+when:1d&hl=en-IN&gl=IN&ceid=IN:en",
        "language": "en",
        "tier": 1,
        "is_aggregator": True,
    },
    # ── 3. Municipal Corporation & Civic Administration (Past 24h) ───────────
    {
        "source_id": "google_news_chd_mc",
        "name": "MC Chandigarh Bulletin",
        "logo": "tribune.png",
        "url": "https://news.google.com/rss/search?q=Chandigarh+Municipal+Corporation+when:1d&hl=en-IN&gl=IN&ceid=IN:en",
        "language": "en",
        "tier": 1,
        "is_aggregator": True,
    },
    {
        "source_id": "google_news_chd_admin",
        "name": "UT Administration Wire",
        "logo": "ht.png",
        "url": "https://news.google.com/rss/search?q=Chandigarh+Administration+when:1d&hl=en-IN&gl=IN&ceid=IN:en",
        "language": "en",
        "tier": 1,
        "is_aggregator": True,
    },
    # ── 4. Traffic Police, Police Cases & Civic Alerts (Past 24h) ────────────
    {
        "source_id": "google_news_chd_police",
        "name": "Chandigarh Police Wire",
        "logo": "ie.png",
        "url": "https://news.google.com/rss/search?q=Chandigarh+Police+when:1d&hl=en-IN&gl=IN&ceid=IN:en",
        "language": "en",
        "tier": 1,
        "is_aggregator": True,
    },
    {
        "source_id": "google_news_chd_traffic",
        "name": "Chandigarh Traffic & Civic",
        "logo": "ie.png",
        "url": "https://news.google.com/rss/search?q=Chandigarh+traffic+when:1d&hl=en-IN&gl=IN&ceid=IN:en",
        "language": "en",
        "tier": 1,
        "is_aggregator": True,
    },
    {
        "source_id": "google_news_chd_civic",
        "name": "Chandigarh Civic Alerts",
        "logo": "ht.png",
        "url": "https://news.google.com/rss/search?q=Chandigarh+water+OR+electricity+OR+road+when:1d&hl=en-IN&gl=IN&ceid=IN:en",
        "language": "en",
        "tier": 1,
        "is_aggregator": True,
    },
    # ── 5. Hindi Feeds (Past 24h) ─────────────────────────────────────────────
    {
        "source_id": "google_news_chd_hi_wire",
        "name": "चंडीगढ़ 24 घंटे समाचार",
        "logo": "amarujala.png",
        "url": "https://news.google.com/rss/search?q=%E0%A4%9A%E0%A4%82%E0%A4%A1%E0%A5%80%E0%A4%97%E0%A4%A2%E0%A4%BC+when:1d&hl=hi&gl=IN&ceid=IN:hi",
        "language": "hi",
        "tier": 1,
        "is_aggregator": True,
    },
    {
        "source_id": "google_news_chd_hi_sectors",
        "name": "चंडीगढ़ सेक्टर डायरी",
        "logo": "amarujala.png",
        "url": "https://news.google.com/rss/search?q=%E0%A4%9A%E0%A4%82%E0%A4%A1%E0%A5%80%E0%A4%97%E0%A4%A2%E0%A4%BC+%E0%A4%B8%E0%A5%87%E0%A4%95%E0%A5%8D%E0%A4%9F%E0%A4%B0+when:1d&hl=hi&gl=IN&ceid=IN:hi",
        "language": "hi",
        "tier": 1,
        "is_aggregator": True,
    },
    {
        "source_id": "google_news_chd_hi_mc",
        "name": "चंडीगढ़ नगर निगम",
        "logo": "amarujala.png",
        "url": "https://news.google.com/rss/search?q=%E0%A4%9A%E0%A4%82%E0%A4%A1%E0%A5%80%E0%A4%97%E0%A4%A2%E0%A4%BC+%E0%A4%A8%E0%A4%97%E0%A4%B0+%E0%A4%A8%E0%A4%BF%E0%A4%97%E0%A4%AE+when:1d&hl=hi&gl=IN&ceid=IN:hi",
        "language": "hi",
        "tier": 1,
        "is_aggregator": True,
    },
    {
        "source_id": "google_news_chd_hi_admin",
        "name": "चंडीगढ़ प्रशासन अपडेट",
        "logo": "amarujala.png",
        "url": "https://news.google.com/rss/search?q=%E0%A4%9A%E0%A4%82%E0%A4%A1%E0%A5%80%E0%A4%97%E0%A4%A2%E0%A4%BC+%E0%A4%AA%E0%A5%8D%E0%A4%B0%E0%A4%B6%E0%A4%BE%E0%A4%B8%E0%A4%A8+when:1d&hl=hi&gl=IN&ceid=IN:hi",
        "language": "hi",
        "tier": 1,
        "is_aggregator": True,
    },
    # ── 6. Outlets Regional City RSS Feeds ───────────────────────────────────
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


def _parse_date(entry) -> str | None:
    """Try multiple date fields and return ISO 8601 string in UTC, or None if unparseable."""
    raw = (
        getattr(entry, "published", None)
        or getattr(entry, "updated", None)
        or getattr(entry, "created", None)
    )
    if not raw:
        return None
    try:
        dt = date_parser.parse(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    except Exception:
        return None


def _clean_html(text: str) -> str:
    """Strip basic HTML tags and unescape entities."""
    clean = re.sub(r"<[^>]+>", "", text or "")
    clean = re.sub(r"&nbsp;|&amp;|&quot;|&#39;", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:500]


def fetch_all_rss() -> list[dict]:
    """
    Fetch and parse all configured RSS feeds using requests with custom headers.
    Restricts entries to those published within the last 24 hours.
    """
    items = []
    session = requests.Session()
    session.headers.update(HEADERS)
    now = datetime.now(timezone.utc)

    for feed_config in RSS_FEEDS:
        source_id = feed_config["source_id"]
        url = feed_config["url"]
        logger.info(f"Fetching RSS (24h): {feed_config['name']} → {url}")

        try:
            resp = session.get(url, timeout=12)
            if resp.status_code != 200:
                logger.warning(f"  ⚠️  HTTP {resp.status_code} for {source_id}")
                continue

            feed = feedparser.parse(resp.text)

            if feed.bozo and not feed.entries:
                logger.warning(f"  ⚠️  Feed parse error for {source_id}: {feed.bozo_exception}")
                continue

            feed_count = 0
            for entry in feed.entries[:100]:
                raw_title = _clean_html(getattr(entry, "title", ""))
                summary = _clean_html(
                    getattr(entry, "summary", "")
                    or getattr(entry, "description", "")
                )
                link = getattr(entry, "link", "")

                if not raw_title or not link:
                    continue

                pub_iso = _parse_date(entry)
                if not pub_iso:
                    continue

                # Strict 24-hour verification on entry level
                try:
                    dt = date_parser.parse(pub_iso)
                    age_hours = (now - dt).total_seconds() / 3600.0
                    if age_hours < -0.25 or age_hours > 24.0:
                        continue
                except Exception:
                    continue

                # Handle Google News title formatting ("Headline - Source Name")
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
                    "published_at": pub_iso,
                    "_raw_id": getattr(entry, "id", link),
                })
                feed_count += 1

            logger.info(f"  ✅  Retained {feed_count} entries within 24h from {source_id}")

        except Exception as e:
            logger.error(f"  ❌  Failed to fetch {source_id}: {e}")
            continue

    return items
