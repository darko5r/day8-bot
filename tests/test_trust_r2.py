import unittest

from engine.commands.models import CommandRuntime, CommandStatus
from engine.commands.service import handle_command
from engine.memory import MemoryStore
from engine.trust.models import (
    AuthorityRole,
    Capability,
    DenialReason,
    ScopeKind,
    ScopeRef,
    ServiceFlag,
)
from engine.trust.scope import parse_scope
from engine.trust.service import TrustService


class TrustR2ScopeTests(unittest.TestCase):
    def setUp(self):
        self.trust = TrustService("founder")
        self.trust.set_role("founder", "sop", AuthorityRole.SOP)
        self.trust.set_role("sop", "op", AuthorityRole.OPERATOR)
        self.trust.set_role("sop", "dev", AuthorityRole.DEVELOPER)
        self.trust.set_role("sop", "member", AuthorityRole.MEMBER)

    def test_scope_labels_are_typed_and_deterministic(self):
        self.assertEqual(ScopeRef.global_scope().label(), "GLOBAL")
        self.assertEqual(
            ScopeRef.self_scope("alice").label(),
            "SELF:alice",
        )
        self.assertEqual(
            ScopeRef.guild_scope("g1").label(),
            "GUILD:g1",
        )
        self.assertEqual(
            ScopeRef.channel_scope("g1", "c1").label(),
            "CHANNEL:g1/c1",
        )

    def test_invalid_scope_shapes_fail_closed(self):
        with self.assertRaises(ValueError):
            ScopeRef(ScopeKind.GUILD)
        with self.assertRaises(ValueError):
            ScopeRef(ScopeKind.CHANNEL, guild_id="g1")
        with self.assertRaises(ValueError):
            ScopeRef(ScopeKind.SELF)

    def test_scope_parser_understands_submission_forms(self):
        self.assertEqual(
            parse_scope("global", "alice"),
            ScopeRef.global_scope(),
        )
        self.assertEqual(
            parse_scope("self", "alice"),
            ScopeRef.self_scope("alice"),
        )
        self.assertEqual(
            parse_scope("guild:123", "alice"),
            ScopeRef.guild_scope("123"),
        )
        self.assertEqual(
            parse_scope("channel:123:456", "alice"),
            ScopeRef.channel_scope("123", "456"),
        )
        self.assertIsNone(parse_scope("channel:123", "alice"))

    def test_channel_capability_is_rejected_outside_channel_scope(self):
        allowed = self.trust.authorize(
            "op",
            Capability.CHANNEL_MODE_SET,
            ScopeRef.channel_scope("g1", "c1"),
        )
        denied = self.trust.authorize(
            "op",
            Capability.CHANNEL_MODE_SET,
            ScopeRef.global_scope(),
        )

        self.assertTrue(allowed.allowed)
        self.assertFalse(denied.allowed)
        self.assertEqual(denied.reason, DenialReason.OUT_OF_SCOPE)

    def test_moderation_capability_supports_channel_or_guild_not_global(self):
        self.assertTrue(
            self.trust.authorize(
                "op",
                Capability.MODERATION_BAN,
                ScopeRef.channel_scope("g1", "c1"),
            ).allowed
        )
        self.assertTrue(
            self.trust.authorize(
                "op",
                Capability.MODERATION_BAN,
                ScopeRef.guild_scope("g1"),
            ).allowed
        )
        decision = self.trust.authorize(
            "op",
            Capability.MODERATION_BAN,
            ScopeRef.global_scope(),
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, DenialReason.OUT_OF_SCOPE)

    def test_service_shutdown_is_global_only_and_founder_only(self):
        self.assertTrue(
            self.trust.authorize(
                "founder",
                Capability.SERVICE_SHUTDOWN,
                ScopeRef.global_scope(),
            ).allowed
        )
        wrong_scope = self.trust.authorize(
            "founder",
            Capability.SERVICE_SHUTDOWN,
            ScopeRef.guild_scope("g1"),
        )
        self.assertEqual(wrong_scope.reason, DenialReason.OUT_OF_SCOPE)

        missing_capability = self.trust.authorize(
            "sop",
            Capability.SERVICE_SHUTDOWN,
            ScopeRef.global_scope(),
        )
        self.assertEqual(
            missing_capability.reason,
            DenialReason.MISSING_CAPABILITY,
        )

    def test_profile_read_self_cannot_be_retargeted(self):
        self.assertTrue(
            self.trust.authorize(
                "member",
                Capability.PROFILE_READ_SELF,
                ScopeRef.self_scope("member"),
            ).allowed
        )
        decision = self.trust.authorize(
            "member",
            Capability.PROFILE_READ_SELF,
            ScopeRef.self_scope("other"),
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, DenialReason.OUT_OF_SCOPE)

    def test_authorization_reports_role_grant_source(self):
        decision = self.trust.authorize(
            "dev",
            Capability.REVIEW_DEEP,
            ScopeRef.global_scope(),
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.source.label(), "role:DV")

    def test_authorization_reports_flag_grant_source(self):
        self.trust.set_flag(
            "sop",
            "member",
            ServiceFlag.REVIEWER,
            True,
        )
        decision = self.trust.authorize(
            "member",
            Capability.REVIEW_DEEP,
            ScopeRef.global_scope(),
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.source.label(), "flag:R")


