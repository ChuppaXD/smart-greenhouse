import { useEffect, useState } from "react";

import {
  createSensor,
  fetchLatestReading,
  fetchSensors,
  readSensor,
  updateDeviceSampling,
  type ReadingDto,
  type SensorDto,
} from "../../services/api";


type SensorCardProps = {
  sensor: SensorDto;
  onSamplingUpdated: (
    sensorId: string,
    interval: number,
    tracking: boolean,
  ) => void;
};


function SensorCard({
  sensor,
  onSamplingUpdated,
}: SensorCardProps) {
  const [latest, setLatest] =
    useState<ReadingDto | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [reading, setReading] =
    useState(false);

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const [interval, setIntervalValue] =
    useState(
      String(
        sensor.sampling_interval_seconds
      )
    );

  const [tracking, setTracking] =
    useState(
      sensor.tracking_enabled
    );


  async function handleReadNow() {
    try {
      setError(null);
      setReading(true);

      const result =
        await readSensor(sensor.id);

      setLatest(result);

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to read sensor."
      );

    } finally {
      setReading(false);
    }
  }


  async function handleSaveSampling() {
    const seconds =
      Number(interval);

    if (
      !Number.isInteger(seconds) ||
      seconds < 5
    ) {
      setError(
        "Sampling interval must be at least 5 seconds."
      );
      return;
    }

    try {
      setError(null);
      setSaving(true);

      const result =
        await updateDeviceSampling(
          sensor.id,
          {
            sampling_interval_seconds:
              seconds,
            tracking_enabled:
              tracking,
          },
        );

      setIntervalValue(
        String(
          result.sampling_interval_seconds
        )
      );

      setTracking(
        result.tracking_enabled
      );

      onSamplingUpdated(
        sensor.id,
        result.sampling_interval_seconds,
        result.tracking_enabled,
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to update sampling."
      );

    } finally {
      setSaving(false);
    }
  }


  useEffect(() => {
    let active = true;

    async function loadLatest() {
      try {
        const result =
          await fetchLatestReading(
            sensor.id
          );

        if (active) {
          setLatest(result);
          setLoading(false);
          setError(null);
        }

      } catch (err) {
        if (active) {
          setError(
            err instanceof Error
              ? err.message
              : "Failed to load latest reading."
          );

          setLoading(false);
        }
      }
    }

    void loadLatest();

    // Temporary Phase 5 polling.
    // Phase 12 replaces this with WebSocket updates.
    const timer =
      window.setInterval(
        () => {
          void loadLatest();
        },
        3000,
      );

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, [sensor.id]);


  return (
    <article className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
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
          {latest?.source ?? "no reading"}
        </span>
      </div>


      <div className="mt-5 rounded-lg bg-slate-50 p-4">
        <p className="text-sm font-medium text-slate-600">
          Latest stored reading
        </p>

        {loading ? (
          <p className="mt-2 text-sm text-slate-500">
            Loading...
          </p>
        ) : latest ? (
          <div className="mt-2">
            <p className="text-3xl font-bold text-slate-900">
              {latest.value} {latest.unit}
            </p>

            <p className="mt-1 text-xs text-slate-500">
              Stored at{" "}
              {new Date(
                latest.recorded_at,
              ).toLocaleString()}
            </p>
          </div>
        ) : (
          <p className="mt-2 text-sm text-slate-500">
            No reading stored yet.
          </p>
        )}
      </div>


      <div className="mt-4">
        <button
          type="button"
          onClick={() =>
            void handleReadNow()
          }
          disabled={reading}
          className="rounded-lg bg-slate-900 px-4 py-2 font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {reading
            ? "Reading..."
            : "Read now"}
        </button>
      </div>


      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <label className="grid gap-1">
          <span className="text-sm font-medium text-slate-700">
            Sampling interval (seconds)
          </span>

          <input
            type="number"
            min={5}
            value={interval}
            onChange={(event) =>
              setIntervalValue(
                event.target.value
              )
            }
            className="rounded-lg border border-slate-300 px-3 py-2"
          />
        </label>


        <label className="flex items-center gap-2 self-end pb-2">
          <input
            type="checkbox"
            checked={tracking}
            onChange={(event) =>
              setTracking(
                event.target.checked
              )
            }
          />

          <span className="text-sm font-medium text-slate-700">
            Tracking enabled
          </span>
        </label>
      </div>


      <div className="mt-4">
        <button
          type="button"
          onClick={() =>
            void handleSaveSampling()
          }
          disabled={saving}
          className="rounded-lg border border-slate-300 px-4 py-2 font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {saving
            ? "Saving..."
            : "Save sampling"}
        </button>
      </div>


      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}


      <div className="mt-5">
        <h4 className="text-sm font-medium text-slate-700">
          Default configuration
        </h4>

        <pre className="mt-2 overflow-x-auto rounded-md bg-slate-900 p-4 text-xs text-white">
          {JSON.stringify(
            sensor.default_config,
            null,
            2,
          )}
        </pre>
      </div>
    </article>
  );
}


export default function SensorList() {
  const [sensors, setSensors] =
    useState<SensorDto[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [creating, setCreating] =
    useState<
      "moisture" | "light" | null
    >(null);

  const [error, setError] =
    useState<string | null>(null);


  async function loadSensors() {
    try {
      setError(null);
      setLoading(true);

      const data =
        await fetchSensors();

      setSensors(data);

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load sensors."
      );

    } finally {
      setLoading(false);
    }
  }


  async function handleCreate(
    type: "moisture" | "light",
  ) {
    try {
      setCreating(type);
      setError(null);

      const created =
        await createSensor(type);

      setSensors(
        (current) => [
          created,
          ...current,
        ],
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to create sensor."
      );

    } finally {
      setCreating(null);
    }
  }


  function handleSamplingUpdated(
    sensorId: string,
    intervalValue: number,
    trackingValue: boolean,
  ) {
    setSensors(
      (current) =>
        current.map(
          (sensor) =>
            sensor.id === sensorId
              ? {
                  ...sensor,
                  sampling_interval_seconds:
                    intervalValue,
                  tracking_enabled:
                    trackingValue,
                }
              : sensor,
        ),
    );
  }


  useEffect(() => {
    void loadSensors();
  }, []);


  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() =>
            void handleCreate(
              "moisture"
            )
          }
          disabled={
            creating !== null
          }
          className="rounded-lg bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {creating === "moisture"
            ? "Adding moisture..."
            : "Add moisture sensor"}
        </button>


        <button
          type="button"
          onClick={() =>
            void handleCreate(
              "light"
            )
          }
          disabled={
            creating !== null
          }
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


      {!loading &&
        !error &&
        sensors.length === 0 && (
          <div className="rounded-lg border border-slate-200 bg-slate-50 p-6 text-sm text-slate-600">
            No sensors yet. Add a moisture or light sensor to get started.
          </div>
        )}


      {!loading &&
        sensors.length > 0 && (
          <div className="space-y-4">
            {sensors.map(
              (sensor) => (
                <SensorCard
                  key={sensor.id}
                  sensor={sensor}
                  onSamplingUpdated={
                    handleSamplingUpdated
                  }
                />
              ),
            )}
          </div>
        )}
    </div>
  );
}