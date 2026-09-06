import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getProfile, updateProfile } from "../services/api";
import type { Profile, ProfileUpdate } from "../types/profile";

interface ProfileDraft {
  preferred_name: string;
  date_of_birth: string;
  sex: string;
  height_cm: string;
  weight_unit: string;
  height_unit: string;
  timezone: string;
}

function defaultDraft(): ProfileDraft {
  return {
    preferred_name: "", date_of_birth: "", sex: "", height_cm: "", weight_unit: "kg", height_unit: "cm",
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "",
  };
}

function toDraft(profile: Profile): ProfileDraft {
  return {
    preferred_name: profile.preferred_name ?? "", date_of_birth: profile.date_of_birth ?? "", sex: profile.sex ?? "",
    height_cm: profile.height_cm?.toString() ?? "", weight_unit: profile.weight_unit ?? "kg",
    height_unit: profile.height_unit ?? "cm", timezone: profile.timezone ?? "",
  };
}

export function ProfilePage() {
  const [draft, setDraft] = useState<ProfileDraft>(defaultDraft);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void getProfile().then((profile) => {
      if (profile) setDraft(toDraft(profile));
    }).catch(() => setError("Your profile could not be loaded.")).finally(() => setIsLoading(false));
  }, []);

  function updateField(field: keyof ProfileDraft, value: string) {
    setDraft((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setMessage(null);
    setError(null);
    const payload: ProfileUpdate = {
      preferred_name: draft.preferred_name.trim() || null,
      date_of_birth: draft.date_of_birth || null,
      sex: (draft.sex || null) as ProfileUpdate["sex"],
      height_cm: draft.height_cm === "" ? null : Number(draft.height_cm),
      weight_unit: (draft.weight_unit || null) as ProfileUpdate["weight_unit"],
      height_unit: (draft.height_unit || null) as ProfileUpdate["height_unit"],
      timezone: draft.timezone.trim() || null,
    };
    try {
      const profile = await updateProfile(payload);
      setDraft(toDraft(profile));
      setMessage("Profile saved.");
    } catch {
      setError("Your profile could not be saved. Check the values and try again.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="page-shell">
      <Link className="back-link" to="/">← Today</Link>
      <p className="eyebrow">Personal Health Tracking</p>
      <h1>Profile</h1>
      <p className="intro">Set the optional basics that will help tailor future tracking views and units.</p>
      <p className="disclaimer">This information supports tracking only; it is not used for diagnosis or treatment.</p>
      {isLoading ? <p aria-live="polite">Loading profile…</p> : (
        <form className="profile-form" onSubmit={handleSubmit}>
          <label>Display name<input value={draft.preferred_name} maxLength={80} onChange={(event) => updateField("preferred_name", event.target.value)} /></label>
          <label>Date of birth<input type="date" value={draft.date_of_birth} onChange={(event) => updateField("date_of_birth", event.target.value)} /></label>
          <label>Sex<select value={draft.sex} onChange={(event) => updateField("sex", event.target.value)}><option value="">Prefer not to specify</option><option value="female">Female</option><option value="male">Male</option><option value="intersex">Intersex</option><option value="prefer_not_to_say">Prefer not to say</option></select></label>
          <label>Height (cm)<input type="number" min="50" max="300" step="0.1" value={draft.height_cm} onChange={(event) => updateField("height_cm", event.target.value)} /></label>
          <label>Preferred weight unit<select value={draft.weight_unit} onChange={(event) => updateField("weight_unit", event.target.value)}><option value="kg">Kilograms (kg)</option><option value="lb">Pounds (lb)</option></select></label>
          <label>Preferred height unit<select value={draft.height_unit} onChange={(event) => updateField("height_unit", event.target.value)}><option value="cm">Centimeters (cm)</option><option value="ft_in">Feet and inches</option></select></label>
          <label>Timezone<input value={draft.timezone} maxLength={64} placeholder="Asia/Bangkok" onChange={(event) => updateField("timezone", event.target.value)} /></label>
          {error && <p role="alert">{error}</p>}
          {message && <p aria-live="polite">{message}</p>}
          <button type="submit" disabled={isSaving}>{isSaving ? "Saving…" : "Save profile"}</button>
        </form>
      )}
    </main>
  );
}
