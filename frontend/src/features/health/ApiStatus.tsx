import { useEffect, useState } from "react";

import { getHealth } from "../../services/api";
import type { HealthStatus } from "../../types/health";

type Status = "loading" | "connected" | "unavailable";

export function ApiStatus() {
  const [status, setStatus] = useState<Status>("loading");
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    void getHealth()
      .then((result) => {
        setHealth(result);
        setStatus("connected");
      })
      .catch(() => setStatus("unavailable"));
  }, []);

  if (status === "loading") {
    return <p aria-live="polite">Checking API connection…</p>;
  }

  if (status === "unavailable") {
    return <p role="alert">API is unavailable. Start the backend service and try again.</p>;
  }

  return <p aria-live="polite">API connected · Database {health?.database}</p>;
}
