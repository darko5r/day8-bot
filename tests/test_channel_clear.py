import unittest

from discord_bot import execute_transport_action
from engine.adapters.discord_adapter import DiscordEngineAdapter
from engine.commands.models import CommandAction
from engine.trust.models import (
    AuthorityRole,
    Capability,
    GrantSourceKind,
    MembershipMode,
    ScopeRef,
    TrustOperationStatus,
)
from engine.trust.service import TrustService


FOUNDER_USER = "100000000000000001"
FOUNDER = f"discord:user:{FOUNDER_USER}"
MEMBER_USER = "100000000000000002"
MEMBER = f"discord:user:{MEMBER_USER}"
GUEST_USER = "100000000000000003"
GUEST = f"discord:user:{GUEST_USER}"
DV_USER = "100000000000000004"
DV = f"discord:user:{DV_USER}"
OP_USER = "100000000000000005"
OP = f"discord:user:{OP_USER}"
SOP_USER = "100000000000000006"
SOP = f"discord:user:{SOP_USER}"

GUILD = "200000000000000001"
CHANNEL = "300000000000000001"
OTHER_CHANNEL = "300000000000000002"

SCOPE = ScopeRef.channel_scope(GUILD, CHANNEL)
OTHER_SCOPE = ScopeRef.channel_scope(GUILD, OTHER_CHANNEL)


