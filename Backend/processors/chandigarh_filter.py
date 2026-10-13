"""
Chandigarh Geographic Filter & Hyperlocal Scoring — City Beautiful Buzz
========================================================================
STRICT HYPERLOCAL FILTER — 100% Chandigarh Only.
Eliminates:
- Mohali, Panchkula, Zirakpur, Kharar, and all surrounding Punjab/Haryana bleeds.
- "Chandigarh University" (CU Gharuan in Mohali district).
- Away sports matches (e.g. Ranji Trophy away games against Mumbai).
- Distant Punjab/Haryana state politics merely datelined in Chandigarh.

Calculates an authoritative `hyperlocal_score` and extracts `sector_tag`.
"""

import re
import logging

logger = logging.getLogger(__name__)

# ── 1. Positive Chandigarh Anchors ─────────────────────────────────────────────
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
    r"\bleisure valley\b",
    r"लेजर वैली",
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

    # Major Arterial Roads in Chandigarh
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

# ── 2. Strict Negative Exclusions ──────────────────────────────────────────────
EXCLUDED_PATTERNS = [
    # Private institution in Mohali district often confused with Chandigarh UT
    r"\bchandigarh university\b",
    r"\bcu gharuan\b",
    r"\bgharuan\b",

    # Domestic away-sports matches
    r"\branji trophy\b",
    r"\branji\b",
    r"\bdeshpande\b",
    r"\bhat-trick\b",

    # Peripheral cities and Tricity neighbors
    r"\bmohali\b", r"\bpanchkula\b", r"\bzirakpur\b", r"\bkharar\b",
    r"\bnew chandigarh\b", r"\bmullanpur\b", r"\bderabassi\b", r"\bkalka\b", r"\bpinjore\b",
    r"मोहाली", r"पंचकूला", r"जीरकपुर", r"खरड़", r"मुल्लांपुर",

    # Distant Punjab/Haryana towns
    r"\bludhiana\b", r"\bamritsar\b", r"\bjalandhar\b", r"\bbathinda\b", r"\bpatiala\b",
    r"\brohtak\b", r"\bhisar\b", r"\bkarnal\b", r"\bpanipat\b", r"\bgurugram\b",
    r"\bfaridabad\b", r"\bambala\b", r"\bkurukshetra\b", r"\bshimla\b", r"\bsolan\b",
    r"लुधियाना", r"अमृतसर", r"जालंधर", r"बठिंडा", r"पटियाला", r"रोहतक", r"हिसार",
]

COMPILED_EXCLUDED = [re.compile(p, re.IGNORECASE) for p in EXCLUDED_PATTERNS]

# Specific Mohali/Panchkula agencies
NON_CHANDIGARH_KEYWORDS = [
    r"\bgmada\b",
    r"\bhuda\b",
    r"\bharyana shahar vikas\b",
    r"\bmohali mc\b",
    r"\bpanchkula mc\b",
]
COMPILED_NON_CHD = [re.compile(p, re.IGNORECASE) for p in NON_CHANDIGARH_KEYWORDS]


# ── Sector & Landmark Extractor ───────────────────────────────────────────────
LANDMARKS_MAP = [
    ([r"\bsukhna\b", r"सुखना"], "SUKHNA"),
    ([r"\bpanjab university\b", r"\bpu campus\b", r"\bपीयू\b"], "PU CAMPUS"),
    ([r"\bpgi\b", r"\bpgimer\b", r"पीजीआई"], "PGIMER"),
    ([r"\brock garden\b", r"रॉक गार्डन"], "ROCK GARDEN"),
    ([r"\brose garden\b", r"रोज गार्डन"], "ROSE GARDEN"),
    ([r"\bleisure valley\b", r"लेज़र वैली"], "LEISURE VALLEY"),
    ([r"\belante\b", r"एलांटे", r"एलांते"], "ELANTE"),
    ([r"\bmadhya marg\b", r"मध्य मार्ग"], "MADHYA MARG"),
    ([r"\bdakshin marg\b", r"दक्षिण मार्ग"], "DAKSHIN MARG"),
    ([r"\bhigh court\b", r"हाई कोर्ट", r"हाईकोर्ट"], "HIGH COURT"),
    ([r"\bcapitol complex\b", r"\bsecretariat\b", r"सचिवालय"], "CAPITOL"),
    ([r"\bgmch\b", r"\bgmch-32\b", r"जीएमसीएच"], "GMCH-32"),
    ([r"\bgmsh\b", r"\bgmsh-16\b"], "GMSH-16"),
    ([r"\bhallomajra\b", r"हल्लोमाजरा"], "HALLOMAJRA"),
    ([r"\bdadu majra\b", r"\bdaddumajra\b", r"डड्डूमाजरा"], "DADDUMAJRA"),
    ([r"\bmanimajra\b", r"मणिमाजरा"], "MANIMAJRA"),
    ([r"\bmaloya\b", r"मलोया"], "MALOYA"),
    ([r"\bdhanas\b", r"धनास"], "DHANAS"),
    ([r"\bburail\b", r"बुड़ैल"], "BURAIL"),
    ([r"\bsarangpur\b", r"सारंगपुर"], "SARANGPUR"),
    ([r"chandigarh railway station", r"रेलवे स्टेशन"], "CHD JUNCTION"),
]


