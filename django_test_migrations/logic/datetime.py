import datetime


def timedelta_to_miliseconds(timedelta: datetime.timedelta) -> int:
    """Convert ``timedelta`` object to miliseconds."""
    return int(timedelta.total_seconds() * 1000)
