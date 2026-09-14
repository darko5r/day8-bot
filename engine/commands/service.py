from difflib import get_close_matches

from engine.commands.handlers import (
    handle_audit,
    handle_authz,
    handle_capabilities,
    handle_exit,
    handle_flag,
    handle_founder,
    handle_help,
    handle_identity,
    handle_joke,
    handle_mood,
    handle_motd,
    handle_policy,
    handle_role,
    handle_scope,
    handle_shutdown,
    handle_uptime,
    handle_users,
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
from engine.trust.models import Capability, ScopeRef


COMMAND_HANDLERS = {
    CommandId.HELP: handle_help,
    CommandId.MOTD: handle_motd,
    CommandId.VERSION: handle_version,
    CommandId.UPTIME: handle_uptime,
    CommandId.WHOIS: handle_whois,
    CommandId.ROLE: handle_role,
    CommandId.FLAG: handle_flag,
    CommandId.CAPABILITIES: handle_capabilities,
    CommandId.USERS: handle_users,
    CommandId.AUDIT: handle_audit,
    CommandId.FOUNDER: handle_founder,
    CommandId.SCOPE: handle_scope,
    CommandId.AUTHZ: handle_authz,
    CommandId.POLICY: handle_policy,
    CommandId.IDENTITY: handle_identity,
    CommandId.SHUTDOWN: handle_shutdown,
    CommandId.JOKE: handle_joke,
    CommandId.MOOD: handle_mood,
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


def _authorization_result(spec, runtime):
    if spec.required_capability is None:
        return None

    if runtime.trust_service is None:
        return CommandResult(
            "*** TRUST0 authorization unavailable.\n"
            f"Required : {spec.required_capability}",
            status=CommandStatus.FORBIDDEN,
        )

    capability = Capability(spec.required_capability)
    decision = runtime.trust_service.authorize(
        runtime.actor_id,
        capability,
        ScopeRef.global_scope(),
    )
    if decision.allowed:
        return None

    reason = decision.reason.value if decision.reason is not None else "policy_denied"
    return CommandResult(
        "*** Access denied.\n"
        f"Required : {spec.required_capability}\n"
        f"Scope    : {decision.scope.label()}\n"
        f"Reason   : {reason}",
        status=CommandStatus.FORBIDDEN,
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

    authorization_result = _authorization_result(spec, runtime)
    if authorization_result is not None:
        return authorization_result

    handler = COMMAND_HANDLERS[spec.command_id]
    return handler(command, memory, runtime)
