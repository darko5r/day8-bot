import unittest

from engine.commands.models import CommandParseStatus
from engine.commands.parser import parse_command
from engine.commands.registry import command_names


class CommandParserTests(unittest.TestCase):
    def parse(self, text):
        return parse_command(text, command_names())

    def test_non_command_is_not_claimed(self):
        result = self.parse("hello")
        self.assertEqual(result.status, CommandParseStatus.NOT_COMMAND)

    def test_command_name_is_case_insensitive(self):
        for text in ("!help", "!HELP", "!Help", "!hElP"):
            with self.subTest(text=text):
                result = self.parse(text)
                self.assertEqual(result.status, CommandParseStatus.VALID)
                self.assertEqual(result.command.name, "help")

    def test_argument_case_is_preserved(self):
        result = self.parse("!WHOIS Darko TheDev")
        self.assertEqual(result.status, CommandParseStatus.VALID)
        self.assertEqual(result.command.name, "whois")
        self.assertEqual(result.command.argument_text, "Darko TheDev")

    def test_malformed_command_forms_are_rejected(self):
        for text in ("!", "! help", "!!help"):
            with self.subTest(text=text):
                result = self.parse(text)
                self.assertEqual(result.status, CommandParseStatus.MALFORMED)

    def test_unknown_command_is_not_fuzzy_executed(self):
        result = self.parse("!hep")
        self.assertEqual(result.status, CommandParseStatus.UNKNOWN)
        self.assertEqual(result.command.name, "hep")

    def test_slash_command_is_not_a_dee_dee_command(self):
        result = self.parse("/help")
        self.assertEqual(result.status, CommandParseStatus.NOT_COMMAND)


if __name__ == "__main__":
    unittest.main()
