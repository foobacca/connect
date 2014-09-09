import factory

from django.contrib.auth.models import Group
from django.utils import timezone

from .models import CustomUser, LinkBrand, Skill, UserLink, UserSkill


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    first_name = 'Standard'
    last_name = 'User'
    # Emails must be unique - so use a sequence here:
    email = factory.Sequence(lambda n: 'user.{}@test.test'.format(n))
    registration_method = CustomUser.INVITED


class ModeratorGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = 'Moderators'
    permissions = (
        ("access_moderators_section", "Can see the moderators section"),
        ("invite_user", "Can issue or reissue an invitation"),
        ("uninvite_user", "Can revoke a user invitation"),
        ("approve_user_application", "Can approve a user's application"),
        ("reject_user_application", "Can reject a user's application"),
        ("dismiss_abuse_report", "Can dismiss an abuse report"),
        ("warn_user", "Can warn a user in response to an abuse report"),
        ("ban_user", "Can ban a user in response to an abuse report"),
    )


class ModeratorFactory(UserFactory):
    first_name = 'Moderator'

    is_moderator = True
    is_superuser = True # Quick and dirty way to give moderator all permissions
    # MAKE ME A MODERATOR - BY ADDING MODERATOR GROUP PERMISSIONS...


class InvitedPendingFactory(factory.django.DjangoModelFactory):
    """
    User who has been invited by a moderator, but not yet
    activated their account
    """
    class Meta:
        model = CustomUser

    first_name = 'Invited Pending'
    last_name = 'User'
    email = factory.Sequence(lambda n: 'invited.pending.{}@test.test'.format(n))
    moderator = factory.SubFactory(UserFactory)


class RequestedPendingFactory(factory.django.DjangoModelFactory):
    """
    User who has requested an account, but not yet been accepted or rejected
    """
    class Meta:
        model = CustomUser

    first_name = 'Requested Pending'
    last_name = 'User'
    email = factory.Sequence(lambda n: 'requested.pending.{}@test.test'.format(n))
    registration_method = CustomUser.REQUESTED


class SkillFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Skill


class UserSkillFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserSkill

    user = factory.SubFactory(UserFactory)
    skill = factory.SubFactory(SkillFactory)
    proficiency = UserSkill.BEGINNER


class UserLinkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserLink

    user = factory.SubFactory(UserFactory)
    anchor = factory.Sequence(lambda n: 'linkname{}'.format(n))
    url = factory.Sequence(lambda n: 'url{}.test'.format(n))


class BrandFactory(factory.django.DjangoModelFactory):
    """
    Use github as a default for all LinkBrand objects
    """
    class Meta:
        model = LinkBrand

    name = 'Github'
    domain = 'github.com'
    fa_icon = 'fa-github'
