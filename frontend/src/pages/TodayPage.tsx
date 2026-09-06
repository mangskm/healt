import { useEffect, useState } from "react";
import { ApiStatus } from "../features/health/ApiStatus";
import { Link } from "react-router-dom";
import { Dashboard, getDashboard } from "../services/api";

export function TodayPage() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null); const [error, setError] = useState(false);
  useEffect(() => { void getDashboard().then(setDashboard).catch(() => setError(true)); }, []);
  return (
    <main className="page-shell">
      <p className="eyebrow">Personal Health Tracking</p>
      <h1>Today</h1>
      <p className="intro">A direct overview of your tracked information for today.</p>
      <div className="quick-actions"><Link className="button-link" to="/weight">Add Weight</Link><Link className="button-link secondary-button" to="/meals">Add Meal</Link><Link className="button-link secondary-button" to="/exercise">Add Exercise</Link><Link className="button-link secondary-button" to="/goals">Manage Goals</Link></div>
      {error && <p role="alert">Dashboard could not be loaded. Your tracking pages are still available above.</p>}
      {!dashboard && !error && <p>Loading dashboard…</p>}
      {dashboard && <section className="dashboard-grid">
        <article className="status-card"><h2>{dashboard.profile?.preferred_name ? `${dashboard.profile.preferred_name}'s summary` : "Profile"}</h2><p>{dashboard.profile ? `Timezone: ${dashboard.timezone}` : "Profile not configured. Dates use UTC until you add a timezone."}</p></article>
        <article className="status-card"><h2>Latest weight</h2>{dashboard.latest_weight ? <p className="latest-weight">{dashboard.latest_weight.weight_kg} kg</p> : <p>No weight records yet.</p>}</article>
        <article className="status-card"><h2>Active goals</h2>{dashboard.active_goals.length ? dashboard.active_goals.map((goal) => <p key={goal.id}>{goal.target_value_kg} kg{goal.target_date ? ` · ${goal.target_date}` : ""}</p>) : <p>No active goals.</p>}</article>
        <article className="status-card"><h2>Meals today</h2>{dashboard.meals.count ? <><p>{dashboard.meals.count} meals · {dashboard.meals.item_count} items</p><p>Entered nutrition: {dashboard.meals.calories_kcal} kcal · {dashboard.meals.protein_g} g protein</p>{dashboard.meals.nutrition_missing_item_count > 0 && <p>Some food items have missing nutrition values.</p>}</> : <p>No meals today.</p>}</article>
        <article className="status-card"><h2>Exercise today</h2>{dashboard.exercise.count ? <><p>{dashboard.exercise.count} sessions · {dashboard.exercise.duration_minutes} min</p>{dashboard.exercise.distance_session_count > 0 && <p>{dashboard.exercise.distance_km} km entered distance</p>}{dashboard.exercise.calories_entered_session_count > 0 && <p>{dashboard.exercise.calories_burned_kcal} kcal manually entered</p>}</> : <p>No exercise today.</p>}</article>
      </section>}
      <section className="status-card" aria-labelledby="service-status-title">
        <h2 id="service-status-title">Service status</h2>
        <ApiStatus />
      </section>
      <p className="disclaimer">This application is not a substitute for professional medical advice.</p>
    </main>
  );
}
