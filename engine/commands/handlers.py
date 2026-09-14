from data.commands import (
    BOT_BUILD,
    BOT_NAME,
    COMMAND_LAYER_VERSION,
    ENGINE_VERSION,
    MOTD_LINES,
    PERSONALITY_LAYER_VERSION,
    TRUST_LAYER_VERSION,
)
from engine.commands.models import (
    CommandAction,
    CommandResult,
    CommandStatus,
)
from engine.commands.registry import iter_command_specs
from engine.native.command_token import backend_name as command_name_backend
from engine.personality import joke_response, personality_status_text
from engine.trust.models import (
    Capability,
    ROLE_CODES,
    ScopeKind,
    ScopeRef,
    TrustOperationStatus,
)
from engine.trust.policy import (
    flags_granting,
    roles_granting,
    scopes_for,
)
from engine.trust.scope import parse_capability, parse_scope
from engine.trust.service import parse_flag, parse_role


def _format_uptime(seconds):
    total_seconds = max(0, int(seconds))
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days:02d}d {hours:02d}h {minutes:02d}m {seconds:02d}s"


def _flags_text(record):
    if record is None or not record.flags:
        return "none"
    return ",".join(sorted(flag.value for flag in record.flags))


def _trust_missing():
    return CommandResult(
        "*** TRUST0 unavailable for this runtime.",
        status=CommandStatus.FORBIDDEN,
    )


def _inspection_scope(runtime):
    scope = runtime.effective_scope()
    if scope.kind == ScopeKind.CHANNEL:
        return ScopeRef.guild_scope(scope.guild_id)
    return scope


def _authorization_denied(decision, required):
    reason = decision.reason.value if decision.reason is not None else "policy_denied"
    return CommandResult(
        "*** Access denied.\n"
        f"Required : {required.value}\n"
        f"Scope    : {decision.scope.label()}\n"
        f"Reason   : {reason}",
        status=CommandStatus.FORBIDDEN,
    )


def _operation_result(result, success_text):
    if result.status in {
        TrustOperationStatus.APPLIED,
        TrustOperationStatus.NO_CHANGE,
    }:
        suffix = "no change" if result.status == TrustOperationStatus.NO_CHANGE else "applied"
        return CommandResult(f"{success_text}\nStatus   : {suffix}")

    reason = result.reason.value if result.reason is not None else "policy_denied"
    return CommandResult(
        f"*** TRUST0 denied.\nReason   : {reason}",
        status=CommandStatus.FORBIDDEN,
    )


def _cross_identity_inspection_allowed(runtime, target_id):
    if target_id == runtime.actor_id:
        return None

    trust = runtime.trust_service
    if trust is None:
        return _trust_missing()

    decision = trust.authorize(
        runtime.actor_id,
        Capability.PROFILE_READ_OTHER,
        _inspection_scope(runtime),
    )
    if decision.allowed:
        return None

    return _authorization_denied(
        decision,
        Capability.PROFILE_READ_OTHER,
    )


