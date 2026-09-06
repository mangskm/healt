from datetime import datetime, time, timezone

from app.models.profile import UserProfile
from app.models.reminder import Reminder, ReminderScheduleType, ReminderType
from app.models.user import User
from app.services.reminder import ReminderService


def payload(**overrides):
    return {"reminder_type": "weight", "title": "  Log weight  ", "reminder_time": "08:00:00", "schedule_type": "daily", "day_of_week": None, "enabled": True, "note": "  optional note  ", **overrides}


def test_reminder_crud_and_enable_disable(client) -> None:
    created = client.post("/api/v1/reminders", json=payload())
    reminder_id = created.json()["id"]
    read = client.get(f"/api/v1/reminders/{reminder_id}")
    updated = client.patch(f"/api/v1/reminders/{reminder_id}", json={"enabled": False, "title": "Updated reminder"})
    listed = client.get("/api/v1/reminders")
    deleted = client.delete(f"/api/v1/reminders/{reminder_id}")

    assert created.status_code == 201
    assert created.json()["title"] == "Log weight"
    assert created.json()["note"] == "optional note"
    assert read.status_code == 200
    assert updated.json()["enabled"] is False
    assert listed.json()["total"] == 1
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/reminders/{reminder_id}").status_code == 404


def test_weekly_and_daily_schedule_validation(client) -> None:
    weekly = client.post("/api/v1/reminders", json=payload(reminder_type="exercise", schedule_type="weekly", day_of_week=0))
    invalid_day = client.post("/api/v1/reminders", json=payload(schedule_type="weekly", day_of_week=7))
    daily_day = client.post("/api/v1/reminders", json=payload(day_of_week=1))
    weekly_without_day = client.post("/api/v1/reminders", json=payload(schedule_type="weekly", day_of_week=None))
    blank_title = client.post("/api/v1/reminders", json=payload(title="   "))

    assert weekly.status_code == 201
    assert all(response.status_code == 422 for response in (invalid_day, daily_day, weekly_without_day, blank_title))
    url = f"/api/v1/reminders/{weekly.json()['id']}"
    assert client.patch(url, json={"schedule_type": "daily", "day_of_week": None}).status_code == 200
    assert client.patch(url, json={"day_of_week": 2}).status_code == 422


def test_reminders_are_scoped_to_local_owner(client, db_session) -> None:
    local = client.post("/api/v1/reminders", json=payload()).json()
    other = User(created_at=datetime(2100, 1, 1, tzinfo=timezone.utc), updated_at=datetime(2100, 1, 1, tzinfo=timezone.utc))
    db_session.add(other); db_session.flush()
    hidden = Reminder(user_id=other.id, reminder_type=ReminderType.CUSTOM, title="Other", reminder_time=time(9), schedule_type=ReminderScheduleType.DAILY)
    db_session.add(hidden); db_session.commit()

    assert client.get("/api/v1/reminders").json()["items"][0]["id"] == local["id"]
    assert client.get(f"/api/v1/reminders/{hidden.id}").status_code == 404


def test_today_notifications_use_profile_timezone_weekday_and_status(db_session) -> None:
    user = User(); db_session.add(user); db_session.flush()
    db_session.add(UserProfile(user_id=user.id, timezone="Asia/Bangkok"))
    db_session.add_all([
        Reminder(user_id=user.id, reminder_type=ReminderType.WEIGHT, title="Daily later", reminder_time=time(8), schedule_type=ReminderScheduleType.DAILY),
        Reminder(user_id=user.id, reminder_type=ReminderType.MEAL, title="Daily due", reminder_time=time(6), schedule_type=ReminderScheduleType.DAILY),
        Reminder(user_id=user.id, reminder_type=ReminderType.EXERCISE, title="Weekly match", reminder_time=time(7), schedule_type=ReminderScheduleType.WEEKLY, day_of_week=0),
        Reminder(user_id=user.id, reminder_type=ReminderType.CUSTOM, title="Weekly no match", reminder_time=time(7, 30), schedule_type=ReminderScheduleType.WEEKLY, day_of_week=1),
    ])
    db_session.commit()

    result = ReminderService(db_session).today(now=datetime(2026, 9, 7, 0, 30, tzinfo=timezone.utc))

    assert result.timezone == "Asia/Bangkok"
    assert str(result.local_date) == "2026-09-07"
    assert [item.title for item in result.reminders] == ["Daily due", "Weekly match", "Daily later"]
    assert [item.status for item in result.reminders] == ["due", "due", "upcoming"]


def test_today_notifications_fall_back_to_utc(db_session) -> None:
    user = User(); db_session.add(user); db_session.flush()
    db_session.add(Reminder(user_id=user.id, reminder_type=ReminderType.CUSTOM, title="UTC", reminder_time=time(8), schedule_type=ReminderScheduleType.DAILY)); db_session.commit()

    result = ReminderService(db_session).today(now=datetime(2026, 9, 7, 7, 30, tzinfo=timezone.utc))

    assert result.timezone == "UTC"
    assert result.reminders[0].status == "upcoming"
