import unittest

import discord

from discord_bot import make_intents, required_environment
from engine.adapters.discord_adapter import (
    DiscordEngineAdapter,
    split_discord_text,
)
from engine.commands.models import CommandAction


FOUNDER = "100000000000000001"
ALICE = "100000000000000002"
BOB = "100000000000000003"
GUILD_A = "200000000000000001"
GUILD_B = "200000000000000002"
CHANNEL_A = "300000000000000001"
CHANNEL_B = "300000000000000002"


class DiscordAdapterTests(unittest.TestCase):
    def make_adapter(self, **kwargs):
        return DiscordEngineAdapter(FOUNDER, **kwargs)

    def test_founder_is_bootstrapped_from_stable_discord_id(self):
        adapter = self.make_adapter()
        self.assertEqual(
            adapter.founder_id,
            f"discord:user:{FOUNDER}",
        )

    def test_invalid_founder_id_is_rejected(self):
        with self.assertRaises(ValueError):
            DiscordEngineAdapter("not-a-snowflake")

    def test_bot_messages_are_ignored_without_registration(self):
        adapter = self.make_adapter()
        result = adapter.process_message(
            "!help",
            user_id=ALICE,
            guild_id=GUILD_A,
            channel_id=CHANNEL_A,
            is_bot=True,
        )
        self.assertTrue(result.ignored)
        self.assertEqual(result.messages, ())
        self.assertIsNone(
            adapter.trust_service.get(f"discord:user:{ALICE}")
        )

    def test_identity_command_uses_discord_context(self):
        adapter = self.make_adapter()
        result = adapter.process_message(
            "!identity",
            user_id=ALICE,
            guild_id=GUILD_A,
            channel_id=CHANNEL_A,
        )
        text = "\n".join(result.messages)
        self.assertIn("Protocol : discord", text)
        self.assertIn(f"Stable ID: discord:user:{ALICE}", text)
        self.assertIn(f"Guild ID : {GUILD_A}", text)
        self.assertIn(f"Channel  : {CHANNEL_A}", text)

    def test_dm_identity_is_self_scoped(self):
        adapter = self.make_adapter()
        result = adapter.process_message(
            "!scope",
            user_id=ALICE,
        )
        text = "\n".join(result.messages)
        self.assertIn("Protocol : discord", text)
        self.assertIn(
            f"Scope    : SELF:discord:user:{ALICE}",
            text,
        )

    def test_guest_cannot_shutdown_service(self):
        adapter = self.make_adapter()
        result = adapter.process_message(
            "!shutdown",
            user_id=ALICE,
            guild_id=GUILD_A,
            channel_id=CHANNEL_A,
        )
        self.assertEqual(result.action, CommandAction.NONE)
        self.assertIn("Access denied", "\n".join(result.messages))

    def test_founder_shutdown_returns_service_action(self):
        adapter = self.make_adapter()
        result = adapter.process_message(
            "!shutdown",
            user_id=FOUNDER,
            guild_id=GUILD_A,
            channel_id=CHANNEL_A,
        )
        self.assertEqual(
            result.action,
            CommandAction.SHUTDOWN_SERVICE,
        )
        self.assertIn(
            "shutdown authorized",
            "\n".join(result.messages).lower(),
        )

    def test_exit_resets_only_current_scoped_session(self):
        adapter = self.make_adapter()

        adapter.process_message(
            "my name is Darko",
            user_id=ALICE,
            guild_id=GUILD_A,
            channel_id=CHANNEL_A,
        )
        adapter.process_message(
            "my name is Bob",
            user_id=BOB,
            guild_id=GUILD_A,
            channel_id=CHANNEL_A,
        )

        exit_result = adapter.process_message(
            "!exit",
            user_id=ALICE,
            guild_id=GUILD_A,
            channel_id=CHANNEL_A,
        )
        self.assertEqual(
            exit_result.action,
            CommandAction.EXIT_SESSION,
        )

        alice_recall = adapter.process_message(
            "what is my name?",
            user_id=ALICE,
            guild_id=GUILD_A,
            channel_id=CHANNEL_A,
        )
        bob_recall = adapter.process_message(
            "what is my name?",
            user_id=BOB,
            guild_id=GUILD_A,
            channel_id=CHANNEL_A,
        )
        self.assertIn(
            "ain't told me your name",
            "\n".join(alice_recall.messages),
        )
        self.assertIn(
            "Bob",
            "\n".join(bob_recall.messages),
        )

    def test_natural_goodbye_resets_session(self):
        adapter = self.make_adapter()

        adapter.process_message(
            "my name is Darko",
            user_id=ALICE,
            guild_id=GUILD_A,
            channel_id=CHANNEL_A,
        )
        goodbye = adapter.process_message(
            "bye",
            user_id=ALICE,
            guild_id=GUILD_A,
            channel_id=CHANNEL_A,
        )
        self.assertEqual(
            goodbye.action,
            CommandAction.EXIT_SESSION,
        )

        recall = adapter.process_message(
            "what is my name?",
            user_id=ALICE,
            guild_id=GUILD_A,
            channel_id=CHANNEL_A,
        )
        self.assertIn(
            "ain't told me your name",
            "\n".join(recall.messages),
        )

    def test_memory_isolated_across_channels(self):
        adapter = self.make_adapter()

        adapter.process_message(
            "my name is Darko",
            user_id=ALICE,
            guild_id=GUILD_A,
            channel_id=CHANNEL_A,
        )
        result = adapter.process_message(
            "what is my name?",
            user_id=ALICE,
            guild_id=GUILD_A,
            channel_id=CHANNEL_B,
        )
        self.assertIn(
            "ain't told me your name",
            "\n".join(result.messages),
        )

    def test_memory_isolated_across_guilds(self):
        adapter = self.make_adapter()

        adapter.process_message(
            "my name is Darko",
            user_id=ALICE,
            guild_id=GUILD_A,
            channel_id=CHANNEL_A,
        )
        result = adapter.process_message(
            "what is my name?",
            user_id=ALICE,
            guild_id=GUILD_B,
            channel_id=CHANNEL_A,
        )
        self.assertIn(
            "ain't told me your name",
            "\n".join(result.messages),
        )

    def test_help_is_chunked_below_configured_limit(self):
        adapter = self.make_adapter(message_limit=400)
        result = adapter.process_message(
            "!help",
            user_id=ALICE,
            guild_id=GUILD_A,
            channel_id=CHANNEL_A,
        )
        self.assertGreater(len(result.messages), 1)
        self.assertTrue(
            all(len(chunk) <= 400 for chunk in result.messages)
        )

    def test_split_discord_text_handles_long_unbroken_line(self):
        chunks = split_discord_text("x" * 25, limit=10)
        self.assertEqual(
            tuple(len(chunk) for chunk in chunks),
            (10, 10, 5),
        )

    def test_runtime_dependency_and_intents_are_qualified(self):
        self.assertEqual(discord.__version__, "2.7.1")
        intents = make_intents()
        self.assertTrue(intents.message_content)
        self.assertEqual(
            required_environment(
                "DEEDEE_TEST_VALUE",
                {"DEEDEE_TEST_VALUE": "  present  "},
            ),
            "present",
        )
        with self.assertRaises(RuntimeError):
            required_environment("DEEDEE_TEST_VALUE", {})


if __name__ == "__main__":
    unittest.main()
