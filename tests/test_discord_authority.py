import unittest

from engine.commands.models import CommandRuntime, CommandStatus
from engine.commands.service import handle_command
from engine.memory import MemoryStore
from engine.trust.discord import (
    DiscordTrustContext,
    bind_discord_identity,
    discord_stable_id,
)
from engine.trust.models import (
    AuthorityRole,
    Capability,
    DenialReason,
    IdentityType,
    ScopeKind,
    ScopeRef,
)
from engine.trust.service import TrustService


class DiscordIdentityBindingTests(unittest.TestCase):
    def test_stable_identity_is_numeric_and_namespaced(self):
        self.assertEqual(
            discord_stable_id("000123"),
            "discord:user:123",
        )
        with self.assertRaises(ValueError):
            discord_stable_id("Darko")
        with self.assertRaises(ValueError):
            discord_stable_id("0")

    def test_channel_context_maps_to_channel_scope_and_memory_scope(self):
        context = DiscordTrustContext.from_ids(
            user_id="100",
            guild_id="200",
            channel_id="300",
        )
        self.assertEqual(context.stable_id, "discord:user:100")
        self.assertEqual(
            context.authorization_scope,
            ScopeRef.channel_scope("200", "300"),
        )
        self.assertEqual(
            context.memory_scope,
            (
                "discord:guild:200",
                "discord:channel:300",
                "discord:user:100",
            ),
        )

    def test_dm_context_is_self_scoped(self):
        context = DiscordTrustContext.from_ids(user_id="100")
        self.assertEqual(
            context.authorization_scope,
            ScopeRef.self_scope("discord:user:100"),
        )
        self.assertEqual(context.memory_scope[0], "discord:dm")

    def test_channel_without_guild_is_invalid(self):
        with self.assertRaises(ValueError):
            DiscordTrustContext.from_ids(
                user_id="100",
                channel_id="300",
            )

    def test_bot_identity_is_service_type(self):
        context = DiscordTrustContext.from_ids(
            user_id="900",
            guild_id="200",
            channel_id="300",
            is_bot=True,
        )
        self.assertEqual(context.identity_type, IdentityType.SERVICE)

    def test_binding_registers_guest_without_using_display_name(self):
        founder = discord_stable_id("1")
        trust = TrustService(founder)
        context = DiscordTrustContext.from_ids(
            user_id="2",
            guild_id="10",
            channel_id="20",
        )
        record = bind_discord_identity(trust, context)
        self.assertEqual(record.stable_id, "discord:user:2")
        self.assertEqual(record.role, AuthorityRole.GUEST)


class GuildAuthorityBindingTests(unittest.TestCase):
    def setUp(self):
        self.founder = discord_stable_id("1")
        self.alice = discord_stable_id("2")
        self.bob = discord_stable_id("3")
        self.trust = TrustService(self.founder)
        self.trust.ensure_guest(self.alice)
        self.trust.ensure_guest(self.bob)

    def test_guild_role_is_isolated_from_other_guilds_and_global_role(self):
        result = self.trust.set_guild_role(
            self.founder,
            self.alice,
            "100",
            AuthorityRole.OPERATOR,
        )
        self.assertTrue(result.ok)
        self.assertEqual(
            self.trust.effective_role(
                self.alice,
                ScopeRef.guild_scope("100"),
            ),
            AuthorityRole.OPERATOR,
        )
        self.assertEqual(
            self.trust.effective_role(
                self.alice,
                ScopeRef.guild_scope("999"),
            ),
            AuthorityRole.GUEST,
        )
        self.assertEqual(
            self.trust.effective_role(
                self.alice,
                ScopeRef.global_scope(),
            ),
            AuthorityRole.GUEST,
        )

    def test_guild_operator_capability_does_not_escape_guild(self):
        self.trust.set_guild_role(
            self.founder,
            self.alice,
            "100",
            AuthorityRole.OPERATOR,
        )
        allowed = self.trust.authorize(
            self.alice,
            Capability.CHANNEL_MODE_SET,
            ScopeRef.channel_scope("100", "10"),
        )
        denied = self.trust.authorize(
            self.alice,
            Capability.CHANNEL_MODE_SET,
            ScopeRef.channel_scope("999", "10"),
        )
        self.assertTrue(allowed.allowed)
        self.assertEqual(allowed.source.label(), "role:OP")
        self.assertFalse(denied.allowed)
        self.assertEqual(denied.reason, DenialReason.MISSING_CAPABILITY)

    def test_guild_operator_can_manage_member_only_inside_its_guild(self):
        self.trust.set_guild_role(
            self.founder,
            self.alice,
            "100",
            AuthorityRole.OPERATOR,
        )
        allowed = self.trust.set_guild_role(
            self.alice,
            self.bob,
            "100",
            AuthorityRole.MEMBER,
        )
        denied = self.trust.set_guild_role(
            self.alice,
            self.bob,
            "999",
            AuthorityRole.MEMBER,
        )
        self.assertTrue(allowed.ok)
        self.assertFalse(denied.ok)

    def test_founder_and_sop_remain_service_global(self):
        self.trust.set_role(
            self.founder,
            self.alice,
            AuthorityRole.SOP,
        )
        for guild_id in ("100", "999"):
            self.assertEqual(
                self.trust.effective_role(
                    self.alice,
                    ScopeRef.guild_scope(guild_id),
                ),
                AuthorityRole.SOP,
            )

    def test_guild_scope_cannot_assign_sop_or_founder(self):
        for role in (AuthorityRole.SOP, AuthorityRole.FOUNDER):
            with self.subTest(role=role):
                result = self.trust.set_guild_role(
                    self.founder,
                    self.alice,
                    "100",
                    role,
                )
                self.assertFalse(result.ok)
                self.assertEqual(result.reason, DenialReason.POLICY_DENIED)


