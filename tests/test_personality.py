import random
import unittest

from data import english as en
from engine.commands.models import CommandRuntime
from engine.commands.service import handle_command
from engine.conversation import handle_message
from engine.memory import MemoryStore
from engine.models import Prompt, Tone


class AdaptivePersonalityTests(unittest.TestCase):
    def setUp(self):
        random.seed(0)
        self.memory = MemoryStore().get(("guild", "channel", "user"))
        self.runtime = CommandRuntime(
            started_at=10.0,
            clock=lambda: 20.0,
            protocol="terminal",
        )

    def send(self, text):
        return handle_message(text, self.memory)

    def test_bad_engineering_triggers_sarcastic_tone(self):
        response, _ = self.send(
            "I deleted the test because it kept failing"
        )
        self.assertEqual(self.memory.session.tone, Tone.SARCASTIC)
        self.assertIn("Dee Dee:", response)

    def test_success_triggers_playful_tone(self):
        response, _ = self.send("it works now")
        self.assertEqual(self.memory.session.tone, Tone.PLAYFUL)
        self.assertIn("Dee Dee:", response)

    def test_first_technical_setback_stays_focused(self):
        response, _ = self.send("this failed again")
        self.assertEqual(self.memory.session.failure_streak, 1)
        self.assertEqual(self.memory.session.tone, Tone.FOCUSED)
        self.assertIn("Dee Dee:", response)

    def test_repeated_setback_escalates_to_motivational(self):
        self.send("this failed again")
        response, _ = self.send("it is still failing")
        self.assertGreaterEqual(self.memory.session.failure_streak, 2)
        self.assertEqual(self.memory.session.tone, Tone.MOTIVATIONAL)
        self.assertIn(response, en.MOTIVATIONAL_RESPONSES)

    def test_direct_discouragement_is_motivational(self):
        response, _ = self.send("I can't do this, I want to give up")
        self.assertEqual(self.memory.session.tone, Tone.MOTIVATIONAL)
        self.assertIn("Dee Dee:", response)

    def test_negative_wellbeing_is_serious(self):
        self.memory.session.last_prompt = Prompt.WELLBEING
        self.memory.session.language = "english"
        self.send("not good")
        self.assertEqual(self.memory.session.tone, Tone.SERIOUS)

    def test_mood_command_reports_adaptive_personality(self):
        self.send("I deleted the test because it kept failing")
        result = handle_command("!mood", self.memory, self.runtime)
        self.assertIn("sarcastic", result.text)
        self.assertIn("Control : adaptive", result.text)
        self.assertIn("strict / technical", result.text)

    def test_mood_command_does_not_interrupt_prompt(self):
        self.memory.session.last_prompt = Prompt.ACTIVITY
        handle_command("!mood", self.memory, self.runtime)
        self.assertEqual(self.memory.session.last_prompt, Prompt.ACTIVITY)


if __name__ == "__main__":
    unittest.main()