def extract_sector_tag(title: str, summary: str) -> str:
    """Extract authoritative sector badge or landmark tag for display."""
    text = f"{title} {summary}"

    # 1. Sector number (Sector 1–63)
    match = SECTOR_REGEX.search(text)
    if match:
        raw_sec = match.group(1).upper()
        digits = re.sub(r"[^\d]", "", raw_sec)
        if digits:
            num = int(digits)
            if 1 <= num <= 63:
                return f"SEC {raw_sec}"

    # 2. Iconic landmark or village
    for kw_list, tag in LANDMARKS_MAP:
        for kw in kw_list:
            if re.search(kw, text, re.IGNORECASE):
                return tag

    # 3. Local bodies
    if re.search(r"\bmc chandigarh\b|\bmunicipal corporation\b|नगर निगम", text, re.IGNORECASE):
        return "MC CHD"
    if re.search(r"\bchandigarh administration\b|\but administration\b|यूटी प्रशासन", text, re.IGNORECASE):
        return "UT ADMIN"
    if re.search(r"\bchandigarh police\b|चंडीगढ़ पुलिस", text, re.IGNORECASE):
        return "CHD POLICE"

    return "CHANDIGARH"


def calculate_hyperlocal_score(item: dict) -> int:
    """
    Computes a civic urgency & hyper-local relevance score.
    Higher score = more deeply anchored in Chandigarh citizen daily life.
    """
    title = (item.get("title") or "").strip()
    summary = (item.get("summary") or "").strip()
    text = f"{title} {summary}".lower()

    score = 10  # base score

    # 1. Sector mentioned (+35 points)
    if SECTOR_REGEX.search(title):
        score += 35
    elif SECTOR_REGEX.search(summary):
        score += 25

    # 2. Civic Local Bodies (+30 points)
    if any(k in text for k in ["municipal corporation", "mc chandigarh", "nagar nigam", "नगर निगम"]):
        score += 30
    if any(k in text for k in ["chandigarh administration", "ut administration", "ut adviser", "administrator", "यूटी प्रशासन"]):
        score += 30
    if any(k in text for k in ["chandigarh police", "traffic police", "traffic advisory", "चंडीगढ़ पुलिस"]):
        score += 25

    # 3. Direct Citizen Disruption / Work (+25 points)
    disruptions = [
        "water supply", "power cut", "electricity cut", "pipeline", "road repair",
        "re-carpeting", "encroachment", "demolition", "challan", "property tax",
        "fog alert", "rain alert", "legacy waste", "dadumajra", "daddumajra"
    ]
    for d in disruptions:
        if d in text:
            score += 25
            break

    # 4. Key Institutions & Landmarks (+20 points)
    landmarks = ["pgi", "pgimer", "gmch", "sukhna", "panjab university", "rock garden", "rose garden", "sector 17"]
    for l in landmarks:
        if l in text:
            score += 20
            break

    # 5. Penalties for noisy state-level political squabbling
    politics_penalty = [
        "aap protest", "congress protest", "bjp protest", "manish sisodia",
        "cheema", "spokesperson", "haryana cm", "punjab cm", "election commission of india",
        "cec", "plea dismissed in high court"
    ]
    for p in politics_penalty:
        if p in text:
            score -= 25
            break

    # 6. Penalty if neighbor mentioned
    if any(n in text for n in ["mohali", "panchkula", "zirakpur"]):
        score -= 15

    return score


def is_chandigarh_relevant(item: dict) -> bool:
    """
    Returns True ONLY if the story is strictly and hyperlocally about
    the Union Territory of Chandigarh.
    """
    title = (item.get("title") or "").strip()
    summary = (item.get("summary") or "").strip()
    combined = f"{title} {summary}"

    # Reject 1: Explicit exclusion of CU Gharuan
    if re.search(r"\b(chandigarh university|cu gharuan|gharuan)\b", combined, re.IGNORECASE):
        return False

    # Reject 2: Ranji Trophy / away cricket match noise
    if re.search(r"\b(ranji trophy|ranji|deshpande hat-trick)\b", combined, re.IGNORECASE):
        return False

    # Reject 3: Explicit Mohali / Panchkula bodies
    for non_chd in COMPILED_NON_CHD:
        if non_chd.search(combined):
            if "chandigarh" not in combined.lower() and "चंडीगढ़" not in combined:
                return False

    # Reject 4: Headline starts with or is predominantly about Mohali/Panchkula/other cities
    headline_reject = r"^(mohali|panchkula|zirakpur|kharar|ludhiana|amritsar|jalandhar|shimla|मोहाली|पंचकूला|जीरकपुर)[\s\:\-]"
    if re.search(headline_reject, title, re.IGNORECASE):
        if "chandigarh" not in title.lower() and "चंडीगढ़" not in title:
            return False

    # Positive Match: Must hit at least one compiled Chandigarh pattern or have a Sector
    for pattern in COMPILED_PATTERNS:
        if pattern.search(combined):
            return True

    if SECTOR_REGEX.search(combined):
        return True

    return False


def filter_chandigarh_only(items: list[dict]) -> list[dict]:
    """
    Filters a list of items to retain ONLY verified, hyperlocal Chandigarh items,
    and attaches `sector_tag` and `hyperlocal_score`.
    """
    accepted = []
    rejected_count = 0

    for item in items:
        if is_chandigarh_relevant(item):
            # Calculate sector tag and civic score
            item["sector_tag"] = extract_sector_tag(item.get("title", ""), item.get("summary", ""))
            item["hyperlocal_score"] = calculate_hyperlocal_score(item)
            accepted.append(item)
        else:
            rejected_count += 1
            logger.debug(f"Filtered out: {item.get('title')}")

    logger.info(f"📍 Hyperlocal Chandigarh Filter: Retained {len(accepted)} items | Rejected {rejected_count} non-Chandigarh items.")
    return accepted
