from dataclasses import dataclass, field
from enum import Enum


class Intent(str, Enum):
    GREETING = "greeting"
    GOODBYE = "goodbye"
    WELLBEING_QUERY = "wellbeing_query"
    WELLBEING_POSITIVE = "wellbeing_positive"
    WELLBEING_NEGATIVE = "wellbeing_negative"
    WELLBEING_NEUTRAL = "wellbeing_neutral"
    WELLBEING_DETAIL = "wellbeing_detail"
    VIBE_STATEMENT = "vibe_statement"
    ACTIVITY_STATEMENT = "activity_statement"
    ACTIVITY_DETAIL_STATEMENT = "activity_detail_statement"
    NEXT_STEP_STATEMENT = "next_step_statement"
    ACTIVITY_RECALL = "activity_recall"
    MORE_RECALL = "more_recall"
    NEXT_RECALL = "next_recall"
    NAME_SET = "name_set"
    NAME_RECALL = "name_recall"
    BOT_IDENTITY_QUERY = "bot_identity_query"
    BOT_CAPABILITIES_QUERY = "bot_capabilities_query"
    JOKE_REQUEST = "joke_request"
    DISCOURAGEMENT = "discouragement"
    ENGINEERING_ANTIPATTERN = "engineering_antipattern"
    TECHNICAL_SETBACK = "technical_setback"
    TECHNICAL_SUCCESS = "technical_success"
    UNKNOWN = "unknown"


class Prompt(str, Enum):
    NONE = "none"
    WELLBEING = "wellbeing"
    VIBE = "vibe"
    WELLBEING_DETAIL = "wellbeing_detail"
    ACTIVITY = "activity"
    ACTIVITY_DETAIL = "activity_detail"
    NEXT_STEP = "next_step"


class Tone(str, Enum):
    SARCASTIC = "sarcastic"
    PLAYFUL = "playful"
    FOCUSED = "focused"
    SERIOUS = "serious"
    MOTIVATIONAL = "motivational"


@dataclass
class SessionMemory:
    language: str = "english"
    last_prompt: Prompt = Prompt.NONE
    last_intent: Intent = Intent.UNKNOWN
    tone: Tone = Tone.FOCUSED
    failure_streak: int = 0


@dataclass
class TaskMemory:
    activity: str | None = None
    focus: str | None = None
    next_step: str | None = None


@dataclass
class ProfileMemory:
    name: str | None = None


@dataclass
class ConversationMemory:
    session: SessionMemory = field(default_factory=SessionMemory)
    task: TaskMemory = field(default_factory=TaskMemory)
    profile: ProfileMemory = field(default_factory=ProfileMemory)


@dataclass(frozen=True)
class Detection:
    intent: Intent
    language: str
    payload: str | None = None
