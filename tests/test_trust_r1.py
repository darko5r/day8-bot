import unittest

from engine.commands.models import (
    CommandAction,
    CommandRuntime,
    CommandStatus,
)
from engine.commands.service import handle_command
from engine.memory import MemoryStore
from engine.trust.models import (
    AuditAction,
    AuthorityRole,
    Capability,
    ServiceFlag,
    TrustOperationStatus,
)
from engine.trust.service import TrustService


class TrustR1ServiceTests(unittest.TestCase):
    def setUp(self):
        self.trust = TrustService("founder")

    def test_audit_records_applied_no_change_and_denied_role_operations(self):
        applied = self.trust.set_role(
            "founder",
            "alice",
            AuthorityRole.MEMBER,
        )
        no_change = self.trust.set_role(
            "founder",
            "alice",
            AuthorityRole.MEMBER,
        )
        denied = self.trust.set_role(
            "alice",
            "bob",
            AuthorityRole.MEMBER,
        )

        self.assertEqual(applied.status, TrustOperationStatus.APPLIED)
        self.assertEqual(no_change.status, TrustOperationStatus.NO_CHANGE)
        self.assertEqual(denied.status, TrustOperationStatus.DENIED)

        events = self.trust.audit_events(10)
        self.assertEqual([event.sequence for event in events], [1, 2, 3])
        self.assertTrue(
            all(event.action == AuditAction.ROLE_SET for event in events)
        )
        self.assertEqual(events[0].target_id, "alice")
        self.assertEqual(events[2].target_id, "bob")

    def test_flag_operations_are_audited(self):
        self.trust.set_role("founder", "alice", AuthorityRole.MEMBER)
        self.trust.set_flag(
            "founder",
            "alice",
            ServiceFlag.TRUSTED,
            True,
        )
        event = self.trust.audit_events(1)[0]
        self.assertEqual(event.action, AuditAction.FLAG_SET)
        self.assertEqual(event.actor_id, "founder")
        self.assertEqual(event.target_id, "alice")
        self.assertIn(ServiceFlag.TRUSTED, event.after_flags)

    def test_founder_transfer_is_atomic_and_changes_root_authority(self):
        self.trust.set_role("founder", "alice", AuthorityRole.SOP)
        result = self.trust.transfer_founder("founder", "alice")

        self.assertTrue(result.ok)
        self.assertEqual(self.trust.founder_id, "alice")
        self.assertEqual(
            self.trust.get("alice").role,
            AuthorityRole.FOUNDER,
        )
        self.assertEqual(
            self.trust.get("founder").role,
            AuthorityRole.SOP,
        )
        self.assertTrue(
            self.trust.authorize(
                "alice",
                Capability.SERVICE_SHUTDOWN,
            ).allowed
        )
        self.assertFalse(
            self.trust.authorize(
                "founder",
                Capability.SERVICE_SHUTDOWN,
            ).allowed
        )

        event = self.trust.audit_events(1)[0]
        self.assertEqual(event.action, AuditAction.FOUNDER_TRANSFER)
        self.assertEqual(event.status, TrustOperationStatus.APPLIED)

    def test_non_founder_cannot_transfer_founder(self):
        self.trust.set_role("founder", "sop", AuthorityRole.SOP)
        self.trust.set_role("founder", "alice", AuthorityRole.MEMBER)

        result = self.trust.transfer_founder("sop", "alice")

        self.assertEqual(result.status, TrustOperationStatus.DENIED)
        self.assertEqual(self.trust.founder_id, "founder")
        self.assertEqual(
            self.trust.audit_events(1)[0].action,
            AuditAction.FOUNDER_TRANSFER,
        )

    def test_records_are_stably_sorted(self):
        self.trust.set_role("founder", "zoe", AuthorityRole.MEMBER)
        self.trust.set_role("founder", "alice", AuthorityRole.MEMBER)
        ids = [record.stable_id for record in self.trust.records()]
        self.assertEqual(ids, sorted(ids))

    def test_service_audit_is_sop_or_founder_only(self):
        self.trust.set_role("founder", "sop", AuthorityRole.SOP)
        self.trust.set_role("founder", "op", AuthorityRole.OPERATOR)
        self.assertTrue(
            self.trust.authorize(
                "founder",
                Capability.SERVICE_AUDIT,
            ).allowed
        )
        self.assertTrue(
            self.trust.authorize(
                "sop",
                Capability.SERVICE_AUDIT,
            ).allowed
        )
        self.assertFalse(
            self.trust.authorize(
                "op",
                Capability.SERVICE_AUDIT,
            ).allowed
        )


