from engine.commands.models import (
    CommandParseResult,
    CommandParseStatus,
    ParsedCommand,
)
from engine.native.command_token import normalize_command_token


def parse_command(raw_text, known_names):
    if not raw_text.startswith("!"):
        return CommandParseResult(CommandParseStatus.NOT_COMMAND)

    if len(raw_text) == 1 or raw_text[1].isspace():
        return CommandParseResult(CommandParseStatus.MALFORMED)

    body = raw_text[1:].rstrip()
    if not body:
        return CommandParseResult(CommandParseStatus.MALFORMED)

    parts = body.split(maxsplit=1)
    command_token = parts[0]

    canonical_name = normalize_command_token(command_token)
    if canonical_name is None:
        return CommandParseResult(CommandParseStatus.MALFORMED)
    argument_text = parts[1].strip() if len(parts) == 2 else ""
    parsed = ParsedCommand(
        raw=raw_text,
        name=canonical_name,
        argument_text=argument_text,
    )

    if canonical_name not in known_names:
        return CommandParseResult(
            CommandParseStatus.UNKNOWN,
            parsed,
        )

    return CommandParseResult(
        CommandParseStatus.VALID,
        parsed,
    )
