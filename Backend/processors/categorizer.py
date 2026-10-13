"""
Categorizer — City Beautiful Buzz
Auto-assigns categories to news items based on regex word-boundary matching.
Prevents substring collision bugs (e.g. 'inroads' matching 'road', 'network' matching 'work').
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
            r"water supply cut", r"power cut", r"power outage", r"water shortage",
            r"electricity cut", r"pipeline burst", r"waterlogging", r"flood alert",
            r"heavy rain alert", r"fog alert", r"cold wave", r"heat wave",
            r"fire outbreak", r"demolition drive", r"encroachment drive",
            r"road closure", r"traffic diversion", r"traffic halted",
            r"बिजली कटौती", r"पानी की कटौती", r"बाढ़", r"जलभराव", r"कोहरे का अलर्ट",
        ],
        "priority": 1,
    },
    {
        "id": "infrastructure",
        "label_en": "🏗️ Infrastructure",
        "label_hi": "🏗️ बुनियादी ढांचा",
        "emoji": "🏗️",
        "keywords": [
            r"road widening", r"re-carpeting", r"road repair", r"construction work",
            r"flyover", r"underpass", r"overbridge", r"cycle track", r"footpath",
            r"drainage system", r"underground parking", r"smart city project",
            r"roundabout", r"streetlights", r"railway station", r"master plan",
            r"legacy waste", r"garbage plant", r"dadumajra", r"daddumajra",
            r"सड़क निर्माण", r"सड़क मरम्मत", r"फ्लाईओवर", r"अंडरपास", r"पार्किंग व्यवस्था",
        ],
        "priority": 2,
    },
    {
        "id": "governance",
        "label_en": "🏛️ Governance",
        "label_hi": "🏛️ प्रशासन",
        "emoji": "🏛️",
        "keywords": [
            r"municipal corporation", r"chandigarh administration", r"ut administration",
            r"ut adviser", r"administrator", r"deputy commissioner", r"dc chandigarh",
            r"mayor", r"mc poll", r"electoral roll", r"voter list", r"property tax",
            r"general house", r"tender", r"cbi arrest", r"cbi probe", r"lokpal",
            r"high court order", r"judicial", r"notification",
            r"नगर निगम", r"यूटी प्रशासन", r"चंडीगढ़ प्रशासन", r"सलाहकार", r"प्रशासक",
            r"मेयर", r"मतदाता सूची", r"संपत्ति कर", r"टेंडर",
        ],
        "priority": 3,
    },
    {
        "id": "events",
        "label_en": "🎭 Events",
        "label_hi": "🎭 कार्यक्रम",
        "emoji": "🎭",
        "keywords": [
            r"festival", r"exhibition", r"fair", r"mela", r"concert",
            r"tagore theatre", r"kala gram", r"rose festival", r"carnival",
            r"cultural fest", r"navratri", r"diwali mela", r"dussehra",
            r"handicraft exhibition", r"book fair", r"marathon",
            r"उत्सव", r"मेला", r"प्रदर्शनी", r"सांस्कृतिक कार्यक्रम", r"टैगोर थिएटर",
        ],
        "priority": 4,
    },
    {
        "id": "education",
        "label_en": "📚 Education",
        "label_hi": "📚 शिक्षा",
        "emoji": "📚",
        "keywords": [
            r"panjab university", r"\bpu\b campus", r"pu senate", r"pu syndicate",
            r"punjab engineering college", r"\bpec\b", r"\bccet\b",
            r"school admission", r"college admission", r"ugc pay scale",
            r"teachers protest", r"board exam", r"merit list",
            r"पंजाब विश्वविद्यालय", r"कॉलेज", r"स्कूल", r"छात्र", r"दाखिला",
        ],
        "priority": 5,
    },
    {
        "id": "health",
        "label_en": "🏥 Health",
        "label_hi": "🏥 स्वास्थ्य",
        "emoji": "🏥",
        "keywords": [
            r"\bpgi\b", r"\bpgimer\b", r"\bgmch\b", r"\bgmch-32\b", r"\bgmsh\b", r"\bgmsh-16\b",
            r"hospital", r"dengue", r"chikungunya", r"swine flu", r"vaccination drive",
            r"blood donation camp", r"doctor strike", r"health department",
            r"पीजीआई", r"अस्पताल", r"स्वास्थ्य", r"डेंगू", r"टीकाकरण",
        ],
        "priority": 6,
    },
    {
        "id": "safety",
        "label_en": "🔐 Safety",
        "label_hi": "🔐 सुरक्षा",
        "emoji": "🔐",
        "keywords": [
            r"chandigarh police", r"chd police", r"cyber crime", r"cyber cell",
            r"arrested", r"police encounter", r"naka", r"challan drive",
            r"pistol", r"weapon seized", r"burglary", r"snatching",
            r"drunken driving", r"hit and run", r"fir registered",
            r"चंडीगढ़ पुलिस", r"गिरफ्तार", r"अपराध", r"चोरी", r"चालान",
        ],
        "priority": 7,
    },
    {
        "id": "sports",
        "label_en": "🏏 Sports",
        "label_hi": "🏏 खेल",
        "emoji": "🏏",
        "keywords": [
            r"sector 16 stadium", r"sector 42 stadium", r"lake club", r"golf club",
            r"inter-college sports", r"state tournament", r"athletics meet",
            r"skating rink", r"chandigarh marathon",
            r"स्टेडियम", r"प्रतियोगिता", r"खिलाड़ी",
        ],
        "priority": 8,
    },
    {
        "id": "lifestyle",
        "label_en": "🍽️ Lifestyle",
        "label_hi": "🍽️ जीवनशैली",
        "emoji": "🍽️",
        "keywords": [
            r"elante mall", r"sector 17 plaza", r"sukhna lake promenade",
            r"gedi route", r"cafe opening", r"food festival", r"shopping festival",
            r"मॉल", r"खान-पान",
        ],
        "priority": 9,
    },
]

DEFAULT_CATEGORY = {
    "id": "governance",  # Most unclassified local civic news relates to governance
    "label_en": "🏛️ Civic",
    "label_hi": "🏛️ प्रशासन",
    "emoji": "🏛️",
}

# Compile patterns safely with regex word boundaries
COMPILED_CATEGORIES = []
for cat in CATEGORIES:
    compiled_patterns = []
    for kw in cat["keywords"]:
        # If already regex (starts with \b or contains brackets), compile directly
        if r"\b" in kw or "[" in kw:
            pattern = re.compile(kw, re.IGNORECASE)
        elif re.search(r"[\u0900-\u097F]", kw):
            # Devanagari boundary
            pattern = re.compile(re.escape(kw), re.IGNORECASE)
        else:
            # English word boundary
            pattern = re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE)
        compiled_patterns.append(pattern)
    COMPILED_CATEGORIES.append({
        "config": cat,
        "patterns": compiled_patterns,
    })


def categorize(item: dict) -> dict:
    """
    Assign a category to a single news item based on boundary regex matching.
    Matches against both title and summary fields.
    """
    title = item.get("title", "")
    summary = item.get("summary", "")
    text = f"{title} {summary}"

    # If already set by specific scraper (e.g. events)
    if item.get("category"):
        for entry in COMPILED_CATEGORIES:
            cat = entry["config"]
            if cat["id"] == item["category"]:
                item["category_id"] = cat["id"]
                item["category_label_en"] = cat["label_en"]
                item["category_label_hi"] = cat["label_hi"]
                return item

    # Match in order of priority (Alerts -> Infrastructure -> Governance -> Events -> ...)
    for entry in sorted(COMPILED_CATEGORIES, key=lambda c: c["config"]["priority"]):
        cat = entry["config"]
        for pattern in entry["patterns"]:
            if pattern.search(text):
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
