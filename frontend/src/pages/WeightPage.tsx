import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { createWeightRecord, deleteWeightRecord, getProfile, listWeightRecords, updateWeightRecord } from "../services/api";
import type { WeightUnit } from "../types/profile";
import type { WeightRecord, WeightRecordInput } from "../types/weight";
import { convertWeight, formatWeight } from "../utils/weightUnits";
import { useConfirm, useToast } from "../components/UiProviders";

interface WeightDraft {
  weight: string;
  unit: WeightUnit;
  recordedAt: string;
  note: string;
}

function toLocalDateTimeInput(isoDate: string): string {
  const date = new Date(isoDate);
  const offsetDate = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
  return offsetDate.toISOString().slice(0, 16);
}

function defaultDraft(unit: WeightUnit = "kg"): WeightDraft {
  return { weight: "", unit, recordedAt: toLocalDateTimeInput(new Date().toISOString()), note: "" };
}

function sortByRecordedAt(records: WeightRecord[]): WeightRecord[] {
  return [...records].sort((left, right) => new Date(right.recorded_at).getTime() - new Date(left.recorded_at).getTime());
}

export function WeightPage() {
  const confirm = useConfirm(); const { success } = useToast();
  const [records, setRecords] = useState<WeightRecord[]>([]);
  const [latest, setLatest] = useState<WeightRecord | null>(null);
  const [draft, setDraft] = useState<WeightDraft>(defaultDraft);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void Promise.all([getProfile(), listWeightRecords()])
      .then(([profile, history]) => {
        const unit = profile?.weight_unit ?? "kg";
        setDraft(defaultDraft(unit));
        setRecords(history.items);
        setLatest(history.latest);
      })
      .catch(() => setError("Weight records could not be loaded."))
      .finally(() => setIsLoading(false));
  }, []);

  function updateField(field: keyof WeightDraft, value: string) {
    setDraft((current) => ({ ...current, [field]: value }));
  }

  function changeUnit(nextUnit: WeightUnit) {
    setDraft((current) => ({
      ...current,
      unit: nextUnit,
      weight: current.weight === "" ? "" : convertWeight(Number(current.weight), current.unit, nextUnit).toFixed(2),
    }));
  }

  function applySavedRecord(record: WeightRecord) {
    setRecords((current) => {
      const next = sortByRecordedAt([record, ...current.filter((item) => item.id !== record.id)]);
      setLatest(next[0] ?? null);
      return next;
    });
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const weight = Number(draft.weight);
    if (!Number.isFinite(weight) || weight <= 0) {
      setError("Enter a weight greater than zero.");
      return;
    }
    if (!draft.recordedAt || new Date(draft.recordedAt).getTime() > Date.now()) {
      setError("Enter a measurement date and time that is not in the future.");
      return;
    }
    setIsSaving(true);
    setMessage(null);
    setError(null);
    const payload: WeightRecordInput = {
      weight,
      unit: draft.unit,
      recorded_at: new Date(draft.recordedAt).toISOString(),
      note: draft.note.trim() || null,
    };
    try {
      const record = editingId ? await updateWeightRecord(editingId, payload) : await createWeightRecord(payload);
      applySavedRecord(record);
      setDraft(defaultDraft(draft.unit));
      setEditingId(null);
      const feedback = editingId ? "Weight record updated." : "Weight record saved."; setMessage(feedback); success(feedback);
    } catch {
      setError("Weight record could not be saved. Check the values and try again.");
    } finally {
      setIsSaving(false);
    }
  }

  function beginEdit(record: WeightRecord) {
    setEditingId(record.id);
    setDraft({
      weight: convertWeight(record.weight_kg, "kg", draft.unit).toFixed(2),
      unit: draft.unit,
      recordedAt: toLocalDateTimeInput(record.recorded_at),
      note: record.note ?? "",
    });
    setMessage(null);
    setError(null);
  }

  async function removeRecord(id: string) {
    if (!await confirm({ title: "Delete weight record?", description: "This measurement and its note will be removed permanently." })) return;
    setDeletingId(id);
    setError(null);
    try {
      await deleteWeightRecord(id);
      setRecords((current) => {
        const next = current.filter((record) => record.id !== id);
        setLatest(next[0] ?? null);
        return next;
      });
      if (editingId === id) {
        setEditingId(null);
        setDraft(defaultDraft(draft.unit));
      }
      setMessage("Weight record deleted."); success("Weight record deleted.");
    } catch {
      setError("Weight record could not be deleted. Try again.");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <main className="page-shell">
      <Link className="back-link" to="/">← Today</Link>
      <p className="eyebrow">Personal Health Tracking</p>
      <h1>Weight</h1>
      <p className="intro">Record measurements over time. This page tracks data only and does not give weight-loss or medical advice.</p>
      {latest && <section className="status-card" aria-labelledby="latest-weight-title"><h2 id="latest-weight-title">Latest measurement</h2><p className="latest-weight">{formatWeight(latest.weight_kg, draft.unit)}</p><p>{new Date(latest.recorded_at).toLocaleString()}</p></section>}
      {isLoading ? <p aria-live="polite">Loading weight records…</p> : (
        <>
          <form className="profile-form" onSubmit={handleSubmit} noValidate>
            <h2>{editingId ? "Edit measurement" : "Add measurement"}</h2>
            <label>Weight<input aria-label="Weight" type="number" min="0.001" step="0.01" value={draft.weight} onChange={(event) => updateField("weight", event.target.value)} /></label>
            <label>Unit<select value={draft.unit} onChange={(event) => changeUnit(event.target.value as WeightUnit)}><option value="kg">Kilograms (kg)</option><option value="lb">Pounds (lb)</option></select></label>
            <label>Measurement date and time<input aria-label="Measurement date and time" type="datetime-local" value={draft.recordedAt} onChange={(event) => updateField("recordedAt", event.target.value)} /></label>
            <label>Note (optional)<textarea value={draft.note} maxLength={500} onChange={(event) => updateField("note", event.target.value)} /></label>
            {error && <p role="alert">{error}</p>}
            {message && <p aria-live="polite">{message}</p>}
            <button type="submit" disabled={isSaving}>{isSaving ? "Saving…" : editingId ? "Update record" : "Save record"}</button>
            {editingId && <button className="secondary-button" type="button" onClick={() => { setEditingId(null); setDraft(defaultDraft(draft.unit)); }}>Cancel edit</button>}
          </form>
          <section className="history-section" aria-labelledby="weight-history-title">
            <h2 id="weight-history-title">Previous measurements</h2>
            {records.length === 0 ? <p>No weight records yet. Add your first measurement above.</p> : <ul className="record-list">{records.map((record) => (
              <li key={record.id}><div><strong>{formatWeight(record.weight_kg, draft.unit)}</strong><span>{new Date(record.recorded_at).toLocaleString()}</span>{record.note && <span>{record.note}</span>}</div><div className="record-actions"><button className="secondary-button" type="button" onClick={() => beginEdit(record)}>Edit</button><button className="danger-button" type="button" disabled={deletingId === record.id} onClick={() => void removeRecord(record.id)}>{deletingId === record.id ? "Deleting…" : "Delete"}</button></div></li>
            ))}</ul>}
          </section>
        </>
      )}
    </main>
  );
}
