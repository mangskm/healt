import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { createGoal, deleteGoal, getProfile, listGoals, listWeightRecords, updateGoal } from "../services/api";
import type { Goal, GoalStatus } from "../types/goal";
import type { WeightUnit } from "../types/profile";
import { convertWeight, formatWeight } from "../utils/weightUnits";
import { useConfirm, useToast } from "../components/UiProviders";

interface GoalDraft { targetValue: string; unit: WeightUnit; targetDate: string; status: GoalStatus; }
const initialDraft = (unit: WeightUnit = "kg"): GoalDraft => ({ targetValue: "", unit, targetDate: "", status: "active" });

export function GoalsPage() {
  const confirm = useConfirm(); const { success } = useToast();
  const [goals, setGoals] = useState<Goal[]>([]);
  const [latestWeight, setLatestWeight] = useState<number | null>(null);
  const [draft, setDraft] = useState<GoalDraft>(initialDraft);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void Promise.all([getProfile(), listGoals(), listWeightRecords()]).then(([profile, goalList, weights]) => {
      setDraft(initialDraft(profile?.weight_unit ?? "kg"));
      setGoals(goalList.items);
      setLatestWeight(weights.latest?.weight_kg ?? null);
    }).catch(() => setError("Goals could not be loaded.")).finally(() => setLoading(false));
  }, []);

  function changeUnit(unit: WeightUnit) {
    setDraft((current) => ({ ...current, unit, targetValue: current.targetValue ? convertWeight(Number(current.targetValue), current.unit, unit).toFixed(2) : "" }));
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = Number(draft.targetValue);
    if (!Number.isFinite(value) || value <= 0) { setError("Enter a target weight greater than zero."); return; }
    setSaving(true); setError(null); setMessage(null);
    const payload = { target_value: value, unit: draft.unit, target_date: draft.targetDate || null, status: draft.status };
    try {
      const goal = editingId ? await updateGoal(editingId, payload) : await createGoal({ goal_type: "target_weight", ...payload });
      setGoals((current) => [goal, ...current.filter((item) => item.id !== goal.id)]);
      setEditingId(null); setDraft(initialDraft(draft.unit)); const feedback = editingId ? "Goal updated." : "Goal saved."; setMessage(feedback); success(feedback);
    } catch { setError("Goal could not be saved. Check the values and try again."); } finally { setSaving(false); }
  }

  function edit(goal: Goal) {
    setEditingId(goal.id);
    setDraft({ targetValue: convertWeight(goal.target_value_kg, "kg", draft.unit).toFixed(2), unit: draft.unit, targetDate: goal.target_date ?? "", status: goal.status });
    setError(null); setMessage(null);
  }

  async function remove(id: string) {
    if (!await confirm({ title: "Delete goal?", description: "This target will be removed permanently." })) return;
    setDeletingId(id); setError(null);
    try { await deleteGoal(id); setGoals((current) => current.filter((goal) => goal.id !== id)); setMessage("Goal deleted."); success("Goal deleted."); }
    catch { setError("Goal could not be deleted. Try again."); } finally { setDeletingId(null); }
  }

  return <main className="page-shell">
    <Link className="back-link" to="/">← Today</Link><p className="eyebrow">Personal Health Tracking</p><h1>Goals</h1>
    <p className="intro">Set a personal target for tracking. Goals are manual and do not create recommendations.</p>
    {latestWeight !== null && <section className="status-card"><h2>Latest recorded weight</h2><p className="latest-weight">{formatWeight(latestWeight, draft.unit)}</p></section>}
    {loading ? <p>Loading goals…</p> : <><form className="profile-form" onSubmit={submit} noValidate><h2>{editingId ? "Edit goal" : "Add target-weight goal"}</h2>
      <label>Target weight<input aria-label="Target weight" type="number" min="0.001" step="0.01" value={draft.targetValue} onChange={(event) => setDraft((current) => ({ ...current, targetValue: event.target.value }))} /></label>
      <label>Unit<select value={draft.unit} onChange={(event) => changeUnit(event.target.value as WeightUnit)}><option value="kg">Kilograms (kg)</option><option value="lb">Pounds (lb)</option></select></label>
      <label>Target date (optional)<input type="date" value={draft.targetDate} onChange={(event) => setDraft((current) => ({ ...current, targetDate: event.target.value }))} /></label>
      <label>Status<select value={draft.status} onChange={(event) => setDraft((current) => ({ ...current, status: event.target.value as GoalStatus }))}><option value="active">Active</option><option value="completed">Completed</option><option value="cancelled">Cancelled</option></select></label>
      {error && <p role="alert">{error}</p>}{message && <p aria-live="polite">{message}</p>}<button disabled={saving} type="submit">{saving ? "Saving…" : editingId ? "Update goal" : "Save goal"}</button>
      {editingId && <button className="secondary-button" type="button" onClick={() => { setEditingId(null); setDraft(initialDraft(draft.unit)); }}>Cancel edit</button>}</form>
      <section className="history-section"><h2>Goals</h2>{goals.length === 0 ? <p>No goals yet. Add a target-weight goal above.</p> : <ul className="record-list">{goals.map((goal) => <li key={goal.id}><div><strong>Target: {formatWeight(goal.target_value_kg, draft.unit)}</strong><span>Status: {goal.status}</span>{goal.target_date && <span>Target date: {goal.target_date}</span>}</div><div className="record-actions"><button className="secondary-button" onClick={() => edit(goal)} type="button">Edit</button><button className="danger-button" disabled={deletingId === goal.id} onClick={() => void remove(goal.id)} type="button">{deletingId === goal.id ? "Deleting…" : "Delete"}</button></div></li>)}</ul>}</section></>}
  </main>;
}