class TrustR2CommandTests(unittest.TestCase):
    def setUp(self):
        self.memory = MemoryStore().get(("guild", "channel", "founder"))
        self.trust = TrustService("founder")
        self.trust.set_role("founder", "sop", AuthorityRole.SOP)
        self.trust.set_role("sop", "op", AuthorityRole.OPERATOR)
        self.trust.set_role("sop", "dev", AuthorityRole.DEVELOPER)
        self.trust.set_role("sop", "member", AuthorityRole.MEMBER)

    def runtime_for(self, actor, scope=None):
        return CommandRuntime(
            started_at=10.0,
            clock=lambda: 20.0,
            protocol="terminal",
            actor_id=actor,
            trust_service=self.trust,
            authorization_scope=scope,
        )

    def command(self, text, actor="founder", scope=None):
        return handle_command(
            text,
            self.memory,
            self.runtime_for(actor, scope),
        )

    def test_help_exposes_r2_diagnostics(self):
        result = self.command("!help")
        for command in ("!scope", "!authz", "!policy"):
            self.assertIn(command, result.text)

    def test_scope_command_reports_runtime_scope(self):
        result = self.command(
            "!scope",
            actor="op",
            scope=ScopeRef.channel_scope("g1", "c1"),
        )
        self.assertEqual(result.status, CommandStatus.OK)
        self.assertIn("CHANNEL:g1/c1", result.text)

    def test_authz_explains_allow_and_out_of_scope(self):
        allowed = self.command(
            "!authz channel.mode.set channel:g1:c1",
            actor="op",
        )
        self.assertEqual(allowed.status, CommandStatus.OK)
        self.assertIn("Decision   : ALLOW", allowed.text)
        self.assertIn("Source     : role:OP", allowed.text)

        denied = self.command(
            "!authz channel.mode.set global",
            actor="op",
        )
        self.assertEqual(denied.status, CommandStatus.FORBIDDEN)
        self.assertIn("Reason     : out_of_scope", denied.text)

    def test_authz_rejects_unknown_capability_and_bad_scope(self):
        unknown = self.command("!authz nope global", actor="op")
        self.assertEqual(unknown.status, CommandStatus.INVALID_ARGUMENTS)

        invalid_scope = self.command(
            "!authz channel.mode.set channel:g1",
            actor="op",
        )
        self.assertEqual(
            invalid_scope.status,
            CommandStatus.INVALID_ARGUMENTS,
        )

    def test_policy_is_developer_or_higher_and_describes_capability(self):
        allowed = self.command("!policy channel.mode.set", actor="dev")
        self.assertEqual(allowed.status, CommandStatus.OK)
        self.assertIn("Scopes     : channel", allowed.text)
        self.assertIn("FOUNDER", allowed.text)
        self.assertIn("SOP", allowed.text)
        self.assertIn("OP", allowed.text)

        denied = self.command("!policy channel.mode.set", actor="member")
        self.assertEqual(denied.status, CommandStatus.FORBIDDEN)

    def test_cross_user_role_and_flag_inspection_is_now_private(self):
        role_denied = self.command("!role op", actor="member")
        flag_denied = self.command("!flag op", actor="member")

        self.assertEqual(role_denied.status, CommandStatus.FORBIDDEN)
        self.assertEqual(flag_denied.status, CommandStatus.FORBIDDEN)

        role_allowed = self.command("!role member", actor="op")
        flag_allowed = self.command("!flag member", actor="op")
        self.assertEqual(role_allowed.status, CommandStatus.OK)
        self.assertEqual(flag_allowed.status, CommandStatus.OK)

    def test_audit_output_includes_typed_scope(self):
        self.command("!role set alice MB")
        result = self.command("!audit 1")
        self.assertEqual(result.status, CommandStatus.OK)
        self.assertIn("scope=GLOBAL", result.text)


if __name__ == "__main__":
    unittest.main()
