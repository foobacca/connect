from django.core.exceptions import PermissionDenied
from django.test import TestCase

from connect.accounts.factories import (
    AbuseReportFactory, BrandFactory, InvitedPendingFactory, ModeratorFactory,
    RequestedPendingFactory, RoleFactory, SkillFactory, UserFactory,
    UserLinkFactory, UserSkillFactory
)
from connect.accounts.models import CustomUser, UserLink, UserSkill


class UserModelTest(TestCase):
    fixtures = ['group_perms']

    def setUp(self):
        self.moderator = ModeratorFactory()
        self.standard_user = UserFactory(
            first_name='Firsto',
            last_name='Namo',
        )
        self.invited_pending = InvitedPendingFactory()
        self.requested_pending = RequestedPendingFactory()

    def test_string_method(self):
        self.assertEqual(self.standard_user.__str__(), 'Firsto Namo')

    def test_get_full_name(self):
        full_name = self.standard_user.get_full_name()

        self.assertEqual(full_name, 'Firsto Namo')

    def test_get_short_name(self):
        short_name = self.standard_user.get_short_name()

        self.assertEqual(short_name, 'Firsto')

    def test_is_pending_activation(self):
        self.assertFalse(self.standard_user.is_pending_activation())
        self.assertTrue(self.invited_pending.is_pending_activation())

    def test_is_invited_pending_activation(self):
        self.assertFalse(self.standard_user.is_invited_pending_activation())
        self.assertTrue(self.invited_pending.is_invited_pending_activation())

    def test_is_pending_approval(self):
        self.assertFalse(self.standard_user.is_pending_approval())
        self.assertTrue(self.requested_pending.is_pending_approval())

    def test_moderator_can_invite_new_user(self):
        user = self.moderator.invite_new_user(email='standard_user@test.test',
                                              first_name='standard_user',
                                              last_name='user')

        self.assertEqual(user.email, 'standard_user@test.test')
        self.assertEqual(user.first_name, 'standard_user')
        self.assertEqual(user.last_name, 'user')
        self.assertEqual(user.registration_method, CustomUser.INVITED)
        self.assertEqual(user.moderator, self.moderator)
        self.assertEqual(user.moderator_decision, CustomUser.PRE_APPROVED)
        self.assertIsNotNone(user.decision_datetime)
        self.assertIsNotNone(user.auth_token)

    def test_standard_user_user_cannot_invite_new_user(self):
        with self.assertRaises(PermissionDenied):
            self.standard_user.invite_new_user(
                email='standard_user@test.test',
                first_name='standard_user',
                last_name='user'
            )

    def test_moderator_can_reinvite_user(self):
        decision_datetime = self.invited_pending.decision_datetime
        auth_token = self.invited_pending.auth_token

        self.moderator.reinvite_user(user=self.invited_pending,
                                     email='reset_email@test.test')

        self.assertEqual(self.invited_pending.email, 'reset_email@test.test')
        self.assertNotEqual(self.invited_pending.decision_datetime,
                            decision_datetime)
        self.assertNotEqual(self.invited_pending.auth_token, auth_token)

    def test_standard_user_user_cannot_reinvite_user(self):
        with self.assertRaises(PermissionDenied):
            self.standard_user.reinvite_user(user=self.invited_pending,
                                             email='reset_email@test.test')

    def test_moderator_can_approve_user_application(self):
        self.moderator.approve_user_application(self.requested_pending)

        self.assertEqual(self.requested_pending.moderator, self.moderator)
        self.assertEqual(self.requested_pending.moderator_decision,
                         CustomUser.APPROVED)
        self.assertIsNotNone(self.requested_pending.decision_datetime)
        self.assertIsNotNone(self.requested_pending.auth_token)

    def test_standard_user_user_cannot_approve_user_application(self):
        with self.assertRaises(PermissionDenied):
            self.standard_user.approve_user_application(self.requested_pending)

    def test_moderator_can_reject_user_application(self):
        self.moderator.reject_user_application(self.requested_pending)

        self.assertEqual(self.requested_pending.moderator, self.moderator)
        self.assertEqual(self.requested_pending.moderator_decision,
                         CustomUser.REJECTED)
        self.assertIsNotNone(self.requested_pending.decision_datetime)
        self.assertIsNotNone(self.requested_pending.auth_token)

    def test_standard_user_user_cannot_reject_user_application(self):
        with self.assertRaises(PermissionDenied):
            self.standard_user.reject_user_application(self.requested_pending)


