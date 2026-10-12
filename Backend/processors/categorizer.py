"""
Categorizer — City Beautiful Buzz
Auto-assigns categories to news items based on keyword matching.
Supports both English and Hindi keywords.
"""

import re
import logging

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Category definitions — keyword sets for English + Hindi
# ─────────────────────────────────────────────────────────────────────────────
CATEGORIES: list[dict] = [
    {
        "id": "alerts",
        "label_en": "⚠️ Alert",
        "label_hi": "⚠️ अलर्ट",
        "emoji": "⚠️",
        "keywords": [
            "water supply cut", "power cut", "outage", "water shortage", "electricity cut",
            "flood", "waterlogging", "storm", "rain alert", "fog alert", "cold wave",
            "heat wave", "fire", "accident", "closure", "shutdown",
            "बिजली कटौती", "पानी की कटौती", "बाढ़", "तूफान",
        ],
        "priority": 1,
    },
    {
        "id": "infrastructure",
        "label_en": "🏗️ Infrastructure",
        "label_hi": "🏗️ बुनियादी ढांचा",
        "emoji": "🏗️",
        "keywords": [
            "road", "widening", "construction", "flyover", "underpass", "overbridge",
            "sector", "divider", "traffic", "diversion", "repair", "work", "project",
            "smart city", "development", "parking", "footpath", "drain",
            "सड़क", "निर्माण", "फ्लाईओवर", "पार्किंग",
        ],
        "priority": 2,
    },
    {
        "id": "governance",
        "label_en": "🏛️ Governance",
        "label_hi": "🏛️ प्रशासन",
        "emoji": "🏛️",
        "keywords": [
            "mc", "municipal corporation", "chandigarh administration", "deputy commissioner",
            "commissioner", "court", "high court", "punjab and haryana", "order", "notice",
            "policy", "rule", "ban", "fine", "action", "meeting", "budget", "tender",
            "नगर निगम", "प्रशासन", "अदालत", "आदेश",
        ],
        "priority": 3,
    },
    {
        "id": "events",
        "label_en": "🎭 Events",
        "label_hi": "🎭 कार्यक्रम",
        "emoji": "🎭",
        "keywords": [
            "festival", "event", "fair", "mela", "concert", "show", "exhibition",
            "carnival", "cultural", "programme", "function", "ceremony",
            "navratri", "diwali", "holi", "baisakhi", "lohri", "christmas",
            "inauguration", "launch", "market", "flea", "convention",
            "उत्सव", "मेला", "प्रदर्शनी", "कार्यक्रम",
        ],
        "priority": 4,
    },
    {
        "id": "important_dates",
        "label_en": "📅 Key Dates",
        "label_hi": "📅 महत्वपूर्ण तिथियाँ",
        "emoji": "📅",
        "keywords": [
            "last date", "deadline", "registration", "exam", "schedule",
            "holiday", "bank holiday", "public holiday", "result", "admit card",
            "notification", "apply before", "closing date", "due date",
            "अंतिम तिथि", "परीक्षा", "आवेदन",
        ],
        "priority": 5,
    },
    {
        "id": "education",
        "label_en": "📚 Education",
        "label_hi": "📚 शिक्षा",
        "emoji": "📚",
        "keywords": [
            "pu", "panjab university", "school", "college", "university", "student",
            "admission", "result", "exam", "fees", "scholarship", "merit list",
            "teacher", "education", "ugc", "neet", "jee",
            "पंजाब विश्वविद्यालय", "स्कूल", "कॉलेज", "छात्र",
        ],
        "priority": 6,
    },
    {
        "id": "health",
        "label_en": "🏥 Health",
        "label_hi": "🏥 स्वास्थ्य",
        "emoji": "🏥",
        "keywords": [
            "hospital", "pgimer", "gmc", "health", "disease", "dengue", "malaria",
            "vaccination", "camp", "doctor", "patient", "health camp", "treatment",
            "स्वास्थ्य", "अस्पताल", "टीकाकरण", "बीमारी",
        ],
        "priority": 7,
    },
    {
        "id": "sports",
        "label_en": "🏏 Sports",
        "label_hi": "🏏 खेल",
        "emoji": "🏏",
        "keywords": [
            "cricket", "football", "hockey", "badminton", "tournament", "match",
            "stadium", "sports", "player", "championship", "gold", "medal",
            "खेल", "क्रिकेट", "टूर्नामेंट",
        ],
        "priority": 8,
    },
    {
        "id": "lifestyle",
        "label_en": "🍽️ Lifestyle",
        "label_hi": "🍽️ जीवनशैली",
        "emoji": "🍽️",
        "keywords": [
            "restaurant", "cafe", "food", "open", "launch", "new", "shopping",
            "mall", "trend", "fashion", "lifestyle", "weekend", "night life",
            "eat", "dine",
        ],
        "priority": 9,
    },
    {
        "id": "safety",
        "label_en": "🔐 Safety",
        "label_hi": "🔐 सुरक्षा",
        "emoji": "🔐",
        "keywords": [
            "crime", "robbery", "theft", "fraud", "arrest", "police", "fir",
            "scam", "murder", "assault", "cybercrime", "missing", "drug",
            "अपराध", "चोरी", "गिरफ्तारी", "पुलिस",
        ],
        "priority": 10,
    },
]

# Default when nothing matches
DEFAULT_CATEGORY = {
    "id": "general",
    "label_en": "📰 General",
    "label_hi": "📰 सामान्य",
    "emoji": "📰",
}


def categorize(item: dict) -> dict:
    """
    Assign a category to a single news item based on keyword matching.
    Matches against both title and summary fields.
    Returns the item dict with 'category_id', 'category_label_en', 'category_label_hi' added.
    """
    text = (
        (item.get("title", "") + " " + item.get("summary", ""))
        .lower()
    )

    # If already assigned (e.g., events from AllEvents)
    if item.get("category"):
        for cat in CATEGORIES:
            if cat["id"] == item["category"]:
                item["category_id"] = cat["id"]
                item["category_label_en"] = cat["label_en"]
                item["category_label_hi"] = cat["label_hi"]
                return item

    for cat in sorted(CATEGORIES, key=lambda c: c["priority"]):
        for keyword in cat["keywords"]:
            if keyword.lower() in text:
                item["category_id"] = cat["id"]
                item["category_label_en"] = cat["label_en"]
                item["category_label_hi"] = cat["label_hi"]
                return item

    # Fallback
    item["category_id"] = DEFAULT_CATEGORY["id"]
    item["category_label_en"] = DEFAULT_CATEGORY["label_en"]
    item["category_label_hi"] = DEFAULT_CATEGORY["label_hi"]
    return item


def categorize_all(items: list[dict]) -> list[dict]:
    """Categorize all items in a list."""
    return [categorize(item) for item in items]
