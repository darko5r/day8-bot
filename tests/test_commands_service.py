import unittest

from engine.commands.models import (
    CommandAction,
    CommandRuntime,
    CommandStatus,
)
from engine.commands.service import handle_command
from engine.memory import MemoryStore
from engine.models import Prompt


class CommandServiceTests(unittest.TestCase):
    def setUp(self):
        self.store = MemoryStore()
        self.memory = self.store.get(("guild", "channel", "user"))
        self.now = 100.0
        self.runtime = CommandRuntime(
            started_at=100.0,
            clock=lambda: self.now,
            protocol="terminal",
        )

    def command(self, text):
        return handle_command(text, self.memory, self.runtime)

    def test_help_is_registry_driven_and_case_insensitive(self):
        lower = self.command("!help")
        mixed = self.command("!HeLp")
        self.assertEqual(lower.text, mixed.text)
        for command in (
            "!help", "!motd", "!version", "!uptime", "!whois", "!exit"
        ):
            self.assertIn(command, lower.text)

    def test_motd_contains_operational_guidance(self):
        result = self.command("!motd")
        self.assertIn("Message of the Day", result.text)
        self.assertIn("Type !help", result.text)

    def test_version_reports_command_and_engine_layers(self):
        result = self.command("!version")
        self.assertIn("Conversation Engine R0", result.text)
        self.assertIn("Retro Command Layer R0", result.text)
        self.assertIn("terminal", result.text)

    def test_uptime_uses_injected_clock(self):
        self.now = 100.0 + 90061
        result = self.command("!uptime")
        self.assertIn("01d 01h 01m 01s", result.text)

    def test_whois_reads_only_current_scope(self):
        self.memory.profile.name = "Darko"
        self.memory.session.language = "english"
        self.memory.task.activity = "building a discord bot"
        self.memory.task.focus = "command routing"
        self.memory.task.next_step = "add tests"

        result = self.command("!whois")
        self.assertIn("WHOIS Darko", result.text)
        self.assertIn("Activity : building a discord bot", result.text)
        self.assertIn("Focus    : command routing", result.text)
        self.assertIn("Next     : add tests", result.text)

        other = self.store.get(("guild", "channel", "other"))
        other.profile.name = "Alice"
        other_result = handle_command("!whois", other, self.runtime)
        self.assertIn("WHOIS Alice", other_result.text)
        self.assertNotIn("Darko", other_result.text)

    def test_cross_user_whois_is_refused_in_r0(self):
        self.memory.profile.name = "Darko"
        result = self.command("!whois Alice")
        self.assertIn("Cross-user lookup is unavailable in R0", result.text)
        self.assertNotIn("Nick     : Darko", result.text)

    def test_unknown_command_can_suggest_but_does_not_execute(self):
        result = self.command("!hep")
        self.assertIn("Unknown command: !hep", result.text)
        self.assertIn("Did you mean !help?", result.text)
        self.assertNotIn("command registry", result.text)

    def test_unexpected_arguments_are_rejected(self):
        result = self.command("!version extra")
        self.assertIn("does not accept arguments", result.text)
        self.assertIn("Usage: !version", result.text)

    def test_exit_returns_action_instead_of_terminating_here(self):
        result = self.command("!exit")
        self.assertEqual(result.action, CommandAction.EXIT_SESSION)

    def test_command_results_have_typed_statuses(self):
        self.assertEqual(
            self.command("!help").status,
            CommandStatus.OK,
        )
        self.assertEqual(
            self.command("! help").status,
            CommandStatus.MALFORMED,
        )
        self.assertEqual(
            self.command("!hep").status,
            CommandStatus.UNKNOWN,
        )
        self.assertEqual(
            self.command("!version extra").status,
            CommandStatus.INVALID_ARGUMENTS,
        )
        self.assertEqual(
            self.command("!whois Alice").status,
            CommandStatus.FORBIDDEN,
        )

    def test_read_only_command_preserves_conversation_context(self):
        self.memory.session.last_prompt = Prompt.ACTIVITY
        self.memory.session.language = "english"
        before = (
            self.memory.session.last_prompt,
            self.memory.session.language,
            self.memory.session.last_intent,
            self.memory.task.activity,
            self.memory.task.focus,
            self.memory.task.next_step,
            self.memory.profile.name,
        )

        self.command("!help")

        after = (
            self.memory.session.last_prompt,
            self.memory.session.language,
            self.memory.session.last_intent,
            self.memory.task.activity,
            self.memory.task.focus,
            self.memory.task.next_step,
            self.memory.profile.name,
        )
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
