"""
Web Sources — City Beautiful Buzz
Scrapes Chandigarh news with strict 24-hour verification.
Uses trafilatura for intelligent article extraction and metadata date discovery.
"""

import requests
import logging
import ssl
import certifi
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import trafilatura
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
    "Accept": "text/html,application/xhtml+xml",
}

REQUEST_TIMEOUT = 12  # seconds

WEB_SOURCES = [
    {
        "source_id": "chandigarh_media",
        "name": "Chandigarh Media",
        "logo": "chandigarhMedia.png",
        "listing_url": "https://chandigarhmedia.com/",
        "language": "en",
        "tier": 2,
        "article_selector": "h2.entry-title a, h3.entry-title a",
        "base_url": "https://chandigarhmedia.com",
    },
    {
        "source_id": "chandigarh_bytes",
        "name": "Chandigarh Bytes",
        "logo": "chandigarhBytes.png",
        "listing_url": "https://www.chandigarhbytes.com/",
        "language": "en",
        "tier": 2,
        "article_selector": "h2.post-title a, h3.post-title a, .entry-title a",
        "base_url": "https://www.chandigarhbytes.com",
    },
]


def _get_page(url: str) -> str | None:
    """Download page HTML, return None on failure."""
    try:
        resp = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
            verify=certifi.where(),
        )
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logger.warning(f"  ⚠️  Could not fetch {url}: {e}")
        return None


def _scrape_listing(source_config: dict) -> list[dict]:
    """
    Fetch listing page, extract article links, check publication date,
    and retain only articles published strictly within the last 24 hours.
    """
    items = []
    source_id = source_config["source_id"]
    listing_url = source_config["listing_url"]
    now = datetime.now(timezone.utc)

    logger.info(f"Web scraping listing: {source_id} → {listing_url}")
    html = _get_page(listing_url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    links_found = soup.select(source_config["article_selector"])
    logger.info(f"  Found {len(links_found)} article links on {source_id}")

    for tag in links_found[:15]:
        href = tag.get("href", "")
        title = tag.get_text(strip=True)

        if not href or not title:
            continue

        if href.startswith("/"):
            href = source_config["base_url"].rstrip("/") + href
        if not href.startswith("http"):
            continue

        article_html = _get_page(href)
        if not article_html:
            continue

        # Extract metadata date via trafilatura
        meta = trafilatura.extract_metadata(article_html)
        if not meta or not meta.date:
            continue  # No reliable date; skip to guarantee <= 24h freshness

        try:
            dt = date_parser.parse(meta.date)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            age_hours = (now - dt).total_seconds() / 3600.0
            if age_hours < -0.25 or age_hours > 24.0:
                continue  # Older than 24 hours; reject
            pub_iso = dt.isoformat()
        except Exception:
            continue

        summary = trafilatura.extract(article_html, favor_precision=True, include_comments=False)
        summary_clean = (summary or title)[:500]

        items.append({
            "title": title,
            "summary": summary_clean,
            "article_url": href,
            "source_id": source_id,
            "source_name": source_config["name"],
            "source_logo": source_config["logo"],
            "language": source_config["language"],
            "tier": source_config["tier"],
            "published_at": pub_iso,
            "_raw_id": href,
        })

    return items


def fetch_all_web() -> list[dict]:
    """Orchestrate web scraping with 24-hour verification."""
    items = []
    for source in WEB_SOURCES:
        try:
            scraped = _scrape_listing(source)
            logger.info(f"  ✅  Retained {len(scraped)} fresh (<=24h) items from {source['source_id']}")
            items.extend(scraped)
        except Exception as e:
            logger.error(f"  ❌  Web scrape failed for {source['source_id']}: {e}")

    return items
