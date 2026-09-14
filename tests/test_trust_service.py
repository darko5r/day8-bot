import unittest

from engine.trust.models import (
    AuthorityRole,
    Capability,
    DenialReason,
    ServiceFlag,
    TrustOperationStatus,
)
from engine.trust.service import TrustService


class TrustServiceTests(unittest.TestCase):
    def setUp(self):
        self.trust = TrustService("founder")

    def test_founder_is_bootstrapped_with_absolute_capabilities(self):
        founder = self.trust.get("founder")
        self.assertEqual(founder.role, AuthorityRole.FOUNDER)
        self.assertEqual(
            self.trust.effective_capabilities("founder"),
            frozenset(Capability),
        )

    def test_founder_can_assign_sop(self):
        result = self.trust.set_role(
            "founder",
            "alice",
            AuthorityRole.SOP,
        )
        self.assertTrue(result.ok)
        self.assertEqual(
            self.trust.get("alice").role,
            AuthorityRole.SOP,
        )

    def test_sop_can_assign_operator_developer_and_member(self):
        self.trust.set_role("founder", "sop", AuthorityRole.SOP)

        for target, role in (
            ("op", AuthorityRole.OPERATOR),
            ("dev", AuthorityRole.DEVELOPER),
            ("member", AuthorityRole.MEMBER),
        ):
            with self.subTest(role=role):
                result = self.trust.set_role("sop", target, role)
                self.assertTrue(result.ok)
                self.assertEqual(self.trust.get(target).role, role)

    def test_sop_cannot_assign_or_demote_sop(self):
        self.trust.set_role("founder", "sop1", AuthorityRole.SOP)
        self.trust.set_role("founder", "sop2", AuthorityRole.SOP)

        promote = self.trust.set_role(
            "sop1",
            "new-sop",
            AuthorityRole.SOP,
        )
        self.assertEqual(promote.status, TrustOperationStatus.DENIED)

        demote = self.trust.set_role(
            "sop1",
            "sop2",
            AuthorityRole.OPERATOR,
        )
        self.assertEqual(demote.status, TrustOperationStatus.DENIED)
        self.assertEqual(
            demote.reason,
            DenialReason.INSUFFICIENT_AUTHORITY,
        )

    def test_operator_can_manage_members_but_not_developers(self):
        self.trust.set_role("founder", "sop", AuthorityRole.SOP)
        self.trust.set_role("sop", "op", AuthorityRole.OPERATOR)

        member = self.trust.set_role(
            "op",
            "member",
            AuthorityRole.MEMBER,
        )
        self.assertTrue(member.ok)

        developer = self.trust.set_role(
            "op",
            "developer",
            AuthorityRole.DEVELOPER,
        )
        self.assertEqual(
            developer.status,
            TrustOperationStatus.DENIED,
        )
        self.assertEqual(
            developer.reason,
            DenialReason.MISSING_CAPABILITY,
        )

    def test_developer_member_and_guest_cannot_assign_roles(self):
        self.trust.set_role("founder", "sop", AuthorityRole.SOP)
        self.trust.set_role("sop", "dev", AuthorityRole.DEVELOPER)
        self.trust.set_role("sop", "member", AuthorityRole.MEMBER)
        self.trust.ensure_guest("guest")

        for actor in ("dev", "member", "guest"):
            with self.subTest(actor=actor):
                result = self.trust.set_role(
                    actor,
                    f"{actor}-target",
                    AuthorityRole.MEMBER,
                )
                self.assertEqual(
                    result.status,
                    TrustOperationStatus.DENIED,
                )

    def test_founder_is_protected_from_demotion(self):
        self.trust.set_role("founder", "sop", AuthorityRole.SOP)
        result = self.trust.set_role(
            "sop",
            "founder",
            AuthorityRole.MEMBER,
        )
        self.assertEqual(result.status, TrustOperationStatus.DENIED)
        self.assertEqual(result.reason, DenialReason.PROTECTED_FOUNDER)
        self.assertEqual(
            self.trust.get("founder").role,
            AuthorityRole.FOUNDER,
        )

    def test_founder_role_cannot_be_assigned_by_role_mutation(self):
        result = self.trust.set_role(
            "founder",
            "alice",
            AuthorityRole.FOUNDER,
        )
        self.assertEqual(result.status, TrustOperationStatus.DENIED)
        self.assertEqual(result.reason, DenialReason.POLICY_DENIED)

    def test_trusted_flag_is_founder_or_sop_only_and_grants_no_power(self):
        self.trust.set_role("founder", "sop", AuthorityRole.SOP)
        self.trust.set_role("sop", "op", AuthorityRole.OPERATOR)
        self.trust.set_role("op", "member", AuthorityRole.MEMBER)

        result = self.trust.set_flag(
            "sop",
            "member",
            ServiceFlag.TRUSTED,
            True,
        )
        self.assertTrue(result.ok)
        self.assertIn(
            ServiceFlag.TRUSTED,
            self.trust.get("member").flags,
        )
        self.assertNotIn(
            Capability.MODERATION_BAN,
            self.trust.effective_capabilities("member"),
        )

        denied = self.trust.set_flag(
            "op",
            "member",
            ServiceFlag.TRUSTED,
            False,
        )
        self.assertEqual(
            denied.status,
            TrustOperationStatus.DENIED,
        )

    def test_reviewer_and_mentor_flags_add_only_their_capabilities(self):
        self.trust.set_role("founder", "sop", AuthorityRole.SOP)
        self.trust.set_role("sop", "member", AuthorityRole.MEMBER)

        self.trust.set_flag(
            "sop",
            "member",
            ServiceFlag.REVIEWER,
            True,
        )
        self.trust.set_flag(
            "sop",
            "member",
            ServiceFlag.MENTOR,
            True,
        )

        capabilities = self.trust.effective_capabilities("member")
        self.assertIn(Capability.REVIEW_DEEP, capabilities)
        self.assertIn(Capability.REVIEW_PUBLISH, capabilities)
        self.assertIn(Capability.MENTOR_PROVIDE, capabilities)
        self.assertNotIn(Capability.MODERATION_KICK, capabilities)

    def test_self_awarded_flags_are_denied(self):
        self.trust.set_role("founder", "sop", AuthorityRole.SOP)
        result = self.trust.set_flag(
            "sop",
            "sop",
            ServiceFlag.TRUSTED,
            True,
        )
        self.assertEqual(result.status, TrustOperationStatus.DENIED)
        self.assertEqual(result.reason, DenialReason.SELF_ASSIGNMENT)

    def test_shutdown_is_founder_only(self):
        self.trust.set_role("founder", "sop", AuthorityRole.SOP)
        founder = self.trust.authorize(
            "founder",
            Capability.SERVICE_SHUTDOWN,
        )
        sop = self.trust.authorize(
            "sop",
            Capability.SERVICE_SHUTDOWN,
        )
        self.assertTrue(founder.allowed)
        self.assertFalse(sop.allowed)

    def test_role_capability_profiles_are_distinct(self):
        self.trust.set_role("founder", "sop", AuthorityRole.SOP)
        self.trust.set_role("sop", "op", AuthorityRole.OPERATOR)
        self.trust.set_role("sop", "dev", AuthorityRole.DEVELOPER)
        self.trust.set_role("sop", "member", AuthorityRole.MEMBER)
        self.trust.ensure_guest("guest")

        self.assertIn(
            Capability.MODERATION_BAN,
            self.trust.effective_capabilities("op"),
        )
        self.assertNotIn(
            Capability.MODERATION_BAN,
            self.trust.effective_capabilities("dev"),
        )
        self.assertIn(
            Capability.REVIEW_DEEP,
            self.trust.effective_capabilities("dev"),
        )
        self.assertNotIn(
            Capability.REVIEW_DEEP,
            self.trust.effective_capabilities("member"),
        )
        self.assertNotIn(
            Capability.REVIEW_RUN,
            self.trust.effective_capabilities("guest"),
        )

    def test_unknown_identity_fails_closed(self):
        decision = self.trust.authorize(
            "nobody",
            Capability.CORE_READ,
        )
        self.assertFalse(decision.allowed)
        self.assertEqual(
            decision.reason,
            DenialReason.UNKNOWN_IDENTITY,
        )


if __name__ == "__main__":
    unittest.main()
