from dataclasses import replace

from engine.trust.models import (
    AuditAction,
    AuditEvent,
    AuthorityRole,
    AuthorizationDecision,
    AuthorizationStatus,
    Capability,
    DenialReason,
    GrantSource,
    GrantSourceKind,
    IdentityRecord,
    IdentityType,
    ROLE_CODES,
    ScopeKind,
    ScopeRef,
    ServiceFlag,
    TrustOperationResult,
    TrustOperationStatus,
)
from engine.trust.policy import (
    CAPABILITIES_BY_FLAG,
    CAPABILITIES_BY_ROLE,
    FLAG_ASSIGNMENT_CAPABILITY,
    ROLE_ASSIGNMENT_CAPABILITY,
    ROLE_RANK,
    scopes_for,
)


ROLE_ALIASES = {
    "founder": AuthorityRole.FOUNDER,
    "sop": AuthorityRole.SOP,
    "superoperator": AuthorityRole.SOP,
    "super_operator": AuthorityRole.SOP,
    "op": AuthorityRole.OPERATOR,
    "operator": AuthorityRole.OPERATOR,
    "dv": AuthorityRole.DEVELOPER,
    "developer": AuthorityRole.DEVELOPER,
    "mb": AuthorityRole.MEMBER,
    "member": AuthorityRole.MEMBER,
    "gt": AuthorityRole.GUEST,
    "guest": AuthorityRole.GUEST,
}


FLAG_ALIASES = {
    "t": ServiceFlag.TRUSTED,
    "trusted": ServiceFlag.TRUSTED,
    "r": ServiceFlag.REVIEWER,
    "reviewer": ServiceFlag.REVIEWER,
    "m": ServiceFlag.MENTOR,
    "mentor": ServiceFlag.MENTOR,
    "c": ServiceFlag.CONTRIBUTOR,
    "contributor": ServiceFlag.CONTRIBUTOR,
}


def parse_role(value):
    return ROLE_ALIASES.get(value.strip().lower())


def parse_flag(value):
    return FLAG_ALIASES.get(value.strip().lower())


