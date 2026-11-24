
import { useEffect, useState } from "react";

import {
  fetchAlerts,
  fetchLocationConfig,
  fetchLocations,
  type AlertDto,
  type LocationSummaryDto,
  type ZoneDto,
} from "../../services/api";


function severityStyle(severity: string): string {
  if (severity === "critical") {
    return "bg-red-100 text-red-800";
  }

  if (severity === "warning") {
    return "bg-amber-100 text-amber-800";
  }

  return "bg-sky-100 text-sky-800";
}


export default function EventFeed() {
  const [alerts, setAlerts] = useState<AlertDto[]>([]);
  const [locations, setLocations] = useState<
    LocationSummaryDto[]
  >([]);
  const [zones, setZones] = useState<ZoneDto[]>([]);

  const [locationId, setLocationId] = useState("");
  const [zoneId, setZoneId] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(
    null
  );

  // Load existing Phase 4 locations.
  useEffect(() => {
    let active = true;

    async function loadLocations() {
      try {
        const data = await fetchLocations();

        if (active) {
          setLocations(data);
        }
      } catch (err) {
        if (active) {
          setError(
            err instanceof Error
              ? err.message
              : "Failed to load locations."
          );
        }
      }
    }

    void loadLocations();

    return () => {
      active = false;
    };
  }, []);

  // Load zones belonging to the selected location.
  useEffect(() => {
    let active = true;

    setZones([]);

    if (!locationId) {
      return () => {
        active = false;
      };
    }

    async function loadZones() {
      try {
        const config = await fetchLocationConfig(
          locationId
        );

        if (active) {
          setZones(config.zones);
        }
      } catch (err) {
        if (active) {
          setError(
            err instanceof Error
              ? err.message
              : "Failed to load zones."
          );
        }
      }
    }

    void loadZones();

    return () => {
      active = false;
    };
  }, [locationId]);

  // Poll the persisted alerts every five seconds.
  // Phase 12 will use the realtime.ts interface.
  useEffect(() => {
    let active = true;

    async function loadAlerts() {
      try {
        const data = await fetchAlerts({
          status: "active",
          location_id: locationId || undefined,
          zone_id: zoneId || undefined,
          limit: 50,
        });

        if (active) {
          setAlerts(data);
          setError(null);
        }
      } catch (err) {
        if (active) {
          setError(
            err instanceof Error
              ? err.message
              : "Failed to load alerts."
          );
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    setLoading(true);
    void loadAlerts();

    const interval = window.setInterval(() => {
      void loadAlerts();
    }, 5000);

    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, [locationId, zoneId]);

  return (
    <div className="space-y-5">
      <div>
        <h3 className="text-xl font-semibold text-slate-900">
          Event feed
        </h3>

        <p className="mt-1 text-sm text-slate-500">
          Persisted greenhouse alerts, refreshed
          automatically every 5 seconds.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label
            htmlFor="alert-location"
            className="mb-1 block text-sm font-medium text-slate-700"
          >
            Filter by location
          </label>

          <select
            id="alert-location"
            value={locationId}
            onChange={(event) => {
              setLocationId(event.target.value);
              setZoneId("");
            }}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
          >
            <option value="">
              All locations
            </option>

            {locations.map((location) => (
              <option
                key={location.id}
                value={location.id}
              >
                {location.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label
            htmlFor="alert-zone"
            className="mb-1 block text-sm font-medium text-slate-700"
          >
            Filter by zone
          </label>

          <select
            id="alert-zone"
            value={zoneId}
            onChange={(event) =>
              setZoneId(event.target.value)
            }
            disabled={!locationId}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm disabled:opacity-50"
          >
            <option value="">
              All zones
            </option>

            {zones.map((zone) => (
              <option
                key={zone.id}
                value={zone.id}
              >
                {zone.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <p className="text-sm text-slate-500">
          Loading alerts...
        </p>
      ) : alerts.length === 0 ? (
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-6 text-sm text-slate-600">
          No active alerts for the selected filters.
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert) => (
            <article
              key={alert.id}
              className="rounded-xl border border-slate-200 bg-white p-4"
            >
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span
                    className={
                      `rounded-full px-3 py-1 text-xs font-semibold ${severityStyle(alert.severity)}`
                    }
                  >
                    {alert.severity}
                  </span>

                  <span className="text-xs font-medium text-slate-500">
                    {alert.event_type}
                  </span>
                </div>

                <time className="text-xs text-slate-500">
                  {new Date(
                    alert.created_at
                  ).toLocaleString()}
                </time>
              </div>

              <p className="mt-3 text-sm font-medium text-slate-900">
                {alert.message}
              </p>

              <div className="mt-3 space-y-1 text-xs text-slate-500">
                {alert.location_id && (
                  <p>
                    Location: {alert.location_id}
                  </p>
                )}

                {alert.zone_id && (
                  <p>
                    Zone: {alert.zone_id}
                  </p>
                )}

                {alert.device_id && (
                  <p>
                    Device: {alert.device_id}
                  </p>
                )}

                {!alert.location_id &&
                  !alert.zone_id && (
                    <p>
                      Unassigned device / no location
                    </p>
                  )}
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
