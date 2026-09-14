import unittest

from engine.commands.models import CommandRuntime
from engine.commands.service import handle_command
from engine.conversation import handle_message
from engine.memory import MemoryStore
from engine.models import Prompt


class CommandConversationIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.store = MemoryStore()
        self.memory = self.store.get(("guild", "channel", "user"))
        self.runtime = CommandRuntime(
            started_at=10.0,
            clock=lambda: 20.0,
            protocol="terminal",
        )

    def test_help_does_not_interrupt_activity_prompt(self):
        self.memory.session.last_prompt = Prompt.ACTIVITY
        self.memory.session.language = "english"

        result = handle_command("!help", self.memory, self.runtime)
        self.assertIsNotNone(result)
        self.assertEqual(self.memory.session.last_prompt, Prompt.ACTIVITY)

        response, should_exit = handle_message(
            "i am building a discord bot",
            self.memory,
        )
        self.assertFalse(should_exit)
        self.assertEqual(
            self.memory.task.activity,
            "i am building a discord bot",
        )
        self.assertEqual(
            self.memory.session.last_prompt,
            Prompt.ACTIVITY_DETAIL,
        )
        self.assertIn("Dee Dee:", response)

    def test_plain_exit_is_no_longer_a_command_or_goodbye(self):
        command_result = handle_command("exit", self.memory, self.runtime)
        self.assertIsNone(command_result)

        _response, should_exit = handle_message("exit", self.memory)
        self.assertFalse(should_exit)

    def test_natural_goodbye_still_works(self):
        _response, should_exit = handle_message("bye", self.memory)
        self.assertTrue(should_exit)


if __name__ == "__main__":
    unittest.main()