class DiscordAuthorizationCommandTests(unittest.TestCase):
    def setUp(self):
        self.founder_context = DiscordTrustContext.from_ids(
            user_id="1",
            guild_id="100",
            channel_id="200",
        )
        self.alice_context = DiscordTrustContext.from_ids(
            user_id="2",
            guild_id="100",
            channel_id="200",
        )
        self.bob_context = DiscordTrustContext.from_ids(
            user_id="3",
            guild_id="100",
            channel_id="200",
        )
        self.trust = TrustService(self.founder_context.stable_id)
        bind_discord_identity(self.trust, self.alice_context)
        bind_discord_identity(self.trust, self.bob_context)
        self.memory = MemoryStore().get(self.founder_context.memory_scope)

    def runtime(self, context):
        return CommandRuntime(
            started_at=10.0,
            clock=lambda: 20.0,
            protocol="discord",
            actor_id=context.stable_id,
            trust_service=self.trust,
            authorization_scope=context.authorization_scope,
            identity_context=context,
        )

    def command(self, text, context=None):
        return handle_command(
            text,
            self.memory,
            self.runtime(context or self.founder_context),
        )

    def test_identity_command_exposes_stable_discord_binding(self):
        result = self.command("!identity")
        self.assertEqual(result.status, CommandStatus.OK)
        self.assertIn("Stable ID: discord:user:1", result.text)
        self.assertIn("Guild ID : 100", result.text)
        self.assertIn("Channel  : 200", result.text)
        self.assertNotIn("Darko", result.text)

    def test_role_set_in_discord_channel_is_guild_scoped(self):
        target = self.alice_context.stable_id
        result = self.command(f"!role set {target} OP")
        self.assertEqual(result.status, CommandStatus.OK)
        self.assertIn("Scope    : CHANNEL:100/200", result.text)
        self.assertEqual(
            self.trust.effective_role(
                target,
                ScopeRef.guild_scope("100"),
            ),
            AuthorityRole.OPERATOR,
        )
        self.assertEqual(
            self.trust.get(target).role,
            AuthorityRole.GUEST,
        )

    def test_guild_operator_can_list_users_but_member_cannot(self):
        alice = self.alice_context.stable_id
        bob = self.bob_context.stable_id
        self.trust.set_guild_role(
            self.founder_context.stable_id,
            alice,
            "100",
            AuthorityRole.OPERATOR,
        )
        self.trust.set_guild_role(
            self.founder_context.stable_id,
            bob,
            "100",
            AuthorityRole.MEMBER,
        )

        allowed = self.command("!users", self.alice_context)
        denied = self.command("!users", self.bob_context)
        self.assertEqual(allowed.status, CommandStatus.OK)
        self.assertIn("GUILD:100", allowed.text)
        self.assertEqual(denied.status, CommandStatus.FORBIDDEN)

    def test_cross_user_whois_reports_guild_effective_role_only(self):
        alice = self.alice_context.stable_id
        bob = self.bob_context.stable_id
        self.trust.set_guild_role(
            self.founder_context.stable_id,
            alice,
            "100",
            AuthorityRole.OPERATOR,
        )
        self.trust.set_guild_role(
            self.founder_context.stable_id,
            bob,
            "100",
            AuthorityRole.MEMBER,
        )
        result = self.command(f"!whois {bob}", self.alice_context)
        self.assertEqual(result.status, CommandStatus.OK)
        self.assertIn("Role     : MB", result.text)
        self.assertIn("Scope    : GUILD:100", result.text)
        self.assertIn("Memory   : private", result.text)

    def test_guild_capability_view_uses_effective_role(self):
        alice = self.alice_context.stable_id
        self.trust.set_guild_role(
            self.founder_context.stable_id,
            alice,
            "100",
            AuthorityRole.OPERATOR,
        )
        result = self.command("!capabilities", self.alice_context)
        self.assertEqual(result.status, CommandStatus.OK)
        self.assertIn("Role     : OP", result.text)
        self.assertIn("channel.mode.set", result.text)
        self.assertIn("Scope    : CHANNEL:100/200", result.text)


if __name__ == "__main__":
    unittest.main()
