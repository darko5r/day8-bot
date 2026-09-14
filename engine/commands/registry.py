from engine.commands.models import CommandId, CommandSpec


COMMAND_SPECS = (
    CommandSpec(
        command_id=CommandId.HELP,
        name="help",
        usage="!help",
        summary="List available Dee Dee commands.",
    ),
    CommandSpec(
        command_id=CommandId.MOTD,
        name="motd",
        usage="!motd",
        summary="Show the DEVNET message of the day.",
    ),
    CommandSpec(
        command_id=CommandId.VERSION,
        name="version",
        usage="!version",
        summary="Show Dee Dee service version information.",
    ),
    CommandSpec(
        command_id=CommandId.UPTIME,
        name="uptime",
        usage="!uptime",
        summary="Show current process uptime.",
    ),
    CommandSpec(
        command_id=CommandId.WHOIS,
        name="whois",
        usage="!whois",
        summary="Show your current scoped Dee Dee profile and task memory.",
        accepts_arguments=True,
    ),
    CommandSpec(
        command_id=CommandId.EXIT,
        name="exit",
        usage="!exit",
        summary="Close the current Dee Dee session.",
    ),
)

COMMANDS_BY_NAME = {spec.name: spec for spec in COMMAND_SPECS}


def command_names():
    return frozenset(COMMANDS_BY_NAME)


def iter_command_specs():
    return COMMAND_SPECS
