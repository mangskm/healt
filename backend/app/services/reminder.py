from datetime import datetime, timezone
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.models.reminder import Reminder, ReminderScheduleType
from app.models.user import User
from app.repositories.profile import ProfileRepository
from app.repositories.reminder import ReminderRepository
from app.schemas.reminder import ReminderCreate, ReminderListResponse, ReminderResponse, ReminderUpdate, TodayNotificationsResponse, TodayReminder


class ReminderNotFoundError(Exception):
    pass


class ReminderService:
    def __init__(self, db: Session, user: User) -> None:
        self._db = db
        self._user = user
        self._profiles = ProfileRepository(db)
        self._reminders = ReminderRepository(db)

    def list_reminders(self) -> ReminderListResponse:
        reminders, total = self._reminders.list_for_user(self._user.id)
        return ReminderListResponse(items=[ReminderResponse.model_validate(reminder) for reminder in reminders], total=total)

    def get_reminder(self, reminder_id: UUID) -> ReminderResponse:
        return ReminderResponse.model_validate(self._owned(reminder_id))

    def create_reminder(self, payload: ReminderCreate) -> ReminderResponse:
        reminder = Reminder(user_id=self._user.id, **payload.model_dump())
        self._reminders.add(reminder)
        self._reminders.save()
        self._db.refresh(reminder)
        return ReminderResponse.model_validate(reminder)

    def update_reminder(self, reminder_id: UUID, payload: ReminderUpdate) -> ReminderResponse:
        reminder = self._owned(reminder_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(reminder, field, value)
        self._validate_schedule(reminder)
        self._reminders.save()
        self._db.refresh(reminder)
        return ReminderResponse.model_validate(reminder)

    def delete_reminder(self, reminder_id: UUID) -> None:
        self._reminders.delete(self._owned(reminder_id))
        self._reminders.save()

    def today(self, now: datetime | None = None) -> TodayNotificationsResponse:
        profile = self._profiles.get_for_user(self._user.id)
        timezone_name = profile.timezone if profile and profile.timezone else "UTC"
        local_now = (now or datetime.now(timezone.utc)).astimezone(ZoneInfo(timezone_name))
        reminders = [reminder for reminder in self._reminders.list_enabled_for_user(self._user.id) if reminder.schedule_type is ReminderScheduleType.DAILY or reminder.day_of_week == local_now.weekday()]
        return TodayNotificationsResponse(timezone=timezone_name, local_date=local_now.date(), reminders=[TodayReminder(id=reminder.id, reminder_type=reminder.reminder_type, title=reminder.title, reminder_time=reminder.reminder_time, schedule_type=reminder.schedule_type, day_of_week=reminder.day_of_week, enabled=reminder.enabled, status="upcoming" if local_now.time() < reminder.reminder_time else "due") for reminder in reminders])

    def _owned(self, reminder_id: UUID) -> Reminder:
        reminder = self._reminders.get_for_user(self._user.id, reminder_id)
        if reminder is None:
            raise ReminderNotFoundError
        return reminder

    @staticmethod
    def _validate_schedule(reminder: Reminder) -> None:
        if reminder.schedule_type is ReminderScheduleType.DAILY and reminder.day_of_week is not None:
            raise ValueError("Daily reminders must not include a day of week.")
        if reminder.schedule_type is ReminderScheduleType.WEEKLY and reminder.day_of_week is None:
            raise ValueError("Weekly reminders require a day of week.")
