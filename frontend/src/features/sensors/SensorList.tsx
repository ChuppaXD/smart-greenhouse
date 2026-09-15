import { useEffect, useState } from "react";
import {
  createSensor,
  fetchSensors,
  type SensorDto,
} from "../../services/api";


export default function SensorList() {
  const [sensors, setSensors] = useState<SensorDto[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState<"moisture" | "light" | null>(null);
  const [error, setError] = useState<string | null>(null);


  async function loadSensors() {
    try {
      setError(null);
      setLoading(true);

      const data = await fetchSensors();

      setSensors(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load sensors.",
      );
    } finally {
      setLoading(false);
    }
  }


  async function handleCreate(type: "moisture" | "light") {
    try {
      setCreating(type);
      setError(null);

      const created = await createSensor(type);

      setSensors((current) => [created, ...current]);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to create sensor.",
      );
    } finally {
      setCreating(null);
    }
  }


  useEffect(() => {
    void loadSensors();
  }, []);


  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => void handleCreate("moisture")}
          disabled={creating !== null}
          className="rounded-lg bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {creating === "moisture"
            ? "Adding moisture..."
            : "Add moisture sensor"}
        </button>

        <button
          type="button"
          onClick={() => void handleCreate("light")}
          disabled={creating !== null}
          className="rounded-lg bg-sky-600 px-4 py-2 font-medium text-white hover:bg-sky-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {creating === "light"
            ? "Adding light..."
            : "Add light sensor"}
        </button>
      </div>


      {loading && (
        <p className="text-sm text-slate-500">
          Loading sensors...
        </p>
      )}


      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}


      {!loading && !error && sensors.length === 0 && (
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-6 text-sm text-slate-600">
          No sensors yet. Add a moisture or light sensor to get started.
        </div>
      )}


      {!loading && sensors.length > 0 && (
        <div className="space-y-4">
          {sensors.map((sensor) => (
            <article
              key={sensor.id}
              className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
            >
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <h3 className="font-semibold text-slate-900">
                    {sensor.display_name}
                  </h3>

                  <p className="mt-1 text-sm text-slate-500">
                    {sensor.device_type}
                  </p>
                </div>

                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                  sensor
                </span>
              </div>

              <div className="mt-4">
                <h4 className="text-sm font-medium text-slate-700">
                  Default configuration
                </h4>

                <pre className="mt-2 overflow-x-auto rounded-md bg-slate-900 p-4 text-xs text-white">
                  {JSON.stringify(sensor.default_config, null, 2)}
                </pre>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}