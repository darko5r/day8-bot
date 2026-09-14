import random

from data import argentine as ar
from data import english as en
from engine.detect import detect_intent
from engine.models import Intent, Prompt
from engine.normalize import normalize_message


PROMPT_BY_NAME = {
    "wellbeing": Prompt.WELLBEING,
    "vibe": Prompt.VIBE,
}


def _dataset(language):
    return ar if language == "argentine" else en


def _set_prompt(memory, prompt, language):
    memory.session.last_prompt = prompt
    memory.session.language = language


def _clear_prompt(memory):
    memory.session.last_prompt = Prompt.NONE


def handle_message(user_message, memory):
    normalized = normalize_message(user_message)
    detection = detect_intent(user_message, normalized, memory)
    memory.session.last_intent = detection.intent
    memory.session.language = detection.language
    data = _dataset(detection.language)

    if detection.intent == Intent.GOODBYE:
        _clear_prompt(memory)
        return random.choice(data.GOODBYE_RESPONSES), True

    if detection.intent == Intent.NAME_SET:
        memory.profile.name = detection.payload
        _clear_prompt(memory)
        if detection.language == "argentine":
            return f"Dee Dee: De una, {detection.payload}. Me lo guardo.", False
        return f"Dee Dee: Seen, {detection.payload}. Mi got U.", False

    if detection.intent == Intent.NAME_RECALL:
        _clear_prompt(memory)
        if memory.profile.name is None:
            if detection.language == "argentine":
                return "Dee Dee: Todavía no me dijiste cómo te llamás.", False
            return "Dee Dee: U ain't told me your name yet.", False

        if detection.language == "argentine":
            return f"Dee Dee: Me dijiste que te llamás {memory.profile.name}.", False
        return f"Dee Dee: U told me your name is {memory.profile.name}.", False

    if detection.intent == Intent.ACTIVITY_RECALL:
        _clear_prompt(memory)
        if memory.task.activity is None:
            if detection.language == "argentine":
                return "Dee Dee: Todavía no me dijiste en qué andabas.", False
            return "Dee Dee: Nah, U ain't told me what U workin on yet.", False

        if detection.language == "argentine":
            return f'Dee Dee: Me dijiste que estabas con: "{memory.task.activity}"', False
        return f'Dee Dee: U told me U workin on: "{memory.task.activity}"', False

    if detection.intent == Intent.MORE_RECALL:
        _clear_prompt(memory)
        if memory.task.activity is None:
            if detection.language == "argentine":
                return "Dee Dee: Todavía no me dijiste en qué andabas.", False
            return "Dee Dee: U ain't told me what U workin on yet.", False

        if detection.language == "argentine":
            focus = memory.task.focus or "todavía no lo guardé"
            return (
                "Dee Dee:\n"
                f"Actividad : {memory.task.activity}\n"
                f"Foco      : {focus}"
            ), False

        focus = memory.task.focus or "not captured yet"
        return (
            "Dee Dee:\n"
            f"Activity : {memory.task.activity}\n"
            f"Focus    : {focus}"
        ), False

    if detection.intent == Intent.NEXT_RECALL:
        _clear_prompt(memory)
        if memory.task.next_step is None:
            if detection.language == "argentine":
                return "Dee Dee: Todavía no me dijiste cuál era el próximo paso.", False
            return "Dee Dee: U ain't told me the next move yet.", False

        if detection.language == "argentine":
            return f"Dee Dee:\nSiguiente : {memory.task.next_step}", False
        return f"Dee Dee:\nNext     : {memory.task.next_step}", False

    if detection.intent == Intent.WELLBEING_QUERY:
        _set_prompt(memory, Prompt.WELLBEING, detection.language)
        return random.choice(data.WELLBEING_RESPONSES), False

    if detection.intent == Intent.WELLBEING_POSITIVE:
        _set_prompt(memory, Prompt.VIBE, detection.language)
        return random.choice(data.POSITIVE_FOLLOWUPS), False

    if detection.intent == Intent.WELLBEING_NEGATIVE:
        _set_prompt(memory, Prompt.WELLBEING_DETAIL, detection.language)
        return random.choice(data.NEGATIVE_FOLLOWUPS), False

    if detection.intent == Intent.WELLBEING_NEUTRAL:
        _set_prompt(memory, Prompt.WELLBEING_DETAIL, detection.language)
        return random.choice(data.NEUTRAL_FOLLOWUPS), False

    if detection.intent == Intent.WELLBEING_DETAIL:
        _clear_prompt(memory)
        return random.choice(data.WELLBEING_DETAIL_ACK), False

    if detection.intent == Intent.GREETING:
        response, prompt_name = random.choice(data.GREETING_OPTIONS)
        _set_prompt(memory, PROMPT_BY_NAME[prompt_name], detection.language)
        return response, False

    if detection.intent == Intent.VIBE_STATEMENT:
        _set_prompt(memory, Prompt.ACTIVITY, detection.language)
        return random.choice(data.VIBE_FOLLOWUPS), False

    if detection.intent == Intent.ACTIVITY_STATEMENT:
        memory.task.activity = detection.payload
        memory.task.focus = None
        memory.task.next_step = None
        _set_prompt(memory, Prompt.ACTIVITY_DETAIL, detection.language)
        return random.choice(data.ACTIVITY_DETAIL_PROMPTS), False

    if detection.intent == Intent.ACTIVITY_DETAIL_STATEMENT:
        memory.task.focus = detection.payload
        memory.task.next_step = None
        _set_prompt(memory, Prompt.NEXT_STEP, detection.language)
        return random.choice(data.NEXT_STEP_PROMPTS), False

    if detection.intent == Intent.NEXT_STEP_STATEMENT:
        memory.task.next_step = detection.payload
        _clear_prompt(memory)
        return random.choice(data.COMPLETION_RESPONSES), False

    _clear_prompt(memory)
    return random.choice(data.UNKNOWN_RESPONSES), False
