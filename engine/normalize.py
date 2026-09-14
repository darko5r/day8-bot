import re
import string
from difflib import SequenceMatcher


_LEET_TRANSLATION = str.maketrans({"0": "o", "1": "l"})
_PUNCTUATION_TRANSLATION = str.maketrans(
    "",
    "",
    string.punctuation + "¿¡",
)
_EXPRESSIVE_REPEATS_RE = re.compile(r"(.)\1{2,}")


def fuzzy_match(text, candidates, cutoff=0.88):
    for candidate in candidates:
        matcher = SequenceMatcher(None, text, candidate)

        if matcher.real_quick_ratio() < cutoff:
            continue
        if matcher.quick_ratio() < cutoff:
            continue
        if matcher.ratio() >= cutoff:
            return True

    return False


def collapse_expressive_repeats(text):
    # Collapse 3+ repeated characters to one character.
    # This keeps legitimate doubled letters such as "good" intact.
    return _EXPRESSIVE_REPEATS_RE.sub(r"\1", text)


def normalize_message(user_message):
    normalized = user_message.lower().strip().translate(
        _LEET_TRANSLATION
    )
    normalized = normalized.translate(_PUNCTUATION_TRANSLATION)
    normalized = collapse_expressive_repeats(normalized)
    return " ".join(normalized.split())


def exit_candidate(normalized_message):
    # Exit words get one extra tolerance rule for trailing doubled letters:
    # byee -> bye, chauu -> chau.
    return re.sub(r"(.)\1+$", r"\1", normalized_message)
