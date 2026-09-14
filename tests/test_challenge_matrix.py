import random
import unittest
from unittest.mock import patch

from data import english as en
from engine.commands.models import CommandAction, CommandRuntime
from engine.commands.parser import parse_command
from engine.commands.registry import command_names
from engine.commands.service import handle_command
from engine.conversation import handle_message
from engine.detect import detect_intent
from engine.memory import MemoryStore
from engine.models import Intent, Prompt, Tone
from engine.normalize import normalize_message


class ChallengeAcceptanceMatrixTests(unittest.TestCase):
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

    # EASY

    def test_easy_greetings_and_goodbyes(self):
        response, should_exit = self.send("hi")
        self.assertIn("Dee Dee:", response)
        self.assertFalse(should_exit)

        response, should_exit = self.send("bye")
        self.assertIn("Dee Dee:", response)
        self.assertTrue(should_exit)

    def test_easy_common_questions(self):
        response, _ = self.send("who are you?")
        self.assertIn("technical reviewer", response.lower())

        response, _ = self.send("what can you do?")
        self.assertIn("!help", response)

    def test_easy_jokes_and_fun_responses(self):
        response, _ = self.send("make me laugh")
        self.assertIn(response, en.JOKES)

        result = handle_command("!joke", self.memory, self.runtime)
        self.assertIn(result.text, en.JOKES)

    def test_easy_unknown_message_handling(self):
        response, should_exit = self.send("quantum banana wallpaper")
        self.assertFalse(should_exit)
        self.assertIn(response, en.UNKNOWN_RESPONSES)

    def test_easy_exit_command(self):
        result = handle_command("!exit", self.memory, self.runtime)
        self.assertEqual(result.action, CommandAction.EXIT_SESSION)

    # MEDIUM

    def test_medium_remember_user_name(self):
        self.send("my name is Darko")
        response, _ = self.send("what is my name?")
        self.assertIn("Darko", response)

    def test_medium_random_responses(self):
        self.memory.session.last_prompt = Prompt.WELLBEING
        with patch(
            "engine.conversation.random.choice",
            return_value=en.POSITIVE_FOLLOWUPS[0],
        ) as chooser:
            response, _ = self.send("yes")
        chooser.assert_called()
        self.assertEqual(response, en.POSITIVE_FOLLOWUPS[0])
        self.assertGreater(len(en.POSITIVE_FOLLOWUPS), 1)

    def test_medium_multiple_conversation_topics(self):
        identity, _ = self.send("who are you?")
        joke, _ = self.send("tell me a joke")
        self.memory.session.last_prompt = Prompt.ACTIVITY
        task, _ = self.send("building a discord bot")

        self.assertIn("technical reviewer", identity.lower())
        self.assertIn(joke, en.JOKES)
        self.assertIn("Dee Dee:", task)

    def test_medium_custom_commands(self):
        result = handle_command("!help", self.memory, self.runtime)
        self.assertIn("!joke", result.text)
        self.assertIn("!mood", result.text)

    def test_medium_basic_conversation_state(self):
        self.memory.session.last_prompt = Prompt.VIBE
        self.memory.session.language = "english"
        self.send("just coding")
        self.assertEqual(self.memory.session.last_prompt, Prompt.ACTIVITY)

        self.send("building a bot")
        self.assertEqual(
            self.memory.session.last_prompt,
            Prompt.ACTIVITY_DETAIL,
        )

    # HARD

    def test_hard_conversation_memory(self):
        self.memory.session.last_prompt = Prompt.ACTIVITY
        self.send("building a discord bot")
        self.send("command routing")
        self.send("add tests")

        response, _ = self.send("what am i working on?")
        self.assertIn("building a discord bot", response)

    def test_hard_intent_detection(self):
        normalized = normalize_message("tell me a joke")
        detection = detect_intent(
            "tell me a joke",
            normalized,
            self.memory,
        )
        self.assertEqual(detection.intent, Intent.JOKE_REQUEST)

    def test_hard_understands_different_phrasings(self):
        hello = detect_intent(
            "hello",
            normalize_message("hello"),
            self.memory,
        )
        typo = detect_intent(
            "helo",
            normalize_message("helo"),
            self.memory,
        )
        self.assertEqual(hello.intent, Intent.GREETING)
        self.assertEqual(typo.intent, Intent.GREETING)

    def test_hard_context_aware_replies(self):
        self.memory.session.last_prompt = Prompt.ACTIVITY
        self.memory.session.language = "english"

        self.send("what can you do?")
        self.assertEqual(self.memory.session.last_prompt, Prompt.ACTIVITY)

        self.send("building a discord bot")
        self.assertEqual(
            self.memory.task.activity,
            "building a discord bot",
        )

    def test_hard_different_personality_moods(self):
        self.send("I deleted the test because it kept failing")
        self.assertEqual(self.memory.session.tone, Tone.SARCASTIC)

        self.send("it works now")
        self.assertEqual(self.memory.session.tone, Tone.PLAYFUL)

        self.send("this failed again")
        self.send("it is still failing")
        self.assertEqual(self.memory.session.tone, Tone.MOTIVATIONAL)

    def test_hard_own_command_system(self):
        parsed = parse_command("!HeLp", command_names())
        self.assertEqual(parsed.command.name, "help")

        unknown = parse_command("!hep", command_names())
        self.assertEqual(unknown.command.name, "hep")

        result = handle_command("!HeLp", self.memory, self.runtime)
        self.assertIn("command registry", result.text)


if __name__ == "__main__":
    unittest.main()

