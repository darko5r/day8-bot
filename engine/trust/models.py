from dataclasses import dataclass, field
from enum import Enum


class IdentityType(str, Enum):
    HUMAN = "human"
    SERVICE = "service"


class AuthorityRole(str, Enum):
    FOUNDER = "founder"
    SOP = "sop"
    OPERATOR = "op"
    DEVELOPER = "dv"
    MEMBER = "mb"
    GUEST = "gt"


ROLE_CODES = {
    AuthorityRole.FOUNDER: "FOUNDER",
    AuthorityRole.SOP: "SOP",
    AuthorityRole.OPERATOR: "OP",
    AuthorityRole.DEVELOPER: "DV",
    AuthorityRole.MEMBER: "MB",
    AuthorityRole.GUEST: "GT",
}


class ServiceFlag(str, Enum):
    TRUSTED = "T"
    REVIEWER = "R"
    MENTOR = "M"
    CONTRIBUTOR = "C"


class Capability(str, Enum):
    CORE_READ = "core.read"
    PROFILE_READ_SELF = "profile.read.self"
    PROFILE_READ_OTHER = "profile.read.other"

    REVIEW_RUN = "review.run"
    REVIEW_DEEP = "review.deep"
    REVIEW_PUBLISH = "review.publish"

    MENTOR_USE = "mentor.use"
    MENTOR_PROVIDE = "mentor.provide"

    CHANNEL_MODE_SET = "channel.mode.set"
    CHANNEL_OPERATOR_GRANT = "channel.operator.grant"
    CHANNEL_VOICE_GRANT = "channel.voice.grant"

    MODERATION_KICK = "moderation.kick"
    MODERATION_BAN = "moderation.ban"
    MODERATION_UNBAN = "moderation.unban"

    ROLE_INSPECT = "role.inspect"
    ROLE_ASSIGN_MEMBER = "role.assign.member"
    ROLE_ASSIGN_DEVELOPER = "role.assign.developer"
    ROLE_ASSIGN_OPERATOR = "role.assign.operator"
    ROLE_ASSIGN_SOP = "role.assign.sop"

    FLAG_INSPECT = "flag.inspect"
    FLAG_ASSIGN_CONTRIBUTOR = "flag.assign.contributor"
    FLAG_ASSIGN_MENTOR = "flag.assign.mentor"
    FLAG_ASSIGN_REVIEWER = "flag.assign.reviewer"
    FLAG_ASSIGN_TRUSTED = "flag.assign.trusted"

    SERVICE_INSPECT = "service.inspect"
    SERVICE_AUDIT = "service.audit"
    SERVICE_CONFIGURE = "service.configure"
    SERVICE_SHUTDOWN = "service.shutdown"

    FOUNDER_TRANSFER = "founder.transfer"


class ScopeKind(str, Enum):
    SELF = "self"
    CHANNEL = "channel"
    GUILD = "guild"
    GLOBAL = "global"


@dataclass(frozen=True)
class ScopeRef:
    kind: ScopeKind
    guild_id: str | None = None
    channel_id: str | None = None
    subject_id: str | None = None

    def __post_init__(self):
        if self.kind == ScopeKind.GLOBAL:
            if any((self.guild_id, self.channel_id, self.subject_id)):
                raise ValueError("global scope cannot carry identifiers")
            return

        if self.kind == ScopeKind.SELF:
            if not self.subject_id:
                raise ValueError("self scope requires subject_id")
            if self.guild_id or self.channel_id:
                raise ValueError("self scope cannot carry guild/channel identifiers")
            return

        if self.kind == ScopeKind.GUILD:
            if not self.guild_id:
                raise ValueError("guild scope requires guild_id")
            if self.channel_id or self.subject_id:
                raise ValueError("guild scope cannot carry channel/subject identifiers")
            return

        if self.kind == ScopeKind.CHANNEL:
            if not self.guild_id or not self.channel_id:
                raise ValueError("channel scope requires guild_id and channel_id")
            if self.subject_id:
                raise ValueError("channel scope cannot carry subject_id")
            return

        raise ValueError(f"unsupported scope kind: {self.kind}")

    @classmethod
    def global_scope(cls):
        return cls(ScopeKind.GLOBAL)

    @classmethod
    def self_scope(cls, subject_id):
        return cls(ScopeKind.SELF, subject_id=subject_id)

    @classmethod
    def guild_scope(cls, guild_id):
        return cls(ScopeKind.GUILD, guild_id=guild_id)

    @classmethod
    def channel_scope(cls, guild_id, channel_id):
        return cls(
            ScopeKind.CHANNEL,
            guild_id=guild_id,
            channel_id=channel_id,
        )

    def label(self):
        if self.kind == ScopeKind.GLOBAL:
            return "GLOBAL"
        if self.kind == ScopeKind.SELF:
            return f"SELF:{self.subject_id}"
        if self.kind == ScopeKind.GUILD:
            return f"GUILD:{self.guild_id}"
        return f"CHANNEL:{self.guild_id}/{self.channel_id}"


class GrantSourceKind(str, Enum):
    ROLE = "role"
    FLAG = "flag"


@dataclass(frozen=True)
class GrantSource:
    kind: GrantSourceKind
    value: str

    def label(self):
        return f"{self.kind.value}:{self.value}"


class AuthorizationStatus(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


class DenialReason(str, Enum):
    UNKNOWN_IDENTITY = "unknown_identity"
    MISSING_CAPABILITY = "missing_capability"
    OUT_OF_SCOPE = "out_of_scope"
    INSUFFICIENT_AUTHORITY = "insufficient_authority"
    PROTECTED_FOUNDER = "protected_founder"
    SELF_ASSIGNMENT = "self_assignment"
    POLICY_DENIED = "policy_denied"


class TrustOperationStatus(str, Enum):
    APPLIED = "applied"
    NO_CHANGE = "no_change"
    DENIED = "denied"
    INVALID = "invalid"


class AuditAction(str, Enum):
    ROLE_SET = "role.set"
    FLAG_SET = "flag.set"
    FOUNDER_TRANSFER = "founder.transfer"


@dataclass(frozen=True)
class IdentityRecord:
    stable_id: str
    role: AuthorityRole
    identity_type: IdentityType = IdentityType.HUMAN
    flags: frozenset[ServiceFlag] = field(default_factory=frozenset)


@dataclass(frozen=True)
class AuthorizationDecision:
    status: AuthorizationStatus
    capability: Capability
    scope: ScopeRef
    reason: DenialReason | None = None
    source: GrantSource | None = None

    @property
    def allowed(self):
        return self.status == AuthorizationStatus.ALLOW


@dataclass(frozen=True)
class TrustOperationResult:
    status: TrustOperationStatus
    reason: DenialReason | None = None

    @property
    def ok(self):
        return self.status in {
            TrustOperationStatus.APPLIED,
            TrustOperationStatus.NO_CHANGE,
        }


@dataclass(frozen=True)
class AuditEvent:
    sequence: int
    action: AuditAction
    actor_id: str
    target_id: str
    status: TrustOperationStatus
    scope: ScopeRef = field(default_factory=ScopeRef.global_scope)
    reason: DenialReason | None = None
    before_role: AuthorityRole | None = None
    after_role: AuthorityRole | None = None
    before_flags: frozenset[ServiceFlag] = field(default_factory=frozenset)
    after_flags: frozenset[ServiceFlag] = field(default_factory=frozenset)
