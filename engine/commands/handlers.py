from data.commands import (
    BOT_BUILD,
    BOT_NAME,
    COMMAND_LAYER_VERSION,
    ENGINE_VERSION,
    MOTD_LINES,
)
from engine.commands.models import (
    CommandAction,
    CommandResult,
    CommandStatus,
)
from engine.commands.registry import iter_command_specs


def _format_uptime(seconds):
    total_seconds = max(0, int(seconds))
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days:02d}d {hours:02d}h {minutes:02d}m {seconds:02d}s"


def handle_help(command, memory, runtime):
    lines = [
        "*** Dee Dee command registry ***",
    ]
    lines.extend(
        f"{spec.usage:<12} {spec.summary}"
        for spec in iter_command_specs()
    )
    lines.extend(
        (
            "*** Command names are case-insensitive.",
            "*** Prefix: !",
        )
    )
    return CommandResult("\n".join(lines))


def handle_motd(command, memory, runtime):
    return CommandResult("\n".join(MOTD_LINES))


def handle_version(command, memory, runtime):
    return CommandResult(
        "\n".join(
            (
                "*** VERSION",
                f"Bot      : {BOT_NAME}",
                f"Build    : {BOT_BUILD}",
                f"Engine   : {ENGINE_VERSION}",
                f"Commands : {COMMAND_LAYER_VERSION}",
                f"Protocol : {runtime.protocol}",
            )
        )
    )


def handle_uptime(command, memory, runtime):
    elapsed = runtime.clock() - runtime.started_at
    return CommandResult(
        f"*** NODE-7 uptime: {_format_uptime(elapsed)}"
    )


def handle_whois(command, memory, runtime):
    if command.argument_text:
        return CommandResult(
            "*** WHOIS R0\n"
            "Cross-user lookup is unavailable in R0.\n"
            "Use !whois with no arguments to inspect your own scoped record.",
            status=CommandStatus.FORBIDDEN,
        )

    nickname = memory.profile.name or "unknown"
    language = memory.session.language.capitalize()
    activity = memory.task.activity or "none"
    focus = memory.task.focus or "none"
    next_step = memory.task.next_step or "none"

    return CommandResult(
        "\n".join(
            (
                f"*** WHOIS {nickname}",
                f"Nick     : {nickname}",
                f"Language : {language}",
                f"Activity : {activity}",
                f"Focus    : {focus}",
                f"Next     : {next_step}",
                "*** End of WHOIS",
            )
        )
    )


def handle_exit(command, memory, runtime):
    return CommandResult(
        "*** Dee Dee session closed.",
        action=CommandAction.EXIT_SESSION,
    )
