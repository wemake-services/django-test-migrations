import typing

if typing.TYPE_CHECKING:
    from main_app.models import SomeItem  # noqa: WPS433


def is_clean_item(instance: 'SomeItem') -> bool:
    """Pure function that decides whether or not whitespace is in the model."""
    return ' ' not in instance.string_field
