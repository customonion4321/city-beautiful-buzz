"""
Chandigarh Geographic Filter — City Beautiful Buzz
===================================================
Strictly filters out regional/national noise (Ludhiana, Delhi, Himachal,
Uttarakhand, Bihar, etc.) to ensure 100% of items are genuinely about
Chandigarh and its immediate Tri-city area.
"""

import re
import logging

logger = logging.getLogger(__name__)

# Exact word boundary keywords (avoids "electricity" matching "tricity"!)
CHANDIGARH_PATTERNS = [
    # City names
    r"\bchandigarh\b",
    r"\bcity beautiful\b",
    r"\btricity\b",
    r"\btri-city\b",
    r"चंडीगढ़",
    r"चंडीगढ़",
    r"ट्राईसिटी",
    r"ट्राइसिटी",

    # Sector regex: Sector 1 to 99, Sec 17, सेक्टर 17, etc.
    r"\b(?:sector|sec\.?)[-\s]*([0-9]{1,2}[a-z]?)\b",
    r"सेक्टर[-\s]*([0-9]{1,2}[a-z]?)",

    # Administration & Local Bodies
    r"\bchandigarh administration\b",
    r"\but administration\b",
    r"यूटी प्रशासन",
    r"चंडीगढ़ प्रशासन",
    r"\bmunicipal corporation chandigarh\b",
    r"\bchandigarh mc\b",
    r"\bmc chandigarh\b",
    r"\bmcc\b",
    r"नगर निगम चंडीगढ़",
    r"\bchandigarh police\b",
    r"चंडीगढ़ पुलिस",
    r"\bchandigarh transport\b",
    r"\bctu\b",
    r"चंडीगढ़ ट्रांसपोर्ट",
    r"\bhigh court\b",
    r"हाई कोर्ट",
    r"हाईकोर्ट",

    # Institutions
    r"\bpgi\b",
    r"\bpgimer\b",
    r"पीजीआई",
    r"\bgmch\b",
    r"\bgmch-32\b",
    r"जीएमसीएच",
    r"\bgmsh\b",
    r"\bgmsh-16\b",
    r"\bpec\b",
    r"\bpanjab university\b",
    r"\bpu chandigarh\b",
    r"\bpu campus\b",
    r"पंजाब यूनिवर्सिटी",
    r"पीयू",

    # Landmarks & Places
    r"\bsukhna\b",
    r"सुखना",
    r"\brock garden\b",
    r"रॉक गार्डन",
    r"\brose garden\b",
    r"रोज गार्डन",
    r"रोज़ गार्डन",
    r"\bleisure valley\b",
    r"लेजर वैली",
    r"लेज़र वैली",
    r"\belante\b",
    r"एलांटे",
    r"एलांते",
    r"\bcapitol complex\b",
    r"कैपिटल कॉम्प्लेक्स",
    r"\bopen hand\b",
    r"ओपन हैंड",
    r"\btagore theatre\b",
    r"टैगोर थिएटर",
    r"\bkala gram\b",
    r"कलाग्राम",

    # Roads
    r"\bmadhya marg\b",
    r"मध्य मार्ग",
    r"\bdakshin marg\b",
    r"दक्षिण मार्ग",
    r"\bjan marg\b",
    r"जन मार्ग",
    r"\bhimalaya marg\b",
    r"हिमालय मार्ग",
    r"\bisbt 17\b",
    r"\bisbt 43\b",
    r"\bisbt\b",

    # Villages & Local Areas
    r"\bhallomajra\b",
    r"हल्लोमाजरा",
    r"\bdadu majra\b",
    r"\bdaddumajra\b",
    r"डड्डूमाजरा",
    r"\bmanimajra\b",
    r"मणिमाजरा",
    r"\bmaloya\b",
    r"मलोया",
    r"\bdhanas\b",
    r"धनास",
    r"\bburail\b",
    r"बुड़ैल",
    r"\bkajheri\b",
    r"कजेहड़ी",
    r"\battawa\b",
    r"अटावा",
    r"\bdaria\b",
    r"दड़वा",
    r"\bmauli jagran\b",
    r"मौली जागरां",
    r"\bbehlana\b",
    r"बहलाना",
    r"\bkaimbwala\b",
    r"कैंबवाला",
    r"\bsarangpur\b",
    r"सारंगपुर",
    r"\bkhuda lahora\b",
    r"खुड्डा लाहौरा",
    r"\bkhuda jassu\b",
    r"खुड्डा जस्सू",
    r"\bkhuda ali sher\b",
    r"खुड्डा अली शेर",
    r"\bkishangarh\b",
    r"किशनगढ़",

    # Immediate Tri-city
    r"\bmohali\b",
    r"मोहाली",
    r"\bsas nagar\b",
    r"\bpanchkula\b",
    r"पंचकूला",
    r"\bzirakpur\b",
    r"जीरकपुर",
    r"\bkharar\b",
    r"खरड़",
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in CHANDIGARH_PATTERNS]

