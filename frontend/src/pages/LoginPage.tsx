import { FormEvent, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { ApiError } from "../services/api";
import { useAuth } from "../features/auth/AuthContext";

export function LoginPage() {
  const { state, login } = useAuth(); const navigate = useNavigate(); const location = useLocation();
  const [email, setEmail] = useState(""); const [password, setPassword] = useState(""); const [visible, setVisible] = useState(false); const [error, setError] = useState<string | null>(null); const [submitting, setSubmitting] = useState(false);
  const destination = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname ?? "/";
  if (state === "authenticated") return <Navigate to={destination} replace />;
  async function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); setError(null); setSubmitting(true); try { await login(email, password); navigate(destination, { replace: true }); } catch (cause) { setError(cause instanceof ApiError ? cause.message : "Login is unavailable. Please try again."); } finally { setSubmitting(false); } }
  return <main className="login-page"><section className="login-card"><div className="brand login-brand"><span className="brand-mark" aria-hidden="true">+</span><span>Daily Well</span></div><p className="eyebrow">Welcome back</p><h1 aria-label="Sign in">Sign in to your tracking space</h1><p className="intro">Your records stay connected to your secure account.</p><form className="profile-form login-form" onSubmit={submit}><label>Email<input type="email" value={email} autoComplete="email" onChange={(event) => setEmail(event.target.value)} required /></label><label>Password<div className="password-field"><input type={visible ? "text" : "password"} value={password} autoComplete="current-password" onChange={(event) => setPassword(event.target.value)} required /><button className="text-button" type="button" onClick={() => setVisible((current) => !current)} aria-label={visible ? "Hide password" : "Show password"}>{visible ? "Hide" : "Show"}</button></div></label>{error && <p className="alert alert-error" role="alert">{error}</p>}<button className="button" type="submit" disabled={submitting}>{submitting ? "Signing in…" : "Sign in"}</button></form><p className="muted-note">This application does not provide medical advice.</p></section></main>;
}
