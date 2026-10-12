"""
Web Sources — City Beautiful Buzz
Scrapes Chandigarh news from sites that don't provide RSS feeds.
Uses trafilatura for intelligent article extraction.
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
        "CityBeautifulBuzz/1.0 "
        "(personal news aggregator; "
        "+https://github.com/shivamkapil/city-beautiful-buzz)"
    ),
    "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
    "Accept": "text/html,application/xhtml+xml",
}

REQUEST_TIMEOUT = 15  # seconds

# ─────────────────────────────────────────────────────────────────────────────
# Sites to scrape — Chandigarh-specific pages
# ─────────────────────────────────────────────────────────────────────────────
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
    {
        "source_id": "tricity_tribune",
        "name": "Tricity Tribune (web)",
        "logo": "tribune.png",
        "listing_url": "https://www.tribuneindia.com/news/chandigarh",
        "language": "en",
        "tier": 1,
        "article_selector": ".story-card a.story-title, h2.story-title a",
        "base_url": "https://www.tribuneindia.com",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# Events Source — AllEvents.in
# ─────────────────────────────────────────────────────────────────────────────
ALLEVENTS_URL = "https://allevents.in/chandigarh"


def _get_page(url: str) -> str | None:
    """Download page HTML, return None on failure."""
    try:
        resp = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
            verify=certifi.where(),  # macOS SSL fix
        )
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logger.warning(f"  ⚠️  Could not fetch {url}: {e}")
        return None


def _extract_article_text(url: str) -> str:
    """Use trafilatura to extract main content from an article URL."""
    html = _get_page(url)
    if not html:
        return ""
    text = trafilatura.extract(html, favor_precision=True, include_comments=False)
    return (text or "")[:500]


def _scrape_listing(source_config: dict) -> list[dict]:
    """
    Fetch a listing/index page, extract article links,
    then extract each article's text.
    """
    items = []
    source_id = source_config["source_id"]
    listing_url = source_config["listing_url"]

    logger.info(f"Web scraping listing: {source_id} → {listing_url}")
    html = _get_page(listing_url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    links_found = soup.select(source_config["article_selector"])
    logger.info(f"  Found {len(links_found)} article links on {source_id}")

    for tag in links_found[:10]:  # limit to 10 articles per source
        href = tag.get("href", "")
        title = tag.get_text(strip=True)

        if not href or not title:
            continue

        # make absolute URL if relative
        if href.startswith("/"):
            href = source_config["base_url"].rstrip("/") + href
        if not href.startswith("http"):
            continue

        # Extract full article text using trafilatura
        summary = _extract_article_text(href)

        if not summary:
            summary = title  # fallback: just the title

        items.append({
            "title": title,
            "summary": summary,
            "article_url": href,
            "source_id": source_id,
            "source_name": source_config["name"],
            "source_logo": source_config["logo"],
            "language": source_config["language"],
            "tier": source_config["tier"],
            "published_at": datetime.now(timezone.utc).isoformat(),
            "_raw_id": href,
        })

    return items


def scrape_events_allevents() -> list[dict]:
    """
    Scrape upcoming events from AllEvents.in for Chandigarh.
    Returns list of normalized event dicts.
    """
    logger.info(f"Scraping events: AllEvents.in → {ALLEVENTS_URL}")
    html = _get_page(ALLEVENTS_URL)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    events = []

    # AllEvents uses structured cards — look for event title + date + link
    event_cards = soup.select(".event-card, .event-item, [class*='event']")
    logger.info(f"  Found {len(event_cards)} event cards on AllEvents")

    for card in event_cards[:12]:
        title_tag = card.select_one("h2, h3, .event-title, [class*='title']")
        link_tag = card.select_one("a[href]")
        date_tag = card.select_one("time, .event-date, [class*='date']")

        if not title_tag or not link_tag:
            continue

        title = title_tag.get_text(strip=True)
        href = link_tag.get("href", "")
        if href.startswith("/"):
            href = "https://allevents.in" + href

        date_str = ""
        if date_tag:
            date_str = date_tag.get("datetime", "") or date_tag.get_text(strip=True)

        # Parse date if available
        pub_date = datetime.now(timezone.utc).isoformat()
        if date_str:
            try:
                pub_date = date_parser.parse(date_str).isoformat()
            except Exception:
                pass

        events.append({
            "title": f"📅 {title}",
            "summary": f"Upcoming event in Chandigarh. Tap for details and tickets.",
            "article_url": href,
            "source_id": "allevents",
            "source_name": "AllEvents",
            "source_logo": "allevents.png",
            "language": "en",
            "tier": 3,
            "published_at": pub_date,
            "category": "events",
            "_raw_id": href,
        })

    return events


def fetch_all_web() -> list[dict]:
    """Orchestrate all web scraping. Returns unified list of items."""
    items = []
    for source in WEB_SOURCES:
        try:
            scraped = _scrape_listing(source)
            logger.info(f"  ✅  Got {len(scraped)} items from {source['source_id']}")
            items.extend(scraped)
        except Exception as e:
            logger.error(f"  ❌  Web scrape failed for {source['source_id']}: {e}")

    try:
        events = scrape_events_allevents()
        logger.info(f"  ✅  Got {len(events)} events from AllEvents")
        items.extend(events)
    except Exception as e:
        logger.error(f"  ❌  AllEvents scrape failed: {e}")

    return items
