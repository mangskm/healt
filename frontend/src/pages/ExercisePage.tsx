import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { createExerciseSession, deleteExerciseSession, listExerciseSessions, updateExerciseSession } from "../services/api";
import type { ActivityType, DistanceUnit, ExerciseInput, ExerciseSession } from "../types/exercise";
import { convertDistance, formatDistance } from "../utils/distanceUnits";
import { useConfirm, useToast } from "../components/UiProviders";

interface Draft { activityType: ActivityType; performedAt: string; duration: string; distance: string; distanceUnit: DistanceUnit; calories: string; note: string; }
const localDateTime = (date = new Date()) => new Date(date.getTime() - date.getTimezoneOffset() * 60_000).toISOString().slice(0, 16);
const emptyDraft = (): Draft => ({ activityType: "walking", performedAt: localDateTime(), duration: "", distance: "", distanceUnit: "km", calories: "", note: "" });
const numberOrNull = (value: string) => value === "" ? null : Number(value);

export function ExercisePage() {
  const confirm = useConfirm(); const { success } = useToast();
  const [sessions, setSessions] = useState<ExerciseSession[]>([]);
  const [draft, setDraft] = useState<Draft>(emptyDraft);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true); const [saving, setSaving] = useState(false); const [deletingId, setDeletingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null); const [message, setMessage] = useState<string | null>(null);

  useEffect(() => { void listExerciseSessions().then((result) => setSessions(result.items)).catch(() => setError("Exercise sessions could not be loaded.")).finally(() => setLoading(false)); }, []);

  function changeUnit(unit: DistanceUnit) { setDraft((current) => ({ ...current, distanceUnit: unit, distance: current.distance ? convertDistance(Number(current.distance), current.distanceUnit, unit).toFixed(2) : "" })); }
  function validate(): string | null {
    if (!draft.performedAt || new Date(draft.performedAt).getTime() > Date.now()) return "Choose a time that is not in the future.";
    if (!Number.isInteger(Number(draft.duration)) || Number(draft.duration) <= 0) return "Duration must be a whole number greater than zero.";
    if (draft.distance && (!Number.isFinite(Number(draft.distance)) || Number(draft.distance) <= 0)) return "Distance must be greater than zero.";
    if (draft.calories && (!Number.isFinite(Number(draft.calories)) || Number(draft.calories) < 0)) return "Calories burned cannot be negative.";
    return null;
  }
  function payload(): ExerciseInput { return { activity_type: draft.activityType, performed_at: new Date(draft.performedAt).toISOString(), duration_minutes: Number(draft.duration), distance: numberOrNull(draft.distance), distance_unit: draft.distance ? draft.distanceUnit : null, calories_burned_kcal: numberOrNull(draft.calories), note: draft.note.trim() || null }; }
  async function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); const invalid = validate(); if (invalid) { setError(invalid); return; } setSaving(true); setError(null); setMessage(null); try { const saved = editingId ? await updateExerciseSession(editingId, payload()) : await createExerciseSession(payload()); setSessions((current) => [saved, ...current.filter((item) => item.id !== saved.id)]); setDraft(emptyDraft()); setEditingId(null); const feedback = editingId ? "Exercise session updated." : "Exercise session saved."; setMessage(feedback); success(feedback); } catch { setError("Exercise session could not be saved. Check the values and try again."); } finally { setSaving(false); } }
  function edit(session: ExerciseSession) { setEditingId(session.id); setDraft({ activityType: session.activity_type, performedAt: localDateTime(new Date(session.performed_at)), duration: String(session.duration_minutes), distance: session.distance_km === null ? "" : String(convertDistance(session.distance_km, "km", draft.distanceUnit).toFixed(2)), distanceUnit: draft.distanceUnit, calories: session.calories_burned_kcal === null ? "" : String(session.calories_burned_kcal), note: session.note ?? "" }); setError(null); setMessage(null); }
  async function remove(id: string) { if (!await confirm({ title: "Delete exercise session?", description: "This activity record and its note will be removed permanently." })) return; setDeletingId(id); setError(null); try { await deleteExerciseSession(id); setSessions((current) => current.filter((session) => session.id !== id)); setMessage("Exercise session deleted."); success("Exercise session deleted."); } catch { setError("Exercise session could not be deleted. Try again."); } finally { setDeletingId(null); } }

  return <main className="page-shell"><Link className="back-link" to="/">← Today</Link><p className="eyebrow">Personal Health Tracking</p><h1>Exercise</h1><p className="intro">Record an activity session. Calories burned are optional values you enter yourself; this page does not estimate or recommend anything.</p>
    <form className="profile-form" onSubmit={submit} noValidate><h2>{editingId ? "Edit exercise session" : "Add exercise session"}</h2>
      <label>Activity type<select aria-label="Activity type" value={draft.activityType} onChange={(event) => setDraft((current) => ({ ...current, activityType: event.target.value as ActivityType }))}><option value="walking">Walking</option><option value="running">Running</option><option value="cycling">Cycling</option><option value="strength_training">Strength training</option><option value="swimming">Swimming</option><option value="sports">Sports</option><option value="other">Other</option></select></label>
      <label>Performed at<input aria-label="Performed at" type="datetime-local" value={draft.performedAt} onChange={(event) => setDraft((current) => ({ ...current, performedAt: event.target.value }))} /></label>
      <label>Duration (minutes)<input aria-label="Duration" type="number" min="1" step="1" value={draft.duration} onChange={(event) => setDraft((current) => ({ ...current, duration: event.target.value }))} /></label>
      <label>Distance (optional)<input aria-label="Distance" type="number" min="0.001" step="0.001" value={draft.distance} onChange={(event) => setDraft((current) => ({ ...current, distance: event.target.value }))} /></label>
      <label>Distance unit<select aria-label="Distance unit" value={draft.distanceUnit} onChange={(event) => changeUnit(event.target.value as DistanceUnit)}><option value="km">Kilometers (km)</option><option value="mi">Miles (mi)</option></select></label>
      <label>Calories burned (optional)<input aria-label="Calories burned" type="number" min="0" step="0.001" value={draft.calories} onChange={(event) => setDraft((current) => ({ ...current, calories: event.target.value }))} /></label>
      <label>Note (optional)<textarea aria-label="Exercise note" value={draft.note} onChange={(event) => setDraft((current) => ({ ...current, note: event.target.value }))} /></label>
      {error && <p role="alert">{error}</p>}{message && <p aria-live="polite">{message}</p>}<button disabled={saving} type="submit">{saving ? "Saving…" : editingId ? "Update exercise session" : "Save exercise session"}</button>{editingId && <button className="secondary-button" type="button" onClick={() => { setEditingId(null); setDraft(emptyDraft()); }}>Cancel edit</button>}</form>
    <section className="history-section"><h2>Exercise history</h2>{loading ? <p>Loading exercise sessions…</p> : sessions.length === 0 ? <p>No exercise sessions yet. Add one above.</p> : <ul className="record-list">{sessions.map((session) => <li key={session.id}><div><strong>{session.activity_type} · {session.duration_minutes} min</strong><span>Performed: {new Date(session.performed_at).toLocaleString()}</span>{session.distance_km !== null && <span>Distance: {formatDistance(session.distance_km, draft.distanceUnit)}</span>}{session.calories_burned_kcal !== null && <span>Calories burned: {session.calories_burned_kcal} kcal</span>}{session.note && <span>{session.note}</span>}</div><div className="record-actions"><button className="secondary-button" type="button" onClick={() => edit(session)}>Edit</button><button className="danger-button" disabled={deletingId === session.id} type="button" onClick={() => void remove(session.id)}>{deletingId === session.id ? "Deleting…" : "Delete"}</button></div></li>)}</ul>}</section>
  </main>;
}
