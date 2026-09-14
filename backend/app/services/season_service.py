from datetime import datetime


def get_current_season() -> int:
    """NFL season runs Sept-Feb, so Jan-Feb should use the previous year."""
    now = datetime.now()
    return now.year - 1 if now.month <= 2 else now.year
