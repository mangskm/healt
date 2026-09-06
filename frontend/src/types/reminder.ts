export type ReminderType = "weight" | "meal" | "exercise" | "custom";
export type ReminderScheduleType = "daily" | "weekly";
export type ReminderStatus = "upcoming" | "due";

export interface Reminder { id: string; reminder_type: ReminderType; title: string; reminder_time: string; schedule_type: ReminderScheduleType; day_of_week: number | null; enabled: boolean; note: string | null; created_at: string; updated_at: string; }
export interface ReminderInput { reminder_type: ReminderType; title: string; reminder_time: string; schedule_type: ReminderScheduleType; day_of_week: number | null; enabled: boolean; note: string | null; }
export interface TodayReminder { id: string; reminder_type: ReminderType; title: string; reminder_time: string; schedule_type: ReminderScheduleType; day_of_week: number | null; enabled: boolean; status: ReminderStatus; }
export interface TodayNotifications { timezone: string; local_date: string; reminders: TodayReminder[]; }