class TrustR1CommandTests(unittest.TestCase):
    def setUp(self):
        self.memory = MemoryStore().get(("guild", "channel", "founder"))
        self.trust = TrustService("founder")
        self.runtime = self.runtime_for("founder")

    def runtime_for(self, actor_id):
        return CommandRuntime(
            started_at=10.0,
            clock=lambda: 20.0,
            protocol="terminal",
            actor_id=actor_id,
            trust_service=self.trust,
        )

    def command(self, text, actor="founder"):
        return handle_command(
            text,
            self.memory,
            self.runtime_for(actor),
        )

    def test_help_exposes_r1_trust_commands(self):
        result = self.command("!help")
        for command in ("!users", "!audit", "!founder"):
            self.assertIn(command, result.text)

    def test_users_is_operator_or_higher(self):
        self.command("!role set sop SOP")
        self.command("!role set op OP")
        self.command("!role set dev DV")

        op_result = self.command("!users", actor="op")
        self.assertEqual(op_result.status, CommandStatus.OK)
        self.assertIn("founder", op_result.text)
        self.assertIn("dev", op_result.text)

        denied = self.command("!users", actor="dev")
        self.assertEqual(denied.status, CommandStatus.FORBIDDEN)

    def test_audit_is_sop_or_founder_only(self):
        self.command("!role set sop SOP")
        self.command("!role set op OP")

        sop_result = self.command("!audit 10", actor="sop")
        self.assertEqual(sop_result.status, CommandStatus.OK)
        self.assertIn("role.set", sop_result.text)

        denied = self.command("!audit", actor="op")
        self.assertEqual(denied.status, CommandStatus.FORBIDDEN)

    def test_founder_transfer_requires_confirmation(self):
        self.command("!role set alice SOP")
        result = self.command("!founder transfer alice")
        self.assertEqual(result.status, CommandStatus.INVALID_ARGUMENTS)
        self.assertEqual(self.trust.founder_id, "founder")

    def test_founder_transfer_command_moves_shutdown_authority(self):
        self.command("!role set alice SOP")
        transfer = self.command("!founder transfer alice CONFIRM")
        self.assertEqual(transfer.status, CommandStatus.OK)
        self.assertEqual(self.trust.founder_id, "alice")

        old_shutdown = self.command("!shutdown", actor="founder")
        self.assertEqual(old_shutdown.status, CommandStatus.FORBIDDEN)
        self.assertEqual(old_shutdown.action, CommandAction.NONE)

        new_shutdown = self.command("!shutdown", actor="alice")
        self.assertEqual(new_shutdown.status, CommandStatus.OK)
        self.assertEqual(
            new_shutdown.action,
            CommandAction.SHUTDOWN_SERVICE,
        )

    def test_cross_user_whois_requires_profile_read_other(self):
        self.command("!role set op OP")
        self.command("!role set member MB")

        allowed = self.command("!whois member", actor="op")
        self.assertEqual(allowed.status, CommandStatus.OK)
        self.assertIn("Role     : MB", allowed.text)
        self.assertIn("Memory   : private", allowed.text)
        self.assertNotIn("Activity", allowed.text)

        denied = self.command("!whois op", actor="member")
        self.assertEqual(denied.status, CommandStatus.FORBIDDEN)

    def test_cross_user_capabilities_require_profile_read_other(self):
        self.command("!role set op OP")
        self.command("!role set member MB")

        allowed = self.command("!capabilities member", actor="op")
        self.assertEqual(allowed.status, CommandStatus.OK)
        self.assertIn("review.run", allowed.text)

        denied = self.command("!capabilities op", actor="member")
        self.assertEqual(denied.status, CommandStatus.FORBIDDEN)


if __name__ == "__main__":
    unittest.main()
