import datetime as dt


def timedelta_to_milliseconds(timedelta: dt.timedelta) -> int:
    """Convert ``timedelta`` object to milliseconds."""
    return int(timedelta.total_seconds() * 1000)
