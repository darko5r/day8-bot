import random
import unittest

from data import argentine as ar
from data import english as en
from engine.commands.models import CommandRuntime
from engine.commands.service import handle_command
from engine.conversation import handle_message
from engine.memory import MemoryStore
from engine.models import Intent, Prompt


class FaqAndFunTests(unittest.TestCase):
    def setUp(self):
        random.seed(0)
        self.store = MemoryStore()
        self.memory = self.store.get(("guild", "channel", "user"))
        self.runtime = CommandRuntime(
            started_at=10.0,
            clock=lambda: 20.0,
            protocol="terminal",
        )

    def send(self, text):
        return handle_message(text, self.memory)

    def test_english_identity_faq(self):
        response, should_exit = self.send("who are you?")
        self.assertFalse(should_exit)
        self.assertIn(response, en.BOT_IDENTITY_RESPONSES)
        self.assertIn("technical reviewer", response.lower())
        self.assertEqual(
            self.memory.session.last_intent,
            Intent.BOT_IDENTITY_QUERY,
        )

    def test_english_capabilities_faq(self):
        response, _ = self.send("what can you do?")
        self.assertIn(response, en.BOT_CAPABILITIES_RESPONSES)
        self.assertIn("!help", response)

    def test_argentine_faq(self):
        response, _ = self.send("quien sos?")
        self.assertIn(response, ar.BOT_IDENTITY_RESPONSES)
        self.assertEqual(self.memory.session.language, "argentine")

    def test_faq_preserves_pending_prompt(self):
        self.memory.session.last_prompt = Prompt.ACTIVITY
        self.memory.session.language = "english"

        response, _ = self.send("what can you do?")
        self.assertIn(response, en.BOT_CAPABILITIES_RESPONSES)
        self.assertEqual(self.memory.session.last_prompt, Prompt.ACTIVITY)

        self.send("building a discord bot")
        self.assertEqual(
            self.memory.task.activity,
            "building a discord bot",
        )

    def test_conversational_joke_english(self):
        response, _ = self.send("tell me a joke")
        self.assertIn(response, en.JOKES)
        self.assertEqual(self.memory.session.last_intent, Intent.JOKE_REQUEST)

    def test_conversational_joke_argentine(self):
        response, _ = self.send("contame un chiste")
        self.assertIn(response, ar.JOKES)
        self.assertEqual(self.memory.session.language, "argentine")

    def test_joke_command_follows_current_language(self):
        self.memory.session.language = "argentine"
        result = handle_command("!joke", self.memory, self.runtime)
        self.assertIn(result.text, ar.JOKES)

        self.memory.session.language = "english"
        result = handle_command("!joke", self.memory, self.runtime)
        self.assertIn(result.text, en.JOKES)

    def test_blank_input_is_a_state_preserving_noop(self):
        self.memory.session.last_prompt = Prompt.ACTIVITY
        self.memory.profile.name = "Darko"
        before = (
            self.memory.session.language,
            self.memory.session.last_prompt,
            self.memory.session.last_intent,
            self.memory.session.tone,
            self.memory.session.failure_streak,
            self.memory.task.activity,
            self.memory.task.focus,
            self.memory.task.next_step,
            self.memory.profile.name,
        )

        response, should_exit = self.send("   \t ")
        self.assertIsNone(response)
        self.assertFalse(should_exit)

        after = (
            self.memory.session.language,
            self.memory.session.last_prompt,
            self.memory.session.last_intent,
            self.memory.session.tone,
            self.memory.session.failure_streak,
            self.memory.task.activity,
            self.memory.task.focus,
            self.memory.task.next_step,
            self.memory.profile.name,
        )
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()