# ── 2. Negative Regional Prefixes (Distant cities) ─────────────────────────────
EXCLUDED_LOCATION_PREFIXES = [
    r"^ludhiana\b", r"^amritsar\b", r"^jalandhar\b", r"^ferozepur\b",
    r"^bathinda\b", r"^hoshiarpur\b", r"^tarn taran\b", r"^patiala\b",
    r"^gurdaspur\b", r"^pathankot\b", r"^moga\b", r"^kapurthala\b",
    r"^rohtak\b", r"^hisar\b", r"^karnal\b", r"^panipat\b", r"^gurugram\b",
    r"^faridabad\b", r"^sonipat\b", r"^ambala\b", r"^kurukshetra\b",
    r"^shimla\b", r"^solan\b", r"^dharamshala\b", r"^kullu\b", r"^manali\b",
    r"^mandi\b", r"^bilaspur\b", r"^una\b", r"^kangra\b", r"^himachal\b",
    r"^delhi\b", r"^new delhi\b", r"^kanpur\b", r"^lucknow\b", r"^noida\b",
    r"^badrinath\b", r"^kedarnath\b", r"^dehradun\b", r"^uttarakhand\b",
    r"^bhagalpur\b", r"^patna\b", r"^bihar\b", r"^kashmir\b", r"^srinagar\b",
    r"^लुधियाना\b", r"^अमृतसर\b", r"^जालंधर\b", r"^बठिंडा\b", r"^पटियाला\b",
    r"^रोहतक\b", r"^हिसार\b", r"^गुरुग्राम\b", r"^फरीदाबाद\b",
    r"^शिमला\b", r"^सोलन\b", r"^धर्मशाला\b", r"^हिमाचल\b",
    r"^दिल्ली\b", r"^कानपुर\b", r"^लखनऊ\b", r"^बद्रीनाथ\b", r"^देहरादून\b",
]

PREFIX_REGEX = re.compile("|".join(EXCLUDED_LOCATION_PREFIXES), re.IGNORECASE)

# National / Non-Chandigarh Distractions (Immediate Disqualifiers)
NATIONAL_DISTRACTIONS = [
    "delhi cops enter bangla sahib",
    "himachal cabinet meeting",
    "badrinath donation",
    "delhi to kanpur",
    "bhagalpur police",
    "shahi imam targets dhirendra shastri",
    "kashmiri saffron and walnuts",
    "amritsar airport",
    "tarn taran",
    "monkey sterilisation",
    "unsung jewish soldiers",
    "farmers golden harvest floated in punjab",
    "satauj rewired itself",
    "frequently mentioned achievements like daytime electricity",
    "daytime electricity and canal water for farmers",
]


def is_chandigarh_relevant(item: dict) -> bool:
    """
    Returns True ONLY if the story is genuinely located in or directly
    pertains to Chandigarh or the immediate Tri-city area.
    """
    title = (item.get("title") or "").strip()
    summary = (item.get("summary") or "").strip()
    combined = f"{title} {summary}".lower()

    # Disqualification 1: Immediate national phrases
    for dist in NATIONAL_DISTRACTIONS:
        if dist in combined:
            return False

    # Disqualification 2: Starts with another city prefix without Chandigarh mention
    cleaned_title = re.sub(r"^[^\w]+", "", title)
    if PREFIX_REGEX.search(cleaned_title):
        if "chandigarh" not in title.lower() and "चंडीगढ़" not in title:
            return False

    # Qualification: Match at least one compiled word-boundary pattern
    for pattern in COMPILED_PATTERNS:
        if pattern.search(title) or pattern.search(summary):
            return True

    # Qualification: Events on AllEvents Chandigarh
    if item.get("source_id") == "allevents":
        return True

    return False


def filter_chandigarh_only(items: list[dict]) -> list[dict]:
    """
    Filters a list of items to retain ONLY verified Chandigarh/Tricity items.
    """
    accepted = []
    rejected_count = 0

    for item in items:
        if is_chandigarh_relevant(item):
            accepted.append(item)
        else:
            rejected_count += 1
            logger.debug(f"Filtered out non-Chandigarh story: {item.get('title')}")

    logger.info(f"📍 Chandigarh Filter: Retained {len(accepted)} items | Rejected {rejected_count} non-Chandigarh items.")
    return accepted
