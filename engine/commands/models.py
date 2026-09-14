from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from engine.trust.models import ScopeRef


class CommandId(str, Enum):
    HELP = "help"
    MOTD = "motd"
    VERSION = "version"
    UPTIME = "uptime"
    WHOIS = "whois"
    ROLE = "role"
    FLAG = "flag"
    CAPABILITIES = "capabilities"
    USERS = "users"
    AUDIT = "audit"
    FOUNDER = "founder"
    SCOPE = "scope"
    AUTHZ = "authz"
    POLICY = "policy"
    IDENTITY = "identity"
    SHUTDOWN = "shutdown"
    JOKE = "joke"
    MOOD = "mood"
    EXIT = "exit"


class CommandParseStatus(str, Enum):
    NOT_COMMAND = "not_command"
    VALID = "valid"
    MALFORMED = "malformed"
    UNKNOWN = "unknown"


class CommandAction(str, Enum):
    NONE = "none"
    EXIT_SESSION = "exit_session"
    SHUTDOWN_SERVICE = "shutdown_service"


class CommandStatus(str, Enum):
    OK = "ok"
    MALFORMED = "malformed"
    UNKNOWN = "unknown"
    INVALID_ARGUMENTS = "invalid_arguments"
    FORBIDDEN = "forbidden"


@dataclass(frozen=True)
class ParsedCommand:
    raw: str
    name: str
    argument_text: str


@dataclass(frozen=True)
class CommandParseResult:
    status: CommandParseStatus
    command: ParsedCommand | None = None


@dataclass(frozen=True)
class CommandSpec:
    command_id: CommandId
    name: str
    usage: str
    summary: str
    accepts_arguments: bool = False
    required_capability: str | None = None


@dataclass(frozen=True)
class CommandResult:
    text: str
    status: CommandStatus = CommandStatus.OK
    action: CommandAction = CommandAction.NONE


@dataclass(frozen=True)
class CommandRuntime:
    started_at: float
    clock: Callable[[], float]
    protocol: str
    actor_id: str = "terminal:user"
    trust_service: object | None = None
    authorization_scope: ScopeRef | None = None
    identity_context: object | None = None

    def effective_scope(self):
        return self.authorization_scope or ScopeRef.global_scope()