class ChannelClearTrustTests(unittest.TestCase):
    def make_trust(self):
        trust = TrustService(FOUNDER)
        for identity in (MEMBER, GUEST, DV, OP, SOP):
            trust.ensure_guest(identity)

        trust.set_guild_role(
            FOUNDER,
            MEMBER,
            GUILD,
            AuthorityRole.MEMBER,
        )
        trust.set_guild_role(
            FOUNDER,
            DV,
            GUILD,
            AuthorityRole.DEVELOPER,
        )
        trust.set_guild_role(
            FOUNDER,
            OP,
            GUILD,
            AuthorityRole.OPERATOR,
        )
        trust.set_role(
            FOUNDER,
            SOP,
            AuthorityRole.SOP,
        )
        return trust

    def test_member_without_voice_is_denied_clear(self):
        trust = self.make_trust()
        decision = trust.authorize(
            MEMBER,
            Capability.CHANNEL_CLEAR,
            SCOPE,
        )
        self.assertFalse(decision.allowed)

    def test_member_with_voice_is_allowed_clear(self):
        trust = self.make_trust()
        result = trust.set_channel_mode(
            FOUNDER,
            MEMBER,
            MembershipMode.VOICE,
            True,
            SCOPE,
        )
        self.assertTrue(result.ok)

        decision = trust.authorize(
            MEMBER,
            Capability.CHANNEL_CLEAR,
            SCOPE,
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(
            decision.source.kind,
            GrantSourceKind.MEMBERSHIP,
        )
        self.assertEqual(decision.source.value, "+v")

    def test_voice_is_channel_local(self):
        trust = self.make_trust()
        trust.set_channel_mode(
            FOUNDER,
            MEMBER,
            MembershipMode.VOICE,
            True,
            SCOPE,
        )
        self.assertTrue(
            trust.authorize(
                MEMBER,
                Capability.CHANNEL_CLEAR,
                SCOPE,
            ).allowed
        )
        self.assertFalse(
            trust.authorize(
                MEMBER,
                Capability.CHANNEL_CLEAR,
                OTHER_SCOPE,
            ).allowed
        )

    def test_developer_is_allowed_clear_without_voice(self):
        trust = self.make_trust()
        self.assertTrue(
            trust.authorize(
                DV,
                Capability.CHANNEL_CLEAR,
                SCOPE,
            ).allowed
        )

    def test_operator_is_allowed_clear_without_voice(self):
        trust = self.make_trust()
        self.assertTrue(
            trust.authorize(
                OP,
                Capability.CHANNEL_CLEAR,
                SCOPE,
            ).allowed
        )

    def test_sop_is_allowed_clear_without_voice(self):
        trust = self.make_trust()
        self.assertTrue(
            trust.authorize(
                SOP,
                Capability.CHANNEL_CLEAR,
                SCOPE,
            ).allowed
        )

    def test_founder_is_allowed_clear_without_voice(self):
        trust = self.make_trust()
        self.assertTrue(
            trust.authorize(
                FOUNDER,
                Capability.CHANNEL_CLEAR,
                SCOPE,
            ).allowed
        )

    def test_guest_is_denied_even_if_voiced(self):
        trust = self.make_trust()
        result = trust.set_channel_mode(
            FOUNDER,
            GUEST,
            MembershipMode.VOICE,
            True,
            SCOPE,
        )
        self.assertTrue(result.ok)
        self.assertFalse(
            trust.authorize(
                GUEST,
                Capability.CHANNEL_CLEAR,
                SCOPE,
            ).allowed
        )

    def test_operator_can_grant_and_remove_voice(self):
        trust = self.make_trust()

        added = trust.set_channel_mode(
            OP,
            MEMBER,
            MembershipMode.VOICE,
            True,
            SCOPE,
        )
        self.assertEqual(
            added.status,
            TrustOperationStatus.APPLIED,
        )
        self.assertIn(
            MembershipMode.VOICE,
            trust.channel_modes(MEMBER, SCOPE),
        )

        removed = trust.set_channel_mode(
            OP,
            MEMBER,
            MembershipMode.VOICE,
            False,
            SCOPE,
        )
        self.assertEqual(
            removed.status,
            TrustOperationStatus.APPLIED,
        )
        self.assertNotIn(
            MembershipMode.VOICE,
            trust.channel_modes(MEMBER, SCOPE),
        )

    def test_developer_cannot_grant_voice(self):
        trust = self.make_trust()
        result = trust.set_channel_mode(
            DV,
            MEMBER,
            MembershipMode.VOICE,
            True,
            SCOPE,
        )
        self.assertEqual(
            result.status,
            TrustOperationStatus.DENIED,
        )

    def test_effective_capabilities_include_clear_for_voiced_member(self):
        trust = self.make_trust()
        trust.set_channel_mode(
            FOUNDER,
            MEMBER,
            MembershipMode.VOICE,
            True,
            SCOPE,
        )
        self.assertIn(
            Capability.CHANNEL_CLEAR,
            trust.effective_capabilities(MEMBER, SCOPE),
        )

    def test_membership_source_is_reported(self):
        trust = self.make_trust()
        trust.set_channel_mode(
            FOUNDER,
            MEMBER,
            MembershipMode.VOICE,
            True,
            SCOPE,
        )
        source = trust.capability_source(
            MEMBER,
            Capability.CHANNEL_CLEAR,
            SCOPE,
        )
        self.assertEqual(source.kind, GrantSourceKind.MEMBERSHIP)
        self.assertEqual(source.value, "+v")


class ChannelClearCommandTests(unittest.TestCase):
    def make_adapter(self):
        adapter = DiscordEngineAdapter(FOUNDER_USER)
        adapter.trust_service.ensure_guest(MEMBER)
        adapter.trust_service.set_guild_role(
            FOUNDER,
            MEMBER,
            GUILD,
            AuthorityRole.MEMBER,
        )
        return adapter

    def test_mode_command_accepts_numeric_discord_id(self):
        adapter = self.make_adapter()
        result = adapter.process_message(
            f"!mode +v {MEMBER_USER}",
            user_id=FOUNDER_USER,
            guild_id=GUILD,
            channel_id=CHANNEL,
        )
        text = "\n".join(result.messages)
        self.assertIn("Mode     : +v", text)
        self.assertIn(f"Target   : {MEMBER}", text)
        self.assertIn("Status   : applied", text)

    def test_mode_command_requires_channel_scope(self):
        adapter = self.make_adapter()
        result = adapter.process_message(
            f"!mode +v {MEMBER_USER}",
            user_id=FOUNDER_USER,
        )
        self.assertIn(
            "requires a Discord channel scope",
            "\n".join(result.messages),
        )

    def test_clear_default_count(self):
        adapter = self.make_adapter()
        result = adapter.process_message(
            "!clear",
            user_id=FOUNDER_USER,
            guild_id=GUILD,
            channel_id=CHANNEL,
        )
        self.assertEqual(result.action, CommandAction.CLEAR_CHANNEL)
        self.assertEqual(result.action_value, 20)
        self.assertEqual(result.messages, ())

    def test_clear_custom_count(self):
        adapter = self.make_adapter()
        result = adapter.process_message(
            "!clear 50",
            user_id=FOUNDER_USER,
            guild_id=GUILD,
            channel_id=CHANNEL,
        )
        self.assertEqual(result.action, CommandAction.CLEAR_CHANNEL)
        self.assertEqual(result.action_value, 50)

    def test_clear_invalid_counts(self):
        adapter = self.make_adapter()
        for raw in ("!clear 0", "!clear 101", "!clear nope", "!clear 1 2"):
            with self.subTest(raw=raw):
                result = adapter.process_message(
                    raw,
                    user_id=FOUNDER_USER,
                    guild_id=GUILD,
                    channel_id=CHANNEL,
                )
                self.assertEqual(result.action, CommandAction.NONE)
                self.assertIn(
                    "CLEAR count must be an integer from 1 to 100",
                    "\n".join(result.messages),
                )

    def test_clear_denied_for_unvoiced_member(self):
        adapter = self.make_adapter()
        result = adapter.process_message(
            "!clear",
            user_id=MEMBER_USER,
            guild_id=GUILD,
            channel_id=CHANNEL,
        )
        self.assertEqual(result.action, CommandAction.NONE)
        self.assertIn("Access denied", "\n".join(result.messages))

    def test_clear_preserves_conversation_memory(self):
        adapter = self.make_adapter()

        adapter.process_message(
            "my name is Darko",
            user_id=FOUNDER_USER,
            guild_id=GUILD,
            channel_id=CHANNEL,
        )
        clear = adapter.process_message(
            "!clear",
            user_id=FOUNDER_USER,
            guild_id=GUILD,
            channel_id=CHANNEL,
        )
        self.assertEqual(clear.action, CommandAction.CLEAR_CHANNEL)

        recall = adapter.process_message(
            "what is my name?",
            user_id=FOUNDER_USER,
            guild_id=GUILD,
            channel_id=CHANNEL,
        )
        self.assertIn("Darko", "\n".join(recall.messages))

    def test_policy_reports_voice_membership_grant(self):
        adapter = self.make_adapter()
        result = adapter.process_message(
            "!policy channel.clear",
            user_id=FOUNDER_USER,
            guild_id=GUILD,
            channel_id=CHANNEL,
        )
        text = "\n".join(result.messages)
        self.assertIn("Capability : channel.clear", text)
        self.assertIn("Modes      : +v", text)

    def test_adapter_propagates_clear_action_value(self):
        adapter = self.make_adapter()
        result = adapter.process_message(
            "!clear 37",
            user_id=FOUNDER_USER,
            guild_id=GUILD,
            channel_id=CHANNEL,
        )
        self.assertEqual(result.action, CommandAction.CLEAR_CHANNEL)
        self.assertEqual(result.action_value, 37)


class FakeMessage:
    def __init__(self, pinned=False):
        self.pinned = pinned


class FakeChannel:
    def __init__(self):
        self.limit = None
        self.check = None
        self.sent = []

    async def purge(self, *, limit, check):
        self.limit = limit
        self.check = check
        return []

    async def send(self, text):
        self.sent.append(text)


class DiscordClearTransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_clear_transport_purges_and_preserves_pins(self):
        adapter = DiscordEngineAdapter(FOUNDER_USER)
        result = adapter.process_message(
            "!clear 33",
            user_id=FOUNDER_USER,
            guild_id=GUILD,
            channel_id=CHANNEL,
        )
        channel = FakeChannel()

        claimed = await execute_transport_action(channel, result)

        self.assertTrue(claimed)
        self.assertEqual(channel.limit, 33)
        self.assertTrue(channel.check(FakeMessage(pinned=False)))
        self.assertFalse(channel.check(FakeMessage(pinned=True)))
        self.assertEqual(channel.sent, [])

    async def test_non_clear_transport_action_is_not_claimed(self):
        adapter = DiscordEngineAdapter(FOUNDER_USER)
        result = adapter.process_message(
            "!version",
            user_id=FOUNDER_USER,
            guild_id=GUILD,
            channel_id=CHANNEL,
        )
        channel = FakeChannel()

        claimed = await execute_transport_action(channel, result)

        self.assertFalse(claimed)
        self.assertIsNone(channel.limit)


if __name__ == "__main__":
    unittest.main()
