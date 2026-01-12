from django.db import models

DEFAULT_CHAR_FIELD_LENGTH = 50


class SomeItem(models.Model):
    """We use this model for testing migrations."""

    string_field = models.CharField(max_length=DEFAULT_CHAR_FIELD_LENGTH)
    is_clean = models.BooleanField()


class SomeMember(models.Model):
    """Member model for testing."""

    name = models.CharField(max_length=DEFAULT_CHAR_FIELD_LENGTH)


class SomeGroup(models.Model):
    """Group model for testing."""

    name = models.CharField(max_length=DEFAULT_CHAR_FIELD_LENGTH)
    members = models.ManyToManyField(
        SomeMember,
        through='SomeMembership',
        through_fields=('group', 'member'),
    )


class SomeMembership(models.Model):
    """Membership model for testing."""

    group = models.ForeignKey(SomeGroup, on_delete=models.CASCADE)
    member = models.ForeignKey(SomeMember, on_delete=models.CASCADE)
    invite_reason = models.CharField(max_length=DEFAULT_CHAR_FIELD_LENGTH)