class AbuseReportTest(TestCase):
    def test_string_method(self):
        user1 = UserFactory(first_name='a', last_name='b')
        user2 = UserFactory(first_name='c', last_name='d')

        report = AbuseReportFactory(logged_against=user2,
                                    logged_by=user1)

        self.assertEqual(report.__str__(), 'Reported by a b against c d')


class SkillTest(TestCase):
    def test_string_method(self):
        skill = SkillFactory(name='MySkill')

        self.assertEqual(skill.__str__(), 'MySkill')


class UserSkillTest(TestCase):
    def test_string_method(self):
        user = UserFactory(first_name='a', last_name='b')
        skill = SkillFactory(name='MySkill')
        user_skill = UserSkillFactory(user=user, skill=skill)

        self.assertEqual(user_skill.__str__(), 'a b - MySkill')

    def test_proficiency_percentage(self):
        user_skill = UserSkillFactory(proficiency=UserSkill.INTERMEDIATE)
        percentage = user_skill.get_proficiency_percentage()

        self.assertEquals(percentage, 50)


class RoleTest(TestCase):
    def test_string_method(self):
        role = RoleFactory(name='MyRole')

        self.assertEqual(role.__str__(), 'MyRole')


class UserLinkTest(TestCase):
    def setUp(self):
        self.github = BrandFactory()  # Github is default brand.

    def test_string_method(self):
        user_link = UserLinkFactory(anchor='MyLink')

        self.assertEqual(user_link.__str__(), 'MyLink')

    def test_custom_save_method_finds_registered_brand(self):
        user_link = UserLinkFactory(url='http://github.com/nlh-kabu')

        self.assertEqual(user_link.icon, self.github)

    def test_custom_save_method_cannot_find_unregistered_brand(self):
        user_link = UserLinkFactory(url='http://blahblah.com/nlh-kabu')

        self.assertIsNone(user_link.icon)

    def test_get_icon_method_gets_correct_icon(self):
        user_link = UserLinkFactory(url='http://github.com/nlh-kabu')
        icon = user_link.get_icon()

        self.assertEqual(icon, 'fa-github')

    def test_get_icon_method_gets_default_icon(self):
        user_link = UserLinkFactory(url='http://noiconurl.com')
        icon = user_link.get_icon()

        self.assertEqual(icon, 'fa-globe')


class LinkBrandTest(TestCase):
    def test_string_method(self):
        brand = BrandFactory(name='Brand')

        self.assertEqual(brand.__str__(), 'Brand')

    def test_custom_save_method_applies_new_brand_to_existing_userlinks(self):
        UserLinkFactory(url='http://facebook.com/myusername')

        new_brand = BrandFactory(name='Facebook',
                                 domain='facebook.com',
                                 fa_icon='fa-facebook')

        # Retreive the link to check that it has the new brand
        link = UserLink.objects.get(url='http://facebook.com/myusername')

        self.assertEqual(link.icon, new_brand)

    def test_false_positive_does_not_apply_brand(self):
        UserLinkFactory(url='http://notreallyfacebook.com/me')

        BrandFactory(name='Facebook', domain='facebook.com',
                     fa_icon='fa-facebook')

        # Retreive the link to check that it does not have the new brand
        link = UserLink.objects.get(url='http://notreallyfacebook.com/me')

        self.assertIsNone(link.icon)
