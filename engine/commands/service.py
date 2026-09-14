from difflib import get_close_matches

from engine.commands.handlers import (
    handle_exit,
    handle_help,
    handle_motd,
    handle_uptime,
    handle_version,
    handle_whois,
)
from engine.commands.models import (
    CommandId,
    CommandParseStatus,
    CommandResult,
    CommandStatus,
)
from engine.commands.parser import parse_command
from engine.commands.registry import COMMANDS_BY_NAME, command_names


COMMAND_HANDLERS = {
    CommandId.HELP: handle_help,
    CommandId.MOTD: handle_motd,
    CommandId.VERSION: handle_version,
    CommandId.UPTIME: handle_uptime,
    CommandId.WHOIS: handle_whois,
    CommandId.EXIT: handle_exit,
}


def _unknown_command_result(command_name):
    suggestions = get_close_matches(
        command_name,
        sorted(command_names()),
        n=1,
        cutoff=0.72,
    )

    lines = [f"*** Unknown command: !{command_name}"]
    if suggestions:
        lines.append(f"*** Did you mean !{suggestions[0]}?")
    lines.append("*** Type !help for available commands.")
    return CommandResult(
        "\n".join(lines),
        status=CommandStatus.UNKNOWN,
    )


def handle_command(raw_text, memory, runtime):
    parsed = parse_command(raw_text, command_names())

    if parsed.status == CommandParseStatus.NOT_COMMAND:
        return None

    if parsed.status == CommandParseStatus.MALFORMED:
        return CommandResult(
            "*** Malformed command. Use !command [arguments].\n"
            "*** Type !help for available commands.",
            status=CommandStatus.MALFORMED,
        )

    if parsed.status == CommandParseStatus.UNKNOWN:
        return _unknown_command_result(parsed.command.name)

    command = parsed.command
    spec = COMMANDS_BY_NAME[command.name]

    if command.argument_text and not spec.accepts_arguments:
        return CommandResult(
            f"*** {spec.name.upper()} does not accept arguments.\n"
            f"*** Usage: {spec.usage}",
            status=CommandStatus.INVALID_ARGUMENTS,
        )

    handler = COMMAND_HANDLERS[spec.command_id]
    return handler(command, memory, runtime)
