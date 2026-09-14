import re
import string
from difflib import SequenceMatcher


def fuzzy_match(text, candidates, cutoff=0.88):
    return any(
        SequenceMatcher(None, text, candidate).ratio() >= cutoff
        for candidate in candidates
    )


def collapse_expressive_repeats(text):
    # Collapse 3+ repeated characters to one character.
    # This keeps legitimate doubled letters such as "good" intact.
    return re.sub(r"(.)\1{2,}", r"\1", text)


def normalize_message(user_message):
    normalized = user_message.lower().strip().translate(
        str.maketrans({"0": "o", "1": "l"})
    )
    normalized = normalized.translate(
        str.maketrans("", "", string.punctuation + "¿¡")
    )
    normalized = collapse_expressive_repeats(normalized)
    return " ".join(normalized.split())


def exit_candidate(normalized_message):
    # Exit words get one extra tolerance rule for trailing doubled letters:
    # byee -> bye, chauu -> chau.
    return re.sub(r"(.)\1+$", r"\1", normalized_message)
