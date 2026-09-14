from engine.trust.models import (
    AuthorityRole,
    Capability,
    ScopeKind,
    ServiceFlag,
    MembershipMode,
)


ROLE_RANK = {
    AuthorityRole.GUEST: 0,
    AuthorityRole.MEMBER: 1,
    AuthorityRole.DEVELOPER: 2,
    AuthorityRole.OPERATOR: 3,
    AuthorityRole.SOP: 4,
    AuthorityRole.FOUNDER: 5,
}


COMMON_INSPECTION = frozenset(
    {
        Capability.CORE_READ,
        Capability.PROFILE_READ_SELF,
        Capability.ROLE_INSPECT,
        Capability.FLAG_INSPECT,
    }
)


CAPABILITIES_BY_ROLE = {
    AuthorityRole.GUEST: COMMON_INSPECTION,
    AuthorityRole.MEMBER: COMMON_INSPECTION
    | {
        Capability.REVIEW_RUN,
        Capability.MENTOR_USE,
    },
    AuthorityRole.DEVELOPER: COMMON_INSPECTION
    | {
        Capability.REVIEW_RUN,
        Capability.REVIEW_DEEP,
        Capability.REVIEW_PUBLISH,
        Capability.MENTOR_USE,
        Capability.CHANNEL_CLEAR,
        Capability.SERVICE_INSPECT,
    },
    AuthorityRole.OPERATOR: COMMON_INSPECTION
    | {
        Capability.PROFILE_READ_OTHER,
        Capability.REVIEW_RUN,
        Capability.MENTOR_USE,
        Capability.CHANNEL_MODE_SET,
        Capability.CHANNEL_OPERATOR_GRANT,
        Capability.CHANNEL_VOICE_GRANT,
        Capability.CHANNEL_CLEAR,
        Capability.MODERATION_KICK,
        Capability.MODERATION_BAN,
        Capability.MODERATION_UNBAN,
        Capability.ROLE_ASSIGN_MEMBER,
        Capability.FLAG_ASSIGN_CONTRIBUTOR,
        Capability.FLAG_ASSIGN_MENTOR,
        Capability.SERVICE_INSPECT,
    },
    AuthorityRole.SOP: COMMON_INSPECTION
    | {
        Capability.PROFILE_READ_OTHER,
        Capability.REVIEW_RUN,
        Capability.REVIEW_DEEP,
        Capability.REVIEW_PUBLISH,
        Capability.MENTOR_USE,
        Capability.MENTOR_PROVIDE,
        Capability.CHANNEL_MODE_SET,
        Capability.CHANNEL_OPERATOR_GRANT,
        Capability.CHANNEL_VOICE_GRANT,
        Capability.CHANNEL_CLEAR,
        Capability.MODERATION_KICK,
        Capability.MODERATION_BAN,
        Capability.MODERATION_UNBAN,
        Capability.ROLE_ASSIGN_MEMBER,
        Capability.ROLE_ASSIGN_DEVELOPER,
        Capability.ROLE_ASSIGN_OPERATOR,
        Capability.FLAG_ASSIGN_CONTRIBUTOR,
        Capability.FLAG_ASSIGN_MENTOR,
        Capability.FLAG_ASSIGN_REVIEWER,
        Capability.FLAG_ASSIGN_TRUSTED,
        Capability.SERVICE_INSPECT,
        Capability.SERVICE_AUDIT,
        Capability.SERVICE_CONFIGURE,
    },
    AuthorityRole.FOUNDER: frozenset(Capability),
}


CAPABILITIES_BY_MEMBERSHIP = {
    MembershipMode.VOICE: frozenset(
        {
            Capability.CHANNEL_CLEAR,
        }
    ),
}


CAPABILITIES_BY_FLAG = {
    ServiceFlag.TRUSTED: frozenset(),
    ServiceFlag.REVIEWER: frozenset(
        {
            Capability.REVIEW_DEEP,
            Capability.REVIEW_PUBLISH,
        }
    ),
    ServiceFlag.MENTOR: frozenset(
        {
            Capability.MENTOR_PROVIDE,
        }
    ),
    ServiceFlag.CONTRIBUTOR: frozenset(),
}


ALL_SCOPES = frozenset(ScopeKind)

