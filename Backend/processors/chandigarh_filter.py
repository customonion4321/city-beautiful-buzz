"""
Chandigarh Geographic Filter — City Beautiful Buzz
===================================================
STRICT HYPERLOCAL FILTER — 100% Chandigarh Only.
Excludes Mohali, Panchkula, Zirakpur, Kharar, and all surrounding areas.
Only accepts stories specifically anchored within the Union Territory of Chandigarh.
"""

import re
import logging

logger = logging.getLogger(__name__)

# ── 1. Positive Chandigarh Anchors ─────────────────────────────────────────────
# MUST match at least one of these strictly Chandigarh-anchored patterns
CHANDIGARH_PATTERNS = [
    # City names & aliases
    r"\bchandigarh\b",
    r"\bcity beautiful\b",
    r"चंडीगढ़",
    r"चंडीगढ़",

    # Administration & Local Bodies (UT only)
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
    r"\bchd police\b",
    r"\bchandigarh transport\b",
    r"\bctu\b",
    r"चंडीगढ़ ट्रांसपोर्ट",
    r"\bpunjab and haryana high court\b",
    r"\bhigh court\b",
    r"हाई कोर्ट",
    r"हाईकोर्ट",

    # Chandigarh Educational & Medical Institutions
    r"\bpgi\b",
    r"\bpgimer\b",
    r"पीजीआई",
    r"\bgmch\b",
    r"\bgmch-32\b",
    r"जीएमसीएच",
    r"\bgmsh\b",
    r"\bgmsh-16\b",
    r"\bpec\b",
    r"\bpunjab engineering college\b",
    r"\bccet\b",
    r"\bpanjab university\b",
    r"\bpu chandigarh\b",
    r"\bpu campus\b",
    r"पंजाब यूनिवर्सिटी",
    r"पीयू",

    # Chandigarh Landmarks & Venues
    r"\bsukhna\b",
    r"\bsukhna lake\b",
    r"सुखना",
    r"सुखना लेक",
    r"\brock garden\b",
    r"रॉक गार्डन",
    r"\brose garden\b",
    r"रोज गार्डन",
    r"रोज़ गार्डन",
    r"\bleisure valley\b",
    r"लेजर वैली",
    r"लेज़र वैली",
    r"\belante\b",
    r"\belante mall\b",
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
    r"\bsector 17 plaza\b",
    r"\bsec 17 plaza\b",
    r"प्लाजा",

    # Major Arterial Roads in Chandigarh
    r"\bmadhya marg\b",
    r"मध्य मार्ग",
    r"\bdakshin marg\b",
    r"दक्षिण मार्ग",
    r"\bjan marg\b",
    r"जन मार्ग",
    r"\bhimalaya marg\b",
    r"हिमालय मार्ग",
    r"\bvikas marg\b",
    r"विकास मार्ग",
    r"\bisbt 17\b",
    r"\bisbt 43\b",
    r"\bisbt\b",

    # Chandigarh UT Villages & Colonies (Strictly within UT boundary)
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
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in CHANDIGARH_PATTERNS]

# Regex for Sector numbers: "Sector 17", "Sec 22", "Sector-35", "सेक्टर 15"
SECTOR_REGEX = re.compile(
    r"(?i)\b(?:Sector|Sec\.?|सेक्टर)[-\s]*([0-9]{1,3}[A-Za-z]?)\b"
)

