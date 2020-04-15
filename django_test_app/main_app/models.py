from django.db import models

_SomeItemStringFieldLength = 50


class SomeItem(models.Model):
    """We use this model for testing migrations."""

    string_field = models.CharField(max_length=_SomeItemStringFieldLength)
    is_clean = models.BooleanField()
