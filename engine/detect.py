import re

from data import argentine as ar
from data import english as en
from engine.models import Detection, Intent, Prompt
from engine.normalize import exit_candidate, fuzzy_match


NAME_PATTERNS = (
    ("english", r"^\s*(?:my name is|call me)\s+(.+?)\s*[.!?]*\s*$"),
    ("argentine", r"^\s*(?:me llamo|mi nombre es)\s+(.+?)\s*[.!?¡¿]*\s*$"),
)


def _extract_name(user_message):
    for language, pattern in NAME_PATTERNS:
        match = re.match(pattern, user_message, flags=re.IGNORECASE)
        if not match:
            continue

        name = match.group(1).strip().strip("\"'.,!?¿¡")
        if 1 <= len(name) <= 40:
            return language, name

    return None, None


def _contains_any(normalized, candidates):
    return any(phrase in normalized for phrase in candidates)


def _language_hint(normalized, words):
    if ar.GREETING_WORDS.intersection(words):
        return "argentine"
    if ar.MARKERS.intersection(words):
        return "argentine"
    if _contains_any(normalized, ar.WELLBEING_QUESTIONS):
        return "argentine"
    return "english"


def detect_intent(user_message, normalized, memory):
    words = set(normalized.split())
    prompt = memory.session.last_prompt

    name_language, name = _extract_name(user_message)
    if name is not None:
        return Detection(Intent.NAME_SET, name_language, name)

    exit_text = exit_candidate(normalized)
    if exit_text in en.GOODBYE_WORDS:
        return Detection(Intent.GOODBYE, "english")
    if exit_text in ar.GOODBYE_WORDS:
        return Detection(Intent.GOODBYE, "argentine")

    if _contains_any(normalized, en.NAME_RECALL):
        return Detection(Intent.NAME_RECALL, "english")
    if _contains_any(normalized, ar.NAME_RECALL):
        return Detection(Intent.NAME_RECALL, "argentine")

    if (
        _contains_any(normalized, en.ACTIVITY_RECALL)
        or fuzzy_match(normalized, en.ACTIVITY_RECALL, cutoff=0.90)
    ):
        return Detection(Intent.ACTIVITY_RECALL, "english")

    if (
        _contains_any(normalized, ar.ACTIVITY_RECALL)
        or fuzzy_match(normalized, ar.ACTIVITY_RECALL, cutoff=0.90)
    ):
        return Detection(Intent.ACTIVITY_RECALL, "argentine")

    if _contains_any(normalized, en.MORE_RECALL):
        return Detection(Intent.MORE_RECALL, "english")
    if _contains_any(normalized, ar.MORE_RECALL):
        return Detection(Intent.MORE_RECALL, "argentine")

    if _contains_any(normalized, en.NEXT_RECALL):
        return Detection(Intent.NEXT_RECALL, "english")
    if _contains_any(normalized, ar.NEXT_RECALL):
        return Detection(Intent.NEXT_RECALL, "argentine")

    if _contains_any(normalized, en.WELLBEING_QUESTIONS):
        return Detection(Intent.WELLBEING_QUERY, "english")
    if _contains_any(normalized, ar.WELLBEING_QUESTIONS):
        return Detection(Intent.WELLBEING_QUERY, "argentine")

    # Contextual short replies are interpreted using Dee Dee's last prompt.
    if prompt in {Prompt.WELLBEING, Prompt.VIBE}:
        if normalized in en.WELLBEING_NEGATIVE:
            return Detection(Intent.WELLBEING_NEGATIVE, "english")
        if normalized in ar.WELLBEING_NEGATIVE:
            return Detection(Intent.WELLBEING_NEGATIVE, "argentine")

        if normalized in en.WELLBEING_NEUTRAL:
            return Detection(Intent.WELLBEING_NEUTRAL, "english")
        if normalized in ar.WELLBEING_NEUTRAL:
            return Detection(Intent.WELLBEING_NEUTRAL, "argentine")

        if normalized in en.WELLBEING_POSITIVE:
            return Detection(Intent.WELLBEING_POSITIVE, "english")
        if normalized in ar.WELLBEING_POSITIVE:
            return Detection(Intent.WELLBEING_POSITIVE, "argentine")

        if normalized in en.VIBE_ANSWERS:
            return Detection(Intent.VIBE_STATEMENT, "english", user_message.strip())
        if normalized in ar.VIBE_ANSWERS:
            return Detection(Intent.VIBE_STATEMENT, "argentine", user_message.strip())

    if prompt == Prompt.WELLBEING_DETAIL and normalized:
        return Detection(
            Intent.WELLBEING_DETAIL,
            memory.session.language,
            user_message.strip(),
        )

    if prompt == Prompt.ACTIVITY and normalized:
        return Detection(
            Intent.ACTIVITY_STATEMENT,
            memory.session.language,
            user_message.strip(),
        )

    if prompt == Prompt.ACTIVITY_DETAIL and normalized:
        return Detection(
            Intent.ACTIVITY_DETAIL_STATEMENT,
            memory.session.language,
            user_message.strip(),
        )

    if prompt == Prompt.NEXT_STEP and normalized:
        return Detection(
            Intent.NEXT_STEP_STATEMENT,
            memory.session.language,
            user_message.strip(),
        )

    # Outside a strict prompt, recognizable activity phrases can still start a task flow.
    if normalized in en.VIBE_ANSWERS:
        return Detection(Intent.VIBE_STATEMENT, "english", user_message.strip())
    if normalized in ar.VIBE_ANSWERS:
        return Detection(Intent.VIBE_STATEMENT, "argentine", user_message.strip())

    argentine_greeting_phrase = (
        normalized.startswith("que onda")
        or normalized.startswith("qué onda")
    )

    if (
        bool(ar.GREETING_WORDS.intersection(words))
        or argentine_greeting_phrase
        or fuzzy_match(normalized, ar.GREETING_WORDS)
    ):
        return Detection(Intent.GREETING, "argentine")

    if (
        bool(en.GREETING_WORDS.intersection(words))
        or fuzzy_match(normalized, en.GREETING_WORDS)
    ):
        return Detection(Intent.GREETING, "english")

    return Detection(Intent.UNKNOWN, _language_hint(normalized, words))
