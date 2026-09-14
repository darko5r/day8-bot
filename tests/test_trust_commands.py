import unittest

from engine.commands.models import (
    CommandAction,
    CommandRuntime,
    CommandStatus,
)
from engine.commands.service import handle_command
from engine.memory import MemoryStore
from engine.trust.models import AuthorityRole, ServiceFlag
from engine.trust.service import TrustService


class TrustCommandTests(unittest.TestCase):
    def setUp(self):
        self.memory = MemoryStore().get(("guild", "channel", "founder"))
        self.trust = TrustService("founder")
        self.runtime = CommandRuntime(
            started_at=10.0,
            clock=lambda: 20.0,
            protocol="terminal",
            actor_id="founder",
            trust_service=self.trust,
        )

    def command(self, text, runtime=None):
        return handle_command(
            text,
            self.memory,
            runtime or self.runtime,
        )

    def runtime_for(self, actor_id):
        return CommandRuntime(
            started_at=10.0,
            clock=lambda: 20.0,
            protocol="terminal",
            actor_id=actor_id,
            trust_service=self.trust,
        )

    def test_help_exposes_trust0_surface(self):
        result = self.command("!help")
        for command in (
            "!role",
            "!flag",
            "!capabilities",
            "!shutdown",
        ):
            self.assertIn(command, result.text)

    def test_founder_can_create_sop_through_role_command(self):
        result = self.command("!role set alice SOP")
        self.assertEqual(result.status, CommandStatus.OK)
        self.assertEqual(
            self.trust.get("alice").role,
            AuthorityRole.SOP,
        )

    def test_sop_can_create_operator_but_cannot_shutdown(self):
        self.command("!role set alice SOP")
        sop_runtime = self.runtime_for("alice")

        promote = self.command(
            "!role set bob OP",
            runtime=sop_runtime,
        )
        self.assertEqual(promote.status, CommandStatus.OK)
        self.assertEqual(
            self.trust.get("bob").role,
            AuthorityRole.OPERATOR,
        )

        shutdown = self.command(
            "!shutdown",
            runtime=sop_runtime,
        )
        self.assertEqual(shutdown.status, CommandStatus.FORBIDDEN)
        self.assertEqual(shutdown.action, CommandAction.NONE)

    def test_founder_shutdown_returns_service_action(self):
        result = self.command("!shutdown")
        self.assertEqual(result.status, CommandStatus.OK)
        self.assertEqual(
            result.action,
            CommandAction.SHUTDOWN_SERVICE,
        )

    def test_shutdown_fails_closed_without_trust_runtime(self):
        runtime = CommandRuntime(
            started_at=10.0,
            clock=lambda: 20.0,
            protocol="terminal",
        )
        result = self.command("!shutdown", runtime=runtime)
        self.assertEqual(result.status, CommandStatus.FORBIDDEN)
        self.assertEqual(result.action, CommandAction.NONE)

    def test_founder_can_grant_trusted_flag(self):
        self.command("!role set alice MB")
        result = self.command("!flag add alice T")
        self.assertEqual(result.status, CommandStatus.OK)
        self.assertIn(
            ServiceFlag.TRUSTED,
            self.trust.get("alice").flags,
        )

    def test_whois_reports_role_and_flags(self):
        self.memory.profile.name = "Darko"
        result = self.command("!whois")
        self.assertIn("Role     : FOUNDER", result.text)
        self.assertIn("Flags    : none", result.text)

    def test_capabilities_show_effective_role_power(self):
        self.command("!role set dev DV")
        result = self.command("!capabilities dev")
        self.assertIn("review.deep", result.text)
        self.assertNotIn("moderation.ban", result.text)

    def test_non_privileged_role_mutation_is_denied(self):
        self.command("!role set member MB")
        member_runtime = self.runtime_for("member")
        result = self.command(
            "!role set victim MB",
            runtime=member_runtime,
        )
        self.assertEqual(result.status, CommandStatus.FORBIDDEN)
        self.assertIsNone(self.trust.get("victim"))

    def test_role_and_flag_commands_do_not_touch_conversation_memory(self):
        before = (
            self.memory.session.language,
            self.memory.session.last_prompt,
            self.memory.session.last_intent,
            self.memory.task.activity,
            self.memory.task.focus,
            self.memory.task.next_step,
            self.memory.profile.name,
        )

        self.command("!role")
        self.command("!flag")
        self.command("!capabilities")

        after = (
            self.memory.session.language,
            self.memory.session.last_prompt,
            self.memory.session.last_intent,
            self.memory.task.activity,
            self.memory.task.focus,
            self.memory.task.next_step,
            self.memory.profile.name,
        )
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
