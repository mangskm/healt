import csv
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from io import StringIO
from typing import Literal

from sqlalchemy.orm import Session

from app.models.profile import WeightUnit
from app.models.user import User
from app.repositories.profile import ProfileRepository
from app.repositories.reports import ReportRepository
from app.services.reporting import LocalDateRange, local_date_range, month_range, profile_timezone
from app.services.weight_units import from_kilograms

ExportType = Literal["weight", "meals", "exercise"]
ExportRange = Literal["month", "last_30_days", "custom"]


def _safe_cell(value: str | None) -> str:
    if value is None:
        return ""
    text = str(value)
    return f"'{text}" if text.lstrip().startswith(("=", "+", "-", "@")) else text


def _number(value: Decimal | float | int | None) -> str:
    if value is None:
        return ""
    return format(Decimal(str(value)).normalize(), "f")


def _local_timestamp(value: datetime, period: LocalDateRange) -> str:
    # PostgreSQL returns timezone-aware values. SQLite, used by the test suite,
    # drops tzinfo for this column type, so retain the application's UTC storage
    # convention when formatting that fallback.
    if value.tzinfo is None or value.utcoffset() is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(period.zone).isoformat(timespec="seconds")


class ExportService:
    """Server-generated, user-owned CSV exports with spreadsheet-safe text cells."""

    def __init__(self, db: Session, user: User) -> None:
        self._user = user
        self._profiles = ProfileRepository(db)
        self._reports = ReportRepository(db)

    def create_csv(
        self,
        data_type: ExportType,
        range_type: ExportRange,
        month: str | None,
        start: date | None,
        end: date | None,
        now: datetime | None = None,
    ) -> tuple[str, str]:
        profile = self._profiles.get_for_user(self._user.id)
        period = self._resolve_period(profile, range_type, month, start, end, now)
        if data_type == "weight":
            content = self._weight_csv(period, profile.weight_unit if profile and profile.weight_unit else WeightUnit.KILOGRAMS)
        elif data_type == "meals":
            content = self._meals_csv(period)
        else:
            content = self._exercise_csv(period)
        filename = f"{data_type}-{period.start_date.isoformat()}-to-{period.end_date.isoformat()}.csv"
        return content, filename

    def _resolve_period(self, profile, range_type: ExportRange, month: str | None, start: date | None, end: date | None, now: datetime | None) -> LocalDateRange:
        if range_type == "month":
            return month_range(profile, month, now)
        timezone_name, zone = profile_timezone(profile)
        if range_type == "last_30_days":
            today = (now or datetime.now(timezone.utc)).astimezone(zone).date()
            return local_date_range(timezone_name, zone, today - timedelta(days=29), today)
        if start is None or end is None:
            raise ValueError("Custom exports require both start and end dates.")
        return local_date_range(timezone_name, zone, start, end)

    def _writer(self) -> tuple[StringIO, csv.writer]:
        output = StringIO(newline="")
        return output, csv.writer(output, lineterminator="\n")

    def _weight_csv(self, period: LocalDateRange, unit: WeightUnit) -> str:
        output, writer = self._writer()
        writer.writerow(["recorded_at_local", "weight", "unit", "note"])
        for record in self._reports.weight_records_in_range(self._user.id, period.start_utc, period.end_utc):
            writer.writerow([_local_timestamp(record.recorded_at, period), _number(from_kilograms(Decimal(str(record.weight_kg)), unit)), unit.value, _safe_cell(record.note)])
        return output.getvalue()

    def _meals_csv(self, period: LocalDateRange) -> str:
        output, writer = self._writer()
        writer.writerow(["eaten_at_local", "meal_type", "meal_note", "food_name", "quantity", "unit", "calories_kcal", "protein_g", "carbohydrates_g", "fat_g"])
        for meal in self._reports.meals_in_range(self._user.id, period.start_utc, period.end_utc):
            for item in meal.items:
                writer.writerow([
                    _local_timestamp(meal.eaten_at, period), meal.meal_type.value, _safe_cell(meal.note), _safe_cell(item.food_name),
                    _number(item.quantity), item.unit.value, _number(item.calories_kcal), _number(item.protein_g),
                    _number(item.carbohydrates_g), _number(item.fat_g),
                ])
        return output.getvalue()

    def _exercise_csv(self, period: LocalDateRange) -> str:
        output, writer = self._writer()
        writer.writerow(["performed_at_local", "activity_type", "duration_minutes", "distance", "distance_unit", "calories_entered_kcal", "note"])
        for session in self._reports.exercise_sessions_in_range(self._user.id, period.start_utc, period.end_utc):
            writer.writerow([
                _local_timestamp(session.performed_at, period), session.activity_type.value, session.duration_minutes,
                _number(session.distance_km), "km" if session.distance_km is not None else "", _number(session.calories_burned_kcal), _safe_cell(session.note),
            ])
        return output.getvalue()
