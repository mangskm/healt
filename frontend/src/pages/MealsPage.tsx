import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { createMeal, createMealItem, deleteMeal, deleteMealItem, getMeal, listMeals, updateMeal, updateMealItem } from "../services/api";
import type { FoodUnit, Meal, MealItemInput, MealType } from "../types/meal";
import { calculateMealTotals } from "../utils/mealTotals";
import { useConfirm, useToast } from "../components/UiProviders";

interface ItemDraft {
  existingId?: string;
  foodName: string;
  quantity: string;
  unit: FoodUnit;
  calories: string;
  protein: string;
  carbohydrates: string;
  fat: string;
}

interface MealDraft { mealType: MealType; eatenAt: string; note: string; items: ItemDraft[]; }

function localDateTimeValue(value = new Date()): string {
  const offset = value.getTimezoneOffset() * 60_000;
  return new Date(value.getTime() - offset).toISOString().slice(0, 16);
}

function emptyItem(): ItemDraft {
  return { foodName: "", quantity: "", unit: "g", calories: "", protein: "", carbohydrates: "", fat: "" };
}

function initialDraft(): MealDraft {
  return { mealType: "breakfast", eatenAt: localDateTimeValue(), note: "", items: [emptyItem()] };
}

function toDraft(meal: Meal): MealDraft {
  return {
    mealType: meal.meal_type,
    eatenAt: localDateTimeValue(new Date(meal.eaten_at)),
    note: meal.note ?? "",
    items: meal.items.map((item) => ({ existingId: item.id, foodName: item.food_name, quantity: String(item.quantity), unit: item.unit, calories: item.calories_kcal === null ? "" : String(item.calories_kcal), protein: item.protein_g === null ? "" : String(item.protein_g), carbohydrates: item.carbohydrates_g === null ? "" : String(item.carbohydrates_g), fat: item.fat_g === null ? "" : String(item.fat_g) })),
  };
}

function numberOrNull(value: string): number | null {
  return value === "" ? null : Number(value);
}

function toItemPayload(item: ItemDraft): MealItemInput {
  return { food_name: item.foodName.trim(), quantity: Number(item.quantity), unit: item.unit, calories_kcal: numberOrNull(item.calories), protein_g: numberOrNull(item.protein), carbohydrates_g: numberOrNull(item.carbohydrates), fat_g: numberOrNull(item.fat) };
}

