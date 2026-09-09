from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.models.profile import UserProfile


@dataclass(frozen=True)
class LocalDateRange:
    timezone_name: str
    zone: ZoneInfo
    start_date: date
    end_date: date
    start_utc: datetime
    end_utc: datetime


def profile_timezone(profile: UserProfile | None) -> tuple[str, ZoneInfo]:
    timezone_name = profile.timezone if profile and profile.timezone else None
    if timezone_name:
        try:
            return timezone_name, ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError:
            pass
    return "UTC", ZoneInfo("UTC")


def month_range(profile: UserProfile | None, month: str | None, now: datetime | None = None) -> LocalDateRange:
    timezone_name, zone = profile_timezone(profile)
    if month is None:
        selected = (now or datetime.now(timezone.utc)).astimezone(zone).date().replace(day=1)
    else:
        try:
            selected = datetime.strptime(month, "%Y-%m").date().replace(day=1)
        except ValueError as error:
            raise ValueError("Month must use YYYY-MM format.") from error
        if month != selected.strftime("%Y-%m"):
            raise ValueError("Month must use YYYY-MM format.")
    next_month = (selected.replace(day=28) + timedelta(days=4)).replace(day=1)
    return local_date_range(timezone_name, zone, selected, next_month - timedelta(days=1))


def local_date_range(timezone_name: str, zone: ZoneInfo, start_date: date, end_date: date) -> LocalDateRange:
    if start_date > end_date:
        raise ValueError("Start date must be on or before end date.")
    start_utc = datetime.combine(start_date, time.min, tzinfo=zone).astimezone(timezone.utc)
    end_utc = datetime.combine(end_date + timedelta(days=1), time.min, tzinfo=zone).astimezone(timezone.utc)
    return LocalDateRange(timezone_name, zone, start_date, end_date, start_utc, end_utc)
