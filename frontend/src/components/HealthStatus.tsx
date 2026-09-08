import { useEffect, useState } from "react";
import { fetchHealth } from "../services/api";

type State = "checking" | "healthy" | "degraded" | "error";

export default function HealthStatus() {
  const [state, setState] = useState<State>("checking");

  useEffect(() => {
    fetchHealth()
      .then((data) => {
        setState(data.status === "ok" && data.db === "ok" ? "healthy" : "degraded");
      })
      .catch(() => {
        setState("error");
      });
  }, []);

  if (state === "checking") {
    return (
      <span className="rounded-full border border-amber-300 px-3 py-1 text-sm text-amber-700">
        Checking…
      </span>
    );
  }

  if (state === "error") {
    return (
      <span className="rounded-full border border-red-300 px-3 py-1 text-sm text-red-700">
        API: unreachable
      </span>
    );
  }

  if (state === "degraded") {
    return (
      <span className="rounded-full border border-amber-300 px-3 py-1 text-sm text-amber-700">
        API: ok · DB: fail
      </span>
    );
  }

  return (
    <span className="rounded-full border border-emerald-300 px-3 py-1 text-sm text-emerald-700">
      API: ok · DB: ok
    </span>
  );
}