def handle_help(command, memory, runtime):
    lines = ["*** Dee Dee command registry ***"]
    lines.extend(
        f"{spec.usage:<48} {spec.summary}"
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
                f"CmdName  : {command_name_backend()}",
                f"Trust    : {TRUST_LAYER_VERSION}",
                f"Personality: {PERSONALITY_LAYER_VERSION}",
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
    trust = runtime.trust_service
    tokens = command.argument_text.split()
    if len(tokens) > 1:
        return CommandResult(
            "*** Usage: !whois [id]",
            status=CommandStatus.INVALID_ARGUMENTS,
        )

    requested_id = tokens[0] if tokens else runtime.actor_id
    is_self = requested_id == runtime.actor_id

    if not is_self:
        if trust is None:
            return CommandResult(
                "*** WHOIS R0\n"
                "Cross-user lookup is unavailable in R0.\n"
                "Use !whois with no arguments to inspect your own scoped record.",
                status=CommandStatus.FORBIDDEN,
            )
        inspection_scope = _inspection_scope(runtime)
        decision = trust.authorize(
            runtime.actor_id,
            Capability.PROFILE_READ_OTHER,
            inspection_scope,
        )
        if not decision.allowed:
            return _authorization_denied(
                decision,
                Capability.PROFILE_READ_OTHER,
            )

        record = trust.get(requested_id)
        if record is None:
            return CommandResult(
                f"*** Unknown identity: {requested_id}",
                status=CommandStatus.INVALID_ARGUMENTS,
            )
        return CommandResult(
            "\n".join(
                (
                    f"*** WHOIS {requested_id}",
                    f"Identity : {record.stable_id}",
                    f"Type     : {record.identity_type.value}",
                    f"Role     : {ROLE_CODES[trust.effective_role(requested_id, inspection_scope)]}",
                    f"Flags    : {_flags_text(record)}",
                    f"Scope    : {inspection_scope.label()}",
                    "Memory   : private",
                    "*** End of WHOIS",
                )
            )
        )

    nickname = memory.profile.name or "unknown"
    language = memory.session.language.capitalize()
    activity = memory.task.activity or "none"
    focus = memory.task.focus or "none"
    next_step = memory.task.next_step or "none"

    identity_line = f"Identity : {runtime.actor_id}"
    type_line = "Type     : unavailable"
    role_line = "Role     : unavailable"
    flags_line = "Flags    : unavailable"
    if trust is not None:
        record = trust.get(runtime.actor_id)
        if record is not None:
            type_line = f"Type     : {record.identity_type.value}"
            role = trust.effective_role(
                runtime.actor_id,
                runtime.effective_scope(),
            )
            role_line = f"Role     : {ROLE_CODES[role]}"
            flags_line = f"Flags    : {_flags_text(record)}"

    return CommandResult(
        "\n".join(
            (
                f"*** WHOIS {nickname}",
                f"Nick     : {nickname}",
                identity_line,
                type_line,
                role_line,
                flags_line,
                f"Language : {language}",
                f"Activity : {activity}",
                f"Focus    : {focus}",
                f"Next     : {next_step}",
                "*** End of WHOIS",
            )
        )
    )


def handle_role(command, memory, runtime):
    trust = runtime.trust_service
    if trust is None:
        return _trust_missing()

    tokens = command.argument_text.split()

    if not tokens:
        target_id = runtime.actor_id
    elif len(tokens) == 1:
        target_id = tokens[0]
    elif len(tokens) == 3 and tokens[0].lower() == "set":
        target_id = tokens[1]
        new_role = parse_role(tokens[2])
        if new_role is None:
            return CommandResult(
                "*** Invalid role. Use FOUNDER, SOP, OP, DV, MB, or GT.",
                status=CommandStatus.INVALID_ARGUMENTS,
            )
        scope = runtime.effective_scope()
        result = trust.set_role_for_scope(
            runtime.actor_id,
            target_id,
            new_role,
            scope,
        )
        return _operation_result(
            result,
            "\n".join(
                (
                    "*** ROLE",
                    f"Target   : {target_id}",
                    f"Role     : {ROLE_CODES[new_role]}",
                    f"Scope    : {scope.label()}",
                )
            ),
        )
    else:
        return CommandResult(
            "*** Usage: !role [id] | !role set <id> <role>",
            status=CommandStatus.INVALID_ARGUMENTS,
        )

    privacy = _cross_identity_inspection_allowed(runtime, target_id)
    if privacy is not None:
        return privacy

    record = trust.get(target_id)
    if record is None:
        return CommandResult(
            f"*** Unknown identity: {target_id}",
            status=CommandStatus.INVALID_ARGUMENTS,
        )

    scope = runtime.effective_scope()
    effective_role = trust.effective_role(target_id, scope)
    return CommandResult(
        "\n".join(
            (
                "*** ROLE",
                f"Identity : {record.stable_id}",
                f"Role     : {ROLE_CODES[effective_role]}",
                f"Global   : {ROLE_CODES[record.role]}",
                f"Scope    : {scope.label()}",
            )
        )
    )


def handle_flag(command, memory, runtime):
    trust = runtime.trust_service
    if trust is None:
        return _trust_missing()

    tokens = command.argument_text.split()

    if not tokens:
        target_id = runtime.actor_id
    elif len(tokens) == 1:
        target_id = tokens[0]
    elif len(tokens) == 3 and tokens[0].lower() in {"add", "remove"}:
        enabled = tokens[0].lower() == "add"
        target_id = tokens[1]
        flag = parse_flag(tokens[2])
        if flag is None:
            return CommandResult(
                "*** Invalid flag. Use T, R, M, or C.",
                status=CommandStatus.INVALID_ARGUMENTS,
            )
        result = trust.set_flag(
            runtime.actor_id,
            target_id,
            flag,
            enabled,
        )
        verb = "added" if enabled else "removed"
        return _operation_result(
            result,
            "\n".join(
                (
                    "*** FLAG",
                    f"Target   : {target_id}",
                    f"Flag     : {flag.value}",
                    f"Action   : {verb}",
                )
            ),
        )
    else:
        return CommandResult(
            "*** Usage: !flag [id] | !flag add|remove <id> <T|R|M|C>",
            status=CommandStatus.INVALID_ARGUMENTS,
        )

    privacy = _cross_identity_inspection_allowed(runtime, target_id)
    if privacy is not None:
        return privacy

    record = trust.get(target_id)
    if record is None:
        return CommandResult(
            f"*** Unknown identity: {target_id}",
            status=CommandStatus.INVALID_ARGUMENTS,
        )

    return CommandResult(
        "\n".join(
            (
                "*** FLAGS",
                f"Identity : {record.stable_id}",
                f"Flags    : {_flags_text(record)}",
            )
        )
    )


def handle_capabilities(command, memory, runtime):
    trust = runtime.trust_service
    if trust is None:
        return _trust_missing()

    tokens = command.argument_text.split()
    if len(tokens) > 1:
        return CommandResult(
            "*** Usage: !capabilities [id]",
            status=CommandStatus.INVALID_ARGUMENTS,
        )

    target_id = tokens[0] if tokens else runtime.actor_id
    scope = runtime.effective_scope()
    if target_id != runtime.actor_id:
        decision = trust.authorize(
            runtime.actor_id,
            Capability.PROFILE_READ_OTHER,
            _inspection_scope(runtime),
        )
        if not decision.allowed:
            return _authorization_denied(
                decision,
                Capability.PROFILE_READ_OTHER,
            )

    record = trust.get(target_id)
    if record is None:
        return CommandResult(
            f"*** Unknown identity: {target_id}",
            status=CommandStatus.INVALID_ARGUMENTS,
        )

    capabilities = sorted(
        capability.value
        for capability in trust.effective_capabilities(target_id, scope)
    )
    lines = [
        "*** CAPABILITIES",
        f"Identity : {target_id}",
        f"Role     : {ROLE_CODES[trust.effective_role(target_id, scope)]}",
        f"Flags    : {_flags_text(record)}",
        f"Scope    : {scope.label()}",
    ]
    lines.extend(f"  {capability}" for capability in capabilities)
    lines.append("*** End of CAPABILITIES")
    return CommandResult("\n".join(lines))


def handle_users(command, memory, runtime):
    trust = runtime.trust_service
    if trust is None:
        return _trust_missing()

    inspection_scope = _inspection_scope(runtime)
    decision = trust.authorize(
        runtime.actor_id,
        Capability.PROFILE_READ_OTHER,
        inspection_scope,
    )
    if not decision.allowed:
        return _authorization_denied(
            decision,
            Capability.PROFILE_READ_OTHER,
        )

    lines = [
        "*** TRUST0 USERS",
        f"Scope    : {inspection_scope.label()}",
    ]
    for record, role in trust.records_for_scope(inspection_scope):
        lines.append(
            f"{record.stable_id:<28} "
            f"{ROLE_CODES[role]:<8} "
            f"flags={_flags_text(record):<7} "
            f"type={record.identity_type.value}"
        )
    lines.append("*** End of USERS")
    return CommandResult("\n".join(lines))


def handle_audit(command, memory, runtime):
    trust = runtime.trust_service
    if trust is None:
        return _trust_missing()

    tokens = command.argument_text.split()
    if len(tokens) > 1:
        return CommandResult(
            "*** Usage: !audit [count]",
            status=CommandStatus.INVALID_ARGUMENTS,
        )

    count = 10
    if tokens:
        try:
            count = int(tokens[0])
        except ValueError:
            return CommandResult(
                "*** AUDIT count must be an integer from 1 to 50.",
                status=CommandStatus.INVALID_ARGUMENTS,
            )
        if not 1 <= count <= 50:
            return CommandResult(
                "*** AUDIT count must be an integer from 1 to 50.",
                status=CommandStatus.INVALID_ARGUMENTS,
            )

    events = trust.audit_events(count)
    lines = ["*** TRUST0 AUDIT"]
    if not events:
        lines.append("(no authority changes recorded)")
    for event in events:
        reason = event.reason.value if event.reason is not None else "-"
        lines.append(
            f"#{event.sequence:04d} "
            f"{event.action.value:<18} "
            f"actor={event.actor_id} "
            f"target={event.target_id} "
            f"status={event.status.value} "
            f"scope={event.scope.label()} "
            f"reason={reason}"
        )
    lines.append("*** End of AUDIT")
    return CommandResult("\n".join(lines))


def handle_founder(command, memory, runtime):
    trust = runtime.trust_service
    if trust is None:
        return _trust_missing()

    tokens = command.argument_text.split()
    if not tokens:
        return CommandResult(
            "\n".join(
                (
                    "*** FOUNDER",
                    f"Identity : {trust.founder_id}",
                    "Authority: root",
                )
            )
        )

    if (
        len(tokens) == 3
        and tokens[0].lower() == "transfer"
        and tokens[2].upper() == "CONFIRM"
    ):
        target_id = tokens[1]
        old_founder = trust.founder_id
        result = trust.transfer_founder(
            runtime.actor_id,
            target_id,
        )
        return _operation_result(
            result,
            "\n".join(
                (
                    "*** FOUNDER TRANSFER",
                    f"Previous : {old_founder}",
                    f"Founder  : {target_id}",
                )
            ),
        )

    return CommandResult(
        "*** Usage: !founder | !founder transfer <id> CONFIRM",
        status=CommandStatus.INVALID_ARGUMENTS,
    )


def handle_scope(command, memory, runtime):
    scope = runtime.effective_scope()
    lines = [
        "*** AUTHORIZATION SCOPE",
        f"Protocol : {runtime.protocol}",
        f"Identity : {runtime.actor_id}",
        f"Scope    : {scope.label()}",
    ]
    if scope.kind == ScopeKind.GLOBAL:
        lines.append("Meaning  : service-wide")
    elif scope.kind == ScopeKind.GUILD:
        lines.append("Meaning  : guild/server")
    elif scope.kind == ScopeKind.CHANNEL:
        lines.append("Meaning  : channel")
    else:
        lines.append("Meaning  : current identity")
    return CommandResult("\n".join(lines))


def handle_authz(command, memory, runtime):
    trust = runtime.trust_service
    if trust is None:
        return _trust_missing()

    tokens = command.argument_text.split()
    if not 1 <= len(tokens) <= 2:
        return CommandResult(
            "*** Usage: !authz <capability> [global|self|guild:<id>|channel:<guild>:<channel>]",
            status=CommandStatus.INVALID_ARGUMENTS,
        )

    capability = parse_capability(tokens[0])
    if capability is None:
        return CommandResult(
            f"*** Unknown capability: {tokens[0]}",
            status=CommandStatus.INVALID_ARGUMENTS,
        )

    scope = runtime.effective_scope()
    if len(tokens) == 2:
        scope = parse_scope(tokens[1], runtime.actor_id)
        if scope is None:
            return CommandResult(
                "*** Invalid scope. Use global, self, guild:<id>, or "
                "channel:<guild>:<channel>.",
                status=CommandStatus.INVALID_ARGUMENTS,
            )

    decision = trust.authorize(
        runtime.actor_id,
        capability,
        scope,
    )
    record = trust.get(runtime.actor_id)
    effective_role = trust.effective_role(runtime.actor_id, scope)
    role = ROLE_CODES[effective_role] if record is not None else "unknown"
    source = decision.source.label() if decision.source is not None else "-"
    reason = decision.reason.value if decision.reason is not None else "-"
    return CommandResult(
        "\n".join(
            (
                "*** AUTHZ",
                f"Identity   : {runtime.actor_id}",
                f"Role       : {role}",
                f"Capability : {capability.value}",
                f"Scope      : {scope.label()}",
                f"Decision   : {decision.status.value.upper()}",
                f"Source     : {source}",
                f"Reason     : {reason}",
            )
        ),
        status=(
            CommandStatus.OK
            if decision.allowed
            else CommandStatus.FORBIDDEN
        ),
    )


def handle_policy(command, memory, runtime):
    tokens = command.argument_text.split()
    if len(tokens) != 1:
        return CommandResult(
            "*** Usage: !policy <capability>",
            status=CommandStatus.INVALID_ARGUMENTS,
        )

    capability = parse_capability(tokens[0])
    if capability is None:
        return CommandResult(
            f"*** Unknown capability: {tokens[0]}",
            status=CommandStatus.INVALID_ARGUMENTS,
        )

    scope_names = ", ".join(
        scope.value
        for scope in sorted(
            scopes_for(capability),
            key=lambda item: item.value,
        )
    )
    role_names = ", ".join(
        ROLE_CODES[role]
        for role in sorted(
            roles_granting(capability),
            key=lambda item: item.value,
        )
    ) or "none"
    flag_names = ", ".join(
        flag.value
        for flag in sorted(
            flags_granting(capability),
            key=lambda item: item.value,
        )
    ) or "none"

    return CommandResult(
        "\n".join(
            (
                "*** TRUST0 POLICY",
                f"Capability : {capability.value}",
                f"Scopes     : {scope_names}",
                f"Roles      : {role_names}",
                f"Flags      : {flag_names}",
            )
        )
    )


def handle_identity(command, memory, runtime):
    trust = runtime.trust_service
    scope = runtime.effective_scope()
    record = trust.get(runtime.actor_id) if trust is not None else None
    role = (
        trust.effective_role(runtime.actor_id, scope)
        if trust is not None and record is not None
        else None
    )

    lines = [
        "*** IDENTITY",
        f"Protocol : {runtime.protocol}",
        f"Stable ID: {runtime.actor_id}",
        f"Scope    : {scope.label()}",
        f"Type     : {record.identity_type.value if record is not None else 'unavailable'}",
        f"Role     : {ROLE_CODES[role] if role is not None else 'unavailable'}",
    ]

    context = runtime.identity_context
    if context is not None and runtime.protocol == "discord":
        lines.extend(
            (
                f"User ID  : {context.user_id}",
                f"Guild ID : {context.guild_id or '-'}",
                f"Channel  : {context.channel_id or '-'}",
            )
        )

    lines.append("*** End of IDENTITY")
    return CommandResult("\n".join(lines))


def handle_shutdown(command, memory, runtime):
    return CommandResult(
        "*** Dee Dee service shutdown authorized.",
        action=CommandAction.SHUTDOWN_SERVICE,
    )


def handle_exit(command, memory, runtime):
    return CommandResult(
        "*** Dee Dee session closed.",
        action=CommandAction.EXIT_SESSION,
    )

def handle_joke(command, memory, runtime):
    return CommandResult(joke_response(memory.session.language))


def handle_mood(command, memory, runtime):
    return CommandResult(personality_status_text(memory))