# ── 2. Negative Exclusions (Mohali, Panchkula, Tricity & Distant Cities) ────────
# Stories primarily about these locations MUST be discarded
EXCLUDED_PREFIXES = [
    # Tricity neighbors — EXCLUDED per user requirement
    r"^mohali\b", r"^panchkula\b", r"^zirakpur\b", r"^kharar\b",
    r"^new chandigarh\b", r"^mullanpur\b", r"^derabassi\b", r"^kalka\b", r"^pinjore\b",
    r"^मोहाली\b", r"^पंचकूला\b", r"^जीरकपुर\b", r"^खरड़\b", r"^मुल्लांपुर\b",

    # Regional cities
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

PREFIX_REGEX = re.compile("|".join(EXCLUDED_PREFIXES), re.IGNORECASE)

# Keywords that indicate Mohali/Panchkula-only stories
NON_CHANDIGARH_KEYWORDS = [
    r"\bmohali mc\b",
    r"\bmunicipal corporation mohali\b",
    r"\bgmada\b",
    r"\bhuda\b",
    r"\bharyana shahar vikas pradhikaran\b",
    r"\bpanchkula mc\b",
    r"\bsector 89\b", # Mohali sector (Chandigarh sectors only go up to 63)
]

COMPILED_NON_CHD = [re.compile(p, re.IGNORECASE) for p in NON_CHANDIGARH_KEYWORDS]


def is_chandigarh_relevant(item: dict) -> bool:
    """
    Returns True ONLY if the story is strictly and hyperlocally about
    the Union Territory of Chandigarh.
    """
    title = (item.get("title") or "").strip()
    summary = (item.get("summary") or "").strip()
    combined = f"{title} {summary}".lower()

    # Rule 1: Starts with an excluded city/neighbor prefix
    cleaned_title = re.sub(r"^[^\w]+", "", title)
    if PREFIX_REGEX.search(cleaned_title):
        # Even if prefix matched, only allow if Chandigarh is explicitly mentioned in title
        if "chandigarh" not in title.lower() and "चंडीगढ़" not in title:
            return False

    # Rule 2: Pure Mohali / Panchkula / Zirakpur / Kharar headline check
    neighbor_pattern = r"\b(mohali|panchkula|zirakpur|kharar|मोहाली|पंचकूला|जीरकपुर|खरड़)\b"
    if re.search(neighbor_pattern, title, re.IGNORECASE):
        # If the headline mentions Mohali/Panchkula and DOES NOT mention Chandigarh, REJECT!
        if not re.search(r"\b(chandigarh|chd|चंडीगढ़|चंडीगढ़)\b", title, re.IGNORECASE):
            return False

    # Rule 3: Check for Mohali-specific sector numbers (> Sector 63)
    sector_match = SECTOR_REGEX.search(title) or SECTOR_REGEX.search(summary)
    if sector_match:
        try:
            sec_num = int(re.sub(r"[^\d]", "", sector_match.group(1)))
            # Chandigarh Sectors only go up to 63. Sectors 64+ are in Mohali or Panchkula!
            if sec_num > 63:
                # If sector > 63 and doesn't mention Chandigarh UT explicitly, discard
                if "chandigarh" not in combined and "चंडीगढ़" not in combined:
                    return False
        except (ValueError, IndexError):
            pass

    # Rule 4: Explicit non-Chandigarh local bodies (GMADA, Mohali MC, etc.)
    for non_chd in COMPILED_NON_CHD:
        if non_chd.search(combined):
            if "chandigarh" not in combined and "चंडीगढ़" not in combined:
                return False

    # Rule 5: Positive Match — must hit at least one compiled Chandigarh pattern
    for pattern in COMPILED_PATTERNS:
        if pattern.search(title) or pattern.search(summary):
            return True

    # Rule 6: AllEvents explicitly in Chandigarh
    if item.get("source_id") == "allevents":
        return True

    return False


def filter_chandigarh_only(items: list[dict]) -> list[dict]:
    """
    Filters a list of items to retain ONLY verified, hyperlocal Chandigarh items.
    """
    accepted = []
    rejected_count = 0

    for item in items:
        if is_chandigarh_relevant(item):
            accepted.append(item)
        else:
            rejected_count += 1
            logger.debug(f"Filtered out: {item.get('title')}")

    logger.info(f"📍 Hyperlocal Chandigarh Filter: Retained {len(accepted)} items | Rejected {rejected_count} non-Chandigarh items.")
    return accepted
