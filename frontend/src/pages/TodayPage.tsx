import { ApiStatus } from "../features/health/ApiStatus";
import { Link } from "react-router-dom";

export function TodayPage() {
  return (
    <main className="page-shell">
      <p className="eyebrow">Personal Health Tracking</p>
      <h1>Today</h1>
      <p className="intro">
        Your tracking dashboard will live here. Phase 0 confirms the application foundation is connected.
      </p>
      <Link className="button-link" to="/profile">Set up profile</Link>
      <Link className="button-link secondary-button" to="/weight">Track weight</Link>
      <Link className="button-link secondary-button" to="/goals">Manage goals</Link>
      <Link className="button-link secondary-button" to="/meals">Track meals</Link>
      <Link className="button-link secondary-button" to="/exercise">Track exercise</Link>
      <section className="status-card" aria-labelledby="service-status-title">
        <h2 id="service-status-title">Service status</h2>
        <ApiStatus />
      </section>
      <p className="disclaimer">This application is not a substitute for professional medical advice.</p>
    </main>
  );
}