class TrustService:
    """In-memory TRUST0 authorization authority.

    Stable IDs are adapter-provided identities. Display names and conversation
    profile names are never used for authorization.

    TRUST0 R2 adds typed authorization scopes and source diagnostics while
    retaining R1's auditable authority mutations and Founder-transfer model.
    """

    def __init__(self, founder_id):
        if not founder_id or not founder_id.strip():
            raise ValueError("founder_id must be a non-empty stable identity")
        founder_id = founder_id.strip()
        self._founder_id = founder_id
        self._records = {
            founder_id: IdentityRecord(
                stable_id=founder_id,
                role=AuthorityRole.FOUNDER,
                identity_type=IdentityType.HUMAN,
            )
        }
        self._guild_roles = {}
        self._audit = []
        self._next_audit_sequence = 1

    @property
    def founder_id(self):
        return self._founder_id

    def get(self, stable_id):
        return self._records.get(stable_id)

    def records(self):
        return tuple(
            self._records[stable_id]
            for stable_id in sorted(self._records)
        )

    def audit_events(self, limit=10):
        if limit <= 0:
            return tuple()
        return tuple(self._audit[-limit:])

    def guild_role(self, stable_id, guild_id):
        return self._guild_roles.get((guild_id, stable_id))

    def effective_role(self, stable_id, scope=None):
        record = self.get(stable_id)
        if record is None:
            return None

        if record.role in {AuthorityRole.FOUNDER, AuthorityRole.SOP}:
            return record.role

        if scope is not None and scope.kind in {
            ScopeKind.GUILD,
            ScopeKind.CHANNEL,
        }:
            guild_role = self.guild_role(stable_id, scope.guild_id)
            if guild_role is not None:
                return guild_role

        return record.role

    def records_for_scope(self, scope=None):
        return tuple(
            (record, self.effective_role(record.stable_id, scope))
            for record in self.records()
        )

    def ensure_guest(self, stable_id, identity_type=IdentityType.HUMAN):
        if not stable_id or not stable_id.strip():
            raise ValueError("stable_id must be a non-empty identity")
        stable_id = stable_id.strip()
        record = self._records.get(stable_id)
        if record is None:
            record = IdentityRecord(
                stable_id=stable_id,
                role=AuthorityRole.GUEST,
                identity_type=identity_type,
            )
            self._records[stable_id] = record
        return record

    def effective_capabilities(self, stable_id, scope=None):
        record = self.get(stable_id)
        if record is None:
            return frozenset()

        role = self.effective_role(stable_id, scope)
        capabilities = set(CAPABILITIES_BY_ROLE[role])
        for flag in record.flags:
            capabilities.update(CAPABILITIES_BY_FLAG[flag])
        return frozenset(capabilities)

    def capability_source(self, stable_id, capability, scope=None):
        record = self.get(stable_id)
        if record is None:
            return None

        role = self.effective_role(stable_id, scope)
        if capability in CAPABILITIES_BY_ROLE[role]:
            return GrantSource(
                GrantSourceKind.ROLE,
                ROLE_CODES[role],
            )

        for flag in sorted(record.flags, key=lambda item: item.value):
            if capability in CAPABILITIES_BY_FLAG[flag]:
                return GrantSource(
                    GrantSourceKind.FLAG,
                    flag.value,
                )

        return None

    def authorize(self, stable_id, capability, scope=None):
        if scope is None:
            scope = ScopeRef.global_scope()

        record = self.get(stable_id)
        if record is None:
            return AuthorizationDecision(
                status=AuthorizationStatus.DENY,
                capability=capability,
                scope=scope,
                reason=DenialReason.UNKNOWN_IDENTITY,
            )

        source = self.capability_source(stable_id, capability, scope)
        if source is None:
            return AuthorizationDecision(
                status=AuthorizationStatus.DENY,
                capability=capability,
                scope=scope,
                reason=DenialReason.MISSING_CAPABILITY,
            )

        if scope.kind not in scopes_for(capability):
            return AuthorizationDecision(
                status=AuthorizationStatus.DENY,
                capability=capability,
                scope=scope,
                reason=DenialReason.OUT_OF_SCOPE,
                source=source,
            )

        if (
            scope.kind == ScopeKind.SELF
            and scope.subject_id != stable_id
            and capability == Capability.PROFILE_READ_SELF
        ):
            return AuthorizationDecision(
                status=AuthorizationStatus.DENY,
                capability=capability,
                scope=scope,
                reason=DenialReason.OUT_OF_SCOPE,
                source=source,
            )

        return AuthorizationDecision(
            status=AuthorizationStatus.ALLOW,
            capability=capability,
            scope=scope,
            source=source,
        )

    def _append_audit(
        self,
        action,
        actor_id,
        target_id,
        result,
        before=None,
        after=None,
        scope=None,
    ):
        event = AuditEvent(
            sequence=self._next_audit_sequence,
            action=action,
            actor_id=actor_id,
            target_id=target_id,
            status=result.status,
            scope=scope or ScopeRef.global_scope(),
            reason=result.reason,
            before_role=before.role if before is not None else None,
            after_role=after.role if after is not None else None,
            before_flags=before.flags if before is not None else frozenset(),
            after_flags=after.flags if after is not None else frozenset(),
        )
        self._next_audit_sequence += 1
        self._audit.append(event)
        return result

    def _authority_check(self, actor, target, new_role=None):
        if target.role == AuthorityRole.FOUNDER:
            return DenialReason.PROTECTED_FOUNDER

        if actor.role == AuthorityRole.FOUNDER:
            if new_role == AuthorityRole.FOUNDER:
                return DenialReason.POLICY_DENIED
            return None

        if actor.stable_id == target.stable_id:
            return DenialReason.SELF_ASSIGNMENT

        actor_rank = ROLE_RANK[actor.role]
        if ROLE_RANK[target.role] >= actor_rank:
            return DenialReason.INSUFFICIENT_AUTHORITY

        if new_role is not None and ROLE_RANK[new_role] >= actor_rank:
            return DenialReason.INSUFFICIENT_AUTHORITY

        return None

    def set_role(self, actor_id, target_id, new_role):
        before = self.get(target_id)
        actor = self.get(actor_id)
        global_scope = ScopeRef.global_scope()

        if actor is None:
            result = TrustOperationResult(
                TrustOperationStatus.DENIED,
                DenialReason.UNKNOWN_IDENTITY,
            )
            return self._append_audit(
                AuditAction.ROLE_SET,
                actor_id,
                target_id,
                result,
                before=before,
                after=before,
                scope=global_scope,
            )

        if new_role == AuthorityRole.FOUNDER:
            result = TrustOperationResult(
                TrustOperationStatus.DENIED,
                DenialReason.POLICY_DENIED,
            )
            return self._append_audit(
                AuditAction.ROLE_SET,
                actor_id,
                target_id,
                result,
                before=before,
                after=before,
                scope=global_scope,
            )

        required = ROLE_ASSIGNMENT_CAPABILITY[new_role]
        decision = self.authorize(actor_id, required, global_scope)
        if not decision.allowed:
            result = TrustOperationResult(
                TrustOperationStatus.DENIED,
                decision.reason,
            )
            return self._append_audit(
                AuditAction.ROLE_SET,
                actor_id,
                target_id,
                result,
                before=before,
                after=before,
                scope=global_scope,
            )

        target = before
        if target is None:
            target = IdentityRecord(
                stable_id=target_id,
                role=AuthorityRole.GUEST,
            )

        denial = self._authority_check(actor, target, new_role)
        if denial is not None:
            result = TrustOperationResult(
                TrustOperationStatus.DENIED,
                denial,
            )
            return self._append_audit(
                AuditAction.ROLE_SET,
                actor_id,
                target_id,
                result,
                before=before,
                after=before,
                scope=global_scope,
            )

        if target.role == new_role:
            self._records[target_id] = target
            result = TrustOperationResult(TrustOperationStatus.NO_CHANGE)
            return self._append_audit(
                AuditAction.ROLE_SET,
                actor_id,
                target_id,
                result,
                before=before or target,
                after=target,
                scope=global_scope,
            )

        after = replace(target, role=new_role)
        self._records[target_id] = after
        result = TrustOperationResult(TrustOperationStatus.APPLIED)
        return self._append_audit(
            AuditAction.ROLE_SET,
            actor_id,
            target_id,
            result,
            before=before,
            after=after,
            scope=global_scope,
        )

    def _scope_authority_check(
        self,
        actor_id,
        actor_role,
        target_id,
        target_role,
        new_role=None,
    ):
        if target_role == AuthorityRole.FOUNDER:
            return DenialReason.PROTECTED_FOUNDER

        if actor_role == AuthorityRole.FOUNDER:
            if new_role == AuthorityRole.FOUNDER:
                return DenialReason.POLICY_DENIED
            return None

        if actor_id == target_id:
            return DenialReason.SELF_ASSIGNMENT

        actor_rank = ROLE_RANK[actor_role]
        if ROLE_RANK[target_role] >= actor_rank:
            return DenialReason.INSUFFICIENT_AUTHORITY

        if new_role is not None and ROLE_RANK[new_role] >= actor_rank:
            return DenialReason.INSUFFICIENT_AUTHORITY

        return None

    def set_guild_role(self, actor_id, target_id, guild_id, new_role):
        guild_scope = ScopeRef.guild_scope(guild_id)
        before = self.get(target_id)
        actor = self.get(actor_id)

        if new_role in {AuthorityRole.FOUNDER, AuthorityRole.SOP}:
            result = TrustOperationResult(
                TrustOperationStatus.DENIED,
                DenialReason.POLICY_DENIED,
            )
            return self._append_audit(
                AuditAction.ROLE_SET,
                actor_id,
                target_id,
                result,
                before=before,
                after=before,
                scope=guild_scope,
            )

        if actor is None:
            result = TrustOperationResult(
                TrustOperationStatus.DENIED,
                DenialReason.UNKNOWN_IDENTITY,
            )
            return self._append_audit(
                AuditAction.ROLE_SET,
                actor_id,
                target_id,
                result,
                before=before,
                after=before,
                scope=guild_scope,
            )

        if before is None:
            before = self.ensure_guest(target_id)

        required = ROLE_ASSIGNMENT_CAPABILITY[new_role]
        decision = self.authorize(actor_id, required, guild_scope)
        if not decision.allowed:
            result = TrustOperationResult(
                TrustOperationStatus.DENIED,
                decision.reason,
            )
            return self._append_audit(
                AuditAction.ROLE_SET,
                actor_id,
                target_id,
                result,
                before=before,
                after=before,
                scope=guild_scope,
            )

        actor_role = self.effective_role(actor_id, guild_scope)
        target_role = self.effective_role(target_id, guild_scope)
        denial = self._scope_authority_check(
            actor_id,
            actor_role,
            target_id,
            target_role,
            new_role,
        )
        if denial is not None:
            result = TrustOperationResult(
                TrustOperationStatus.DENIED,
                denial,
            )
            return self._append_audit(
                AuditAction.ROLE_SET,
                actor_id,
                target_id,
                result,
                before=before,
                after=before,
                scope=guild_scope,
            )

        existing = self.guild_role(target_id, guild_id)
        if existing == new_role:
            result = TrustOperationResult(TrustOperationStatus.NO_CHANGE)
        else:
            self._guild_roles[(guild_id, target_id)] = new_role
            result = TrustOperationResult(TrustOperationStatus.APPLIED)

        return self._append_audit(
            AuditAction.ROLE_SET,
            actor_id,
            target_id,
            result,
            before=before,
            after=before,
            scope=guild_scope,
        )

    def set_role_for_scope(self, actor_id, target_id, new_role, scope):
        if scope.kind == ScopeKind.GLOBAL:
            return self.set_role(actor_id, target_id, new_role)
        if scope.kind in {ScopeKind.GUILD, ScopeKind.CHANNEL}:
            return self.set_guild_role(
                actor_id,
                target_id,
                scope.guild_id,
                new_role,
            )
        result = TrustOperationResult(
            TrustOperationStatus.DENIED,
            DenialReason.OUT_OF_SCOPE,
        )
        return self._append_audit(
            AuditAction.ROLE_SET,
            actor_id,
            target_id,
            result,
            before=self.get(target_id),
            after=self.get(target_id),
            scope=scope,
        )

    def set_flag(self, actor_id, target_id, flag, enabled):
        actor = self.get(actor_id)
        target = self.get(target_id)
        before = target
        global_scope = ScopeRef.global_scope()

        if actor is None or target is None:
            result = TrustOperationResult(
                TrustOperationStatus.DENIED,
                DenialReason.UNKNOWN_IDENTITY,
            )
            return self._append_audit(
                AuditAction.FLAG_SET,
                actor_id,
                target_id,
                result,
                before=before,
                after=before,
                scope=global_scope,
            )

        if actor.stable_id == target.stable_id:
            result = TrustOperationResult(
                TrustOperationStatus.DENIED,
                DenialReason.SELF_ASSIGNMENT,
            )
            return self._append_audit(
                AuditAction.FLAG_SET,
                actor_id,
                target_id,
                result,
                before=before,
                after=before,
                scope=global_scope,
            )

        denial = self._authority_check(actor, target)
        if denial is not None:
            result = TrustOperationResult(
                TrustOperationStatus.DENIED,
                denial,
            )
            return self._append_audit(
                AuditAction.FLAG_SET,
                actor_id,
                target_id,
                result,
                before=before,
                after=before,
                scope=global_scope,
            )

        required = FLAG_ASSIGNMENT_CAPABILITY[flag]
        decision = self.authorize(actor_id, required, global_scope)
        if not decision.allowed:
            result = TrustOperationResult(
                TrustOperationStatus.DENIED,
                decision.reason,
            )
            return self._append_audit(
                AuditAction.FLAG_SET,
                actor_id,
                target_id,
                result,
                before=before,
                after=before,
                scope=global_scope,
            )

        flags = set(target.flags)
        changed = False
        if enabled and flag not in flags:
            flags.add(flag)
            changed = True
        elif not enabled and flag in flags:
            flags.remove(flag)
            changed = True

        if not changed:
            result = TrustOperationResult(TrustOperationStatus.NO_CHANGE)
            return self._append_audit(
                AuditAction.FLAG_SET,
                actor_id,
                target_id,
                result,
                before=before,
                after=before,
                scope=global_scope,
            )

        after = replace(target, flags=frozenset(flags))
        self._records[target_id] = after
        result = TrustOperationResult(TrustOperationStatus.APPLIED)
        return self._append_audit(
            AuditAction.FLAG_SET,
            actor_id,
            target_id,
            result,
            before=before,
            after=after,
            scope=global_scope,
        )

    def transfer_founder(self, actor_id, target_id):
        before_target = self.get(target_id)
        actor = self.get(actor_id)
        current_founder = self.get(self._founder_id)
        global_scope = ScopeRef.global_scope()

        if actor is None or before_target is None or current_founder is None:
            result = TrustOperationResult(
                TrustOperationStatus.DENIED,
                DenialReason.UNKNOWN_IDENTITY,
            )
            return self._append_audit(
                AuditAction.FOUNDER_TRANSFER,
                actor_id,
                target_id,
                result,
                before=before_target,
                after=before_target,
                scope=global_scope,
            )

        decision = self.authorize(
            actor_id,
            Capability.FOUNDER_TRANSFER,
            global_scope,
        )
        if not decision.allowed or actor_id != self._founder_id:
            result = TrustOperationResult(
                TrustOperationStatus.DENIED,
                decision.reason or DenialReason.POLICY_DENIED,
            )
            return self._append_audit(
                AuditAction.FOUNDER_TRANSFER,
                actor_id,
                target_id,
                result,
                before=before_target,
                after=before_target,
                scope=global_scope,
            )

        if target_id == self._founder_id:
            result = TrustOperationResult(TrustOperationStatus.NO_CHANGE)
            return self._append_audit(
                AuditAction.FOUNDER_TRANSFER,
                actor_id,
                target_id,
                result,
                before=before_target,
                after=before_target,
                scope=global_scope,
            )

        new_founder = replace(
            before_target,
            role=AuthorityRole.FOUNDER,
        )
        former_founder = replace(
            current_founder,
            role=AuthorityRole.SOP,
        )

        self._records[target_id] = new_founder
        self._records[self._founder_id] = former_founder
        old_founder_id = self._founder_id
        self._founder_id = target_id

        result = TrustOperationResult(TrustOperationStatus.APPLIED)
        return self._append_audit(
            AuditAction.FOUNDER_TRANSFER,
            actor_id,
            target_id,
            result,
            before=before_target,
            after=new_founder,
            scope=global_scope,
        )
