from engine.commands.models import CommandId, CommandSpec
from engine.trust.models import Capability


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
        summary="Show the Dee Dee network message of the day.",
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
        usage="!whois [id]",
        summary="Show self profile or authorized identity information.",
        accepts_arguments=True,
    ),
    CommandSpec(
        command_id=CommandId.ROLE,
        name="role",
        usage="!role [id] | !role set <id> <role>",
        summary="Inspect or manage service authority roles.",
        accepts_arguments=True,
    ),
    CommandSpec(
        command_id=CommandId.FLAG,
        name="flag",
        usage="!flag [id] | !flag add|remove <id> <flag>",
        summary="Inspect or manage Dee Dee service flags.",
        accepts_arguments=True,
    ),
    CommandSpec(
        command_id=CommandId.CAPABILITIES,
        name="capabilities",
        usage="!capabilities [id]",
        summary="Show effective authorization capabilities.",
        accepts_arguments=True,
    ),
    CommandSpec(
        command_id=CommandId.USERS,
        name="users",
        usage="!users",
        summary="List identities visible in the current authorization scope.",
    ),
    CommandSpec(
        command_id=CommandId.AUDIT,
        name="audit",
        usage="!audit [count]",
        summary="Show recent authority changes (SOP or Founder).",
        accepts_arguments=True,
        required_capability=Capability.SERVICE_AUDIT.value,
    ),
    CommandSpec(
        command_id=CommandId.FOUNDER,
        name="founder",
        usage="!founder | !founder transfer <id> CONFIRM",
        summary="Show Founder or transfer root authority.",
        accepts_arguments=True,
    ),
    CommandSpec(
        command_id=CommandId.SCOPE,
        name="scope",
        usage="!scope",
        summary="Show the current authorization scope.",
    ),
    CommandSpec(
        command_id=CommandId.AUTHZ,
        name="authz",
        usage="!authz <capability> [scope]",
        summary="Explain your authorization decision for a capability.",
        accepts_arguments=True,
    ),
    CommandSpec(
        command_id=CommandId.POLICY,
        name="policy",
        usage="!policy <capability>",
        summary="Inspect authorization capability policy (DV or higher).",
        accepts_arguments=True,
        required_capability=Capability.SERVICE_INSPECT.value,
    ),
    CommandSpec(
        command_id=CommandId.IDENTITY,
        name="identity",
        usage="!identity",
        summary="Show the adapter-bound stable identity and scope.",
    ),
    CommandSpec(
        command_id=CommandId.SHUTDOWN,
        name="shutdown",
        usage="!shutdown",
        summary="Stop the Dee Dee service (Founder only).",
        required_capability=Capability.SERVICE_SHUTDOWN.value,
    ),
    CommandSpec(
        command_id=CommandId.JOKE,
        name="joke",
        usage="!joke",
        summary="Ask Dee Dee for a randomized dry technical joke.",
    ),
    CommandSpec(
        command_id=CommandId.MOOD,
        name="mood",
        usage="!mood",
        summary="Show Dee Dee's current adaptively inferred tone.",
    ),
    CommandSpec(
        command_id=CommandId.MODE,
        name="mode",
        usage="!mode [id] | !mode +v|-v <id>",
        summary="Inspect or manage channel membership modes.",
        accepts_arguments=True,
    ),
    CommandSpec(
        command_id=CommandId.CLEAR,
        name="clear",
        usage="!clear [count]",
        summary="Clear recent messages from the current Discord channel.",
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
