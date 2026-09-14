import random
import unittest

from engine.conversation import handle_message
from engine.memory import MemoryStore
from engine.models import Prompt


class ConversationTests(unittest.TestCase):
    def setUp(self):
        random.seed(0)
        self.store = MemoryStore()
        self.memory = self.store.get(("guild", "channel", "user"))

    def send(self, message):
        return handle_message(message, self.memory)

    def test_english_task_memory_flow(self):
        self.memory.session.last_prompt = Prompt.VIBE
        self.memory.session.language = "english"

        self.send("just coding")
        self.send("i am building a discord bot")
        self.send("the command routing")
        self.send("add tests")

        response, should_exit = self.send("what am i working on?")
        self.assertFalse(should_exit)
        self.assertIn("i am building a discord bot", response)

        response, _ = self.send("what else?")
        self.assertIn("Activity : i am building a discord bot", response)
        self.assertIn("Focus    : the command routing", response)
        self.assertNotIn("Next", response)

        response, _ = self.send("what should i do next?")
        self.assertIn("Next     : add tests", response)
        self.assertNotIn("Focus", response)

    def test_english_wellbeing_to_activity_transition(self):
        self.memory.session.last_prompt = Prompt.WELLBEING
        self.memory.session.language = "english"

        self.send("yes")
        self.assertEqual(
            self.memory.session.last_prompt,
            Prompt.VIBE,
        )

        self.send("just coding")
        self.assertEqual(
            self.memory.session.last_prompt,
            Prompt.ACTIVITY,
        )

        self.send("i am building a discord bot")
        self.assertEqual(
            self.memory.task.activity,
            "i am building a discord bot",
        )
        self.assertEqual(
            self.memory.session.last_prompt,
            Prompt.ACTIVITY_DETAIL,
        )

    def test_argentine_wellbeing_to_activity_transition(self):
        self.memory.session.last_prompt = Prompt.WELLBEING
        self.memory.session.language = "argentine"

        self.send("si")
        self.assertEqual(
            self.memory.session.last_prompt,
            Prompt.VIBE,
        )

        self.send("laburando")
        self.assertEqual(
            self.memory.session.last_prompt,
            Prompt.ACTIVITY,
        )

        self.send("estoy armando un bot de discord")
        self.assertEqual(
            self.memory.task.activity,
            "estoy armando un bot de discord",
        )
        self.assertEqual(
            self.memory.session.last_prompt,
            Prompt.ACTIVITY_DETAIL,
        )

    def test_name_memory(self):
        self.send("my name is Darko")
        response, _ = self.send("what is my name?")
        self.assertIn("Darko", response)

    def test_argentine_flow(self):
        self.memory.session.last_prompt = Prompt.VIBE
        self.memory.session.language = "argentine"

        self.send("laburando")
        self.send("estoy armando un bot de discord")
        self.send("el ruteo de comandos")
        self.send("agregar tests")

        response, _ = self.send("que mas?")
        self.assertIn("Actividad : estoy armando un bot de discord", response)
        self.assertIn("Foco      : el ruteo de comandos", response)

        response, _ = self.send("que sigue?")
        self.assertIn("Siguiente : agregar tests", response)

    def test_memory_is_scoped(self):
        first = self.store.get(("guild", "channel", "alice"))
        second = self.store.get(("guild", "channel", "bob"))

        first.profile.name = "Alice"
        first.task.activity = "secret project"

        self.assertIsNone(second.profile.name)
        self.assertIsNone(second.task.activity)

    def test_expressive_goodbye(self):
        response, should_exit = self.send("byeee")
        self.assertTrue(should_exit)
        self.assertIn("Dee Dee:", response)


if __name__ == "__main__":
    unittest.main()
