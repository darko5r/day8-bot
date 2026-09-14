import random

from data import argentine as ar
from data import english as en
from data.personality import CONTROL_MODE, CORE_PERSONALITY_TEXT
from engine.models import Intent, Tone


FOCUSED_INTENTS = {
    Intent.BOT_IDENTITY_QUERY,
    Intent.BOT_CAPABILITIES_QUERY,
    Intent.NAME_SET,
    Intent.NAME_RECALL,
    Intent.ACTIVITY_RECALL,
    Intent.MORE_RECALL,
    Intent.NEXT_RECALL,
    Intent.VIBE_STATEMENT,
    Intent.ACTIVITY_STATEMENT,
    Intent.ACTIVITY_DETAIL_STATEMENT,
    Intent.NEXT_STEP_STATEMENT,
}

PLAYFUL_INTENTS = {
    Intent.GREETING,
    Intent.GOODBYE,
    Intent.JOKE_REQUEST,
    Intent.TECHNICAL_SUCCESS,
}

SERIOUS_INTENTS = {
    Intent.WELLBEING_NEGATIVE,
    Intent.WELLBEING_NEUTRAL,
    Intent.WELLBEING_DETAIL,
}


def _dataset(language):
    return ar if language == "argentine" else en


def apply_adaptive_tone(detection, memory):
    """Update Dee Dee's observable tone from conversational evidence.

    Personality is fixed; tone is contextual. Genuine discouragement outranks
    sarcasm. Repeated technical setbacks escalate from focused to motivational.
    """
    session = memory.session
    intent = detection.intent

    if intent == Intent.DISCOURAGEMENT:
        session.failure_streak = max(2, session.failure_streak + 1)
        session.tone = Tone.MOTIVATIONAL
        return session.tone

    if intent == Intent.ENGINEERING_ANTIPATTERN:
        session.tone = Tone.SARCASTIC
        return session.tone

    if intent == Intent.TECHNICAL_SETBACK:
        session.failure_streak += 1
        session.tone = (
            Tone.MOTIVATIONAL
            if session.failure_streak >= 2
            else Tone.FOCUSED
        )
        return session.tone

    if intent == Intent.TECHNICAL_SUCCESS:
        session.failure_streak = 0
        session.tone = Tone.PLAYFUL
        return session.tone

    if intent in SERIOUS_INTENTS:
        session.tone = Tone.SERIOUS
        return session.tone

    if intent in PLAYFUL_INTENTS:
        session.tone = Tone.PLAYFUL
        return session.tone

    if intent in FOCUSED_INTENTS:
        session.tone = Tone.FOCUSED
        return session.tone

    return session.tone


def personality_event_response(language, intent, tone):
    data = _dataset(language)

    if intent == Intent.DISCOURAGEMENT:
        return random.choice(data.MOTIVATIONAL_RESPONSES)

    if intent == Intent.ENGINEERING_ANTIPATTERN:
        return random.choice(data.SARCASTIC_ENGINEERING_RESPONSES)

    if intent == Intent.TECHNICAL_SUCCESS:
        return random.choice(data.PLAYFUL_SUCCESS_RESPONSES)

    if intent == Intent.TECHNICAL_SETBACK:
        if tone == Tone.MOTIVATIONAL:
            return random.choice(data.MOTIVATIONAL_RESPONSES)
        return random.choice(data.FOCUSED_SETBACK_RESPONSES)

    raise ValueError(f"unsupported personality event: {intent}")


def joke_response(language):
    return random.choice(_dataset(language).JOKES)


def personality_status_text(memory):
    return "\n".join(
        (
            "*** DEE DEE PERSONALITY",
            f"Core    : {CORE_PERSONALITY_TEXT}",
            f"Tone    : {memory.session.tone.value}",
            f"Control : {CONTROL_MODE}",
            "*** End of PERSONALITY",
        )
    )