CAPABILITY_SCOPES = {
    Capability.CORE_READ: ALL_SCOPES,
    Capability.PROFILE_READ_SELF: frozenset({ScopeKind.SELF}),
    Capability.PROFILE_READ_OTHER: frozenset(
        {ScopeKind.GUILD, ScopeKind.GLOBAL}
    ),

    Capability.REVIEW_RUN: ALL_SCOPES,
    Capability.REVIEW_DEEP: ALL_SCOPES,
    Capability.REVIEW_PUBLISH: ALL_SCOPES,

    Capability.MENTOR_USE: ALL_SCOPES,
    Capability.MENTOR_PROVIDE: frozenset(
        {ScopeKind.CHANNEL, ScopeKind.GUILD, ScopeKind.GLOBAL}
    ),

    Capability.CHANNEL_MODE_SET: frozenset({ScopeKind.CHANNEL}),
    Capability.CHANNEL_OPERATOR_GRANT: frozenset({ScopeKind.CHANNEL}),
    Capability.CHANNEL_VOICE_GRANT: frozenset({ScopeKind.CHANNEL}),
    Capability.CHANNEL_CLEAR: frozenset({ScopeKind.CHANNEL}),

    Capability.MODERATION_KICK: frozenset(
        {ScopeKind.CHANNEL, ScopeKind.GUILD}
    ),
    Capability.MODERATION_BAN: frozenset(
        {ScopeKind.CHANNEL, ScopeKind.GUILD}
    ),
    Capability.MODERATION_UNBAN: frozenset(
        {ScopeKind.CHANNEL, ScopeKind.GUILD}
    ),

    Capability.ROLE_INSPECT: frozenset(
        {ScopeKind.SELF, ScopeKind.GUILD, ScopeKind.GLOBAL}
    ),
    Capability.ROLE_ASSIGN_MEMBER: frozenset(
        {ScopeKind.GUILD, ScopeKind.GLOBAL}
    ),
    Capability.ROLE_ASSIGN_DEVELOPER: frozenset(
        {ScopeKind.GUILD, ScopeKind.GLOBAL}
    ),
    Capability.ROLE_ASSIGN_OPERATOR: frozenset(
        {ScopeKind.GUILD, ScopeKind.GLOBAL}
    ),
    Capability.ROLE_ASSIGN_SOP: frozenset({ScopeKind.GLOBAL}),

    Capability.FLAG_INSPECT: frozenset(
        {ScopeKind.SELF, ScopeKind.GUILD, ScopeKind.GLOBAL}
    ),
    Capability.FLAG_ASSIGN_CONTRIBUTOR: frozenset({ScopeKind.GLOBAL}),
    Capability.FLAG_ASSIGN_MENTOR: frozenset({ScopeKind.GLOBAL}),
    Capability.FLAG_ASSIGN_REVIEWER: frozenset({ScopeKind.GLOBAL}),
    Capability.FLAG_ASSIGN_TRUSTED: frozenset({ScopeKind.GLOBAL}),

    Capability.SERVICE_INSPECT: frozenset({ScopeKind.GLOBAL}),
    Capability.SERVICE_AUDIT: frozenset({ScopeKind.GLOBAL}),
    Capability.SERVICE_CONFIGURE: frozenset({ScopeKind.GLOBAL}),
    Capability.SERVICE_SHUTDOWN: frozenset({ScopeKind.GLOBAL}),

    Capability.FOUNDER_TRANSFER: frozenset({ScopeKind.GLOBAL}),
}


ROLE_ASSIGNMENT_CAPABILITY = {
    AuthorityRole.GUEST: Capability.ROLE_ASSIGN_MEMBER,
    AuthorityRole.MEMBER: Capability.ROLE_ASSIGN_MEMBER,
    AuthorityRole.DEVELOPER: Capability.ROLE_ASSIGN_DEVELOPER,
    AuthorityRole.OPERATOR: Capability.ROLE_ASSIGN_OPERATOR,
    AuthorityRole.SOP: Capability.ROLE_ASSIGN_SOP,
}


FLAG_ASSIGNMENT_CAPABILITY = {
    ServiceFlag.TRUSTED: Capability.FLAG_ASSIGN_TRUSTED,
    ServiceFlag.REVIEWER: Capability.FLAG_ASSIGN_REVIEWER,
    ServiceFlag.MENTOR: Capability.FLAG_ASSIGN_MENTOR,
    ServiceFlag.CONTRIBUTOR: Capability.FLAG_ASSIGN_CONTRIBUTOR,
}


def scopes_for(capability):
    return CAPABILITY_SCOPES[capability]


def roles_granting(capability):
    return tuple(
        role
        for role in AuthorityRole
        if capability in CAPABILITIES_BY_ROLE[role]
    )


def flags_granting(capability):
    return tuple(
        flag
        for flag in ServiceFlag
        if capability in CAPABILITIES_BY_FLAG[flag]
    )


def membership_modes_granting(capability):
    return tuple(
        mode
        for mode in MembershipMode
        if capability in CAPABILITIES_BY_MEMBERSHIP[mode]
    )
