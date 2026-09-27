"""
Text preprocessing and emergency-signal detection.
"""

import re


# Strong emergency words/phrases.
# These are used as a safety net so unusual wording
# does not get silently classified as LOW.
EMERGENCY_TERMS = [
    "explosion",
    "exploded",
    "explode",
    "blast",
    "blown up",
    "blew up",

    "fire",
    "fire broke out",
    "flames",
    "burning",
    "smoke",

    "collapse",
    "collapsed",
    "building came down",
    "trapped",

    "injured",
    "injury",
    "hurt",
    "bleeding",
    "unconscious",
    "medical emergency",

    "accident",
    "crash",
    "crashed",
    "collision",

    "flood",
    "flooding",
    "water rising",

    "shooting",
    "shots fired",
    "gunshot",
    "gunshots",
    "robbery",
    "assault",

    "missing person",
    "missing child",

    "gas leak",
    "evacuation",
    "evacuating",
    "rescue",
    "ambulance",
    "emergency",
    "send help",
    "need help"
]


# Words that can indicate that an emergency term
# is being discussed rather than actually occurring.
CONTEXT_EXCLUSIONS = [
    "movie",
    "film",
    "filming",
    "documentary",
    "drill",
    "fireworks",
    "video game",
    "fictional",
    "yesterday",
    "last week",
    "old story",
    "museum exhibit"
]


def clean_text(text):
    """
    Basic preprocessing for emergency reports.
    """

    text = str(text).lower()

    text = re.sub(
        r"http\S+|www\S+",
        "",
        text
    )

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


def contains_emergency_signal(text):
    """
    Check whether a report contains a potentially
    important emergency term. Ensures slang/idioms with hazard words
    are excluded.

    Returns:
        bool
    """
    from src.relevance.idiom_detector import is_slang_or_figurative
    is_slang, _ = is_slang_or_figurative(text)
    if is_slang:
        return False

    cleaned = clean_text(text)

    for term in EMERGENCY_TERMS:
        if re.search(r"\b" + re.escape(term) + r"\b", cleaned):
            return True
    return False


def has_context_exclusion(text):
    """
    Detect contexts where an emergency word may not
    describe a real emergency.
    """
    from src.relevance.idiom_detector import is_slang_or_figurative
    is_slang, reason = is_slang_or_figurative(text)
    if reason == "authentic_emergency_signal_present":
        return False
    if is_slang:
        return True

    cleaned = clean_text(text)

    for phrase in CONTEXT_EXCLUSIONS:
        if re.search(r"\b" + re.escape(phrase) + r"\b", cleaned):
            return True
    return False