export function MealsPage() {
  const confirm = useConfirm(); const { success } = useToast();
  const [meals, setMeals] = useState<Meal[]>([]);
  const [draft, setDraft] = useState<MealDraft>(initialDraft);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [removedItemIds, setRemovedItemIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void listMeals().then((result) => setMeals(result.items)).catch(() => setError("Meals could not be loaded.")).finally(() => setLoading(false));
  }, []);

  function updateItem(index: number, field: keyof ItemDraft, value: string) {
    setDraft((current) => ({ ...current, items: current.items.map((item, itemIndex) => itemIndex === index ? { ...item, [field]: value } : item) }));
  }

  function validateDraft(): string | null {
    if (!draft.eatenAt || new Date(draft.eatenAt).getTime() > Date.now()) return "Choose a meal time that is not in the future.";
    if (draft.items.length === 0) return "Add at least one food item.";
    for (const item of draft.items) {
      if (!item.foodName.trim()) return "Each food item needs a name.";
      if (!Number.isFinite(Number(item.quantity)) || Number(item.quantity) <= 0) return "Each quantity must be greater than zero.";
      for (const value of [item.calories, item.protein, item.carbohydrates, item.fat]) {
        if (value !== "" && (!Number.isFinite(Number(value)) || Number(value) < 0)) return "Nutrition values cannot be negative.";
      }
    }
    return null;
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const validationError = validateDraft();
    if (validationError) { setError(validationError); return; }
    setSaving(true); setError(null); setMessage(null);
    const mealPayload = { meal_type: draft.mealType, eaten_at: new Date(draft.eatenAt).toISOString(), note: draft.note.trim() || null };
    try {
      const savedMeal = editingId ? await updateMeal(editingId, mealPayload) : await createMeal(mealPayload);
      await Promise.all(draft.items.map((item) => item.existingId ? updateMealItem(savedMeal.id, item.existingId, toItemPayload(item)) : createMealItem(savedMeal.id, toItemPayload(item))));
      await Promise.all(removedItemIds.map((itemId) => deleteMealItem(savedMeal.id, itemId)));
      const meal = await getMeal(savedMeal.id);
      setMeals((current) => [meal, ...current.filter((item) => item.id !== meal.id)]);
      setDraft(initialDraft()); setEditingId(null); setRemovedItemIds([]); const feedback = editingId ? "Meal updated." : "Meal saved."; setMessage(feedback); success(feedback);
    } catch { setError("Meal could not be saved. Check the values and try again."); }
    finally { setSaving(false); }
  }

  function edit(meal: Meal) {
    setDraft(toDraft(meal)); setEditingId(meal.id); setRemovedItemIds([]); setError(null); setMessage(null);
  }

  async function removeItem(index: number) {
    if (!await confirm({ title: "Remove food item?", description: "This item will be removed when you save the meal.", confirmLabel: "Remove" })) return;
    setDraft((current) => {
      const item = current.items[index];
      if (item.existingId) setRemovedItemIds((ids) => [...ids, item.existingId!]);
      return { ...current, items: current.items.filter((_, itemIndex) => itemIndex !== index) };
    });
  }

  async function removeMeal(id: string) {
    if (!await confirm({ title: "Delete meal?", description: "This meal and all of its food items will be removed permanently." })) return;
    setDeletingId(id); setError(null);
    try { await deleteMeal(id); setMeals((current) => current.filter((meal) => meal.id !== id)); setMessage("Meal deleted."); success("Meal deleted."); }
    catch { setError("Meal could not be deleted. Try again."); }
    finally { setDeletingId(null); }
  }

  return <main className="page-shell">
    <Link className="back-link" to="/">← Today</Link><p className="eyebrow">Personal Health Tracking</p><h1>Meals</h1>
    <p className="intro">Record meals and the food items you entered. Nutrition values are optional tracking details, not targets or recommendations.</p>
    <form className="profile-form meal-form" onSubmit={submit} noValidate>
      <h2>{editingId ? "Edit meal" : "Add meal"}</h2>
      <label>Meal type<select aria-label="Meal type" value={draft.mealType} onChange={(event) => setDraft((current) => ({ ...current, mealType: event.target.value as MealType }))}><option value="breakfast">Breakfast</option><option value="lunch">Lunch</option><option value="dinner">Dinner</option><option value="snack">Snack</option><option value="other">Other</option></select></label>
      <label>Eaten at<input aria-label="Eaten at" type="datetime-local" value={draft.eatenAt} onChange={(event) => setDraft((current) => ({ ...current, eatenAt: event.target.value }))} /></label>
      <label>Note (optional)<textarea aria-label="Meal note" value={draft.note} onChange={(event) => setDraft((current) => ({ ...current, note: event.target.value }))} /></label>
      <fieldset className="meal-items"><legend>Food items</legend>{draft.items.map((item, index) => <div className="meal-item-form" key={item.existingId ?? index}>
        <label>Food name<input aria-label={`Food name ${index + 1}`} value={item.foodName} onChange={(event) => updateItem(index, "foodName", event.target.value)} /></label>
        <label>Quantity<input aria-label={`Quantity ${index + 1}`} type="number" min="0.001" step="0.001" value={item.quantity} onChange={(event) => updateItem(index, "quantity", event.target.value)} /></label>
        <label>Unit<select aria-label={`Unit ${index + 1}`} value={item.unit} onChange={(event) => updateItem(index, "unit", event.target.value)}><option value="g">g</option><option value="ml">ml</option><option value="serving">serving</option><option value="piece">piece</option></select></label>
        <label>Calories (optional)<input aria-label={`Calories ${index + 1}`} type="number" min="0" step="0.001" value={item.calories} onChange={(event) => updateItem(index, "calories", event.target.value)} /></label>
        <label>Protein g (optional)<input aria-label={`Protein ${index + 1}`} type="number" min="0" step="0.001" value={item.protein} onChange={(event) => updateItem(index, "protein", event.target.value)} /></label>
        <label>Carbohydrates g (optional)<input aria-label={`Carbohydrates ${index + 1}`} type="number" min="0" step="0.001" value={item.carbohydrates} onChange={(event) => updateItem(index, "carbohydrates", event.target.value)} /></label>
        <label>Fat g (optional)<input aria-label={`Fat ${index + 1}`} type="number" min="0" step="0.001" value={item.fat} onChange={(event) => updateItem(index, "fat", event.target.value)} /></label>
        <button className="secondary-button" type="button" onClick={() => void removeItem(index)}>Remove item</button>
      </div>)}</fieldset>
      <button className="secondary-button" type="button" onClick={() => setDraft((current) => ({ ...current, items: [...current.items, emptyItem()] }))}>Add food item</button>
      {error && <p role="alert">{error}</p>}{message && <p aria-live="polite">{message}</p>}<button disabled={saving} type="submit">{saving ? "Saving…" : editingId ? "Update meal" : "Save meal"}</button>
      {editingId && <button className="secondary-button" type="button" onClick={() => { setDraft(initialDraft()); setEditingId(null); setRemovedItemIds([]); }}>Cancel edit</button>}
    </form>
    <section className="history-section"><h2>Meal history</h2>{loading ? <p>Loading meals…</p> : meals.length === 0 ? <p>No meals yet. Add a meal above.</p> : <ul className="record-list meal-list">{meals.map((meal) => {
      const totals = calculateMealTotals(meal.items); const hasNutrition = meal.items.some((item) => item.calories_kcal !== null || item.protein_g !== null || item.carbohydrates_g !== null || item.fat_g !== null);
      return <li key={meal.id}><div><strong>{meal.meal_type} · {new Date(meal.eaten_at).toLocaleString()}</strong>{meal.note && <span>{meal.note}</span>}<span>{meal.items.map((item) => `${item.food_name} (${item.quantity} ${item.unit})`).join(", ")}</span>{hasNutrition && <span>Calories: {totals.calories_kcal} kcal · Protein: {totals.protein_g} g · Carbohydrates: {totals.carbohydrates_g} g · Fat: {totals.fat_g} g</span>}</div><div className="record-actions"><button className="secondary-button" type="button" onClick={() => edit(meal)}>Edit</button><button className="danger-button" disabled={deletingId === meal.id} type="button" onClick={() => void removeMeal(meal.id)}>{deletingId === meal.id ? "Deleting…" : "Delete"}</button></div></li>;
    })}</ul>}</section>
  </main>;
}
