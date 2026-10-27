import { useEffect, useState } from "react";

import {
  fetchLocations,
  type LocationSummaryDto,
} from "../../services/api";

import {
  fetchOverview,
  type LocationOverviewDto,
} from "./api";


type OverviewPanelProps = {
  refreshKey: number;
};


export default function OverviewPanel({
  refreshKey,
}: OverviewPanelProps) {
  const [locations, setLocations] =
    useState<LocationSummaryDto[]>(
      [],
    );

  const [
    selectedLocationId,
    setSelectedLocationId,
  ] = useState("");

  const [overview, setOverview] =
    useState<LocationOverviewDto | null>(
      null,
    );

  const [loading, setLoading] =
    useState(true);

  const [refreshing, setRefreshing] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  async function loadOverview(
    locationId: string,
    showLoading = false,
  ) {
    try {
      setError(null);

      if (showLoading) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }

      const data =
        await fetchOverview(
          locationId,
        );

      setOverview(data);

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load overview.",
      );

      setOverview(null);

    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }


  async function loadInitialData() {
    try {
      setError(null);
      setLoading(true);

      const data =
        await fetchLocations();

      setLocations(data);

      if (data.length === 0) {
        setSelectedLocationId("");
        setOverview(null);
        return;
      }

      const selectedId =
        selectedLocationId &&
        data.some(
          (location) =>
            location.id ===
            selectedLocationId,
        )
          ? selectedLocationId
          : data[0].id;

      setSelectedLocationId(
        selectedId,
      );

      await loadOverview(
        selectedId,
        true,
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load overview.",
      );

      setOverview(null);

    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    void loadInitialData();
  }, [refreshKey]);


  function handleLocationChange(
    locationId: string,
  ) {
    setSelectedLocationId(
      locationId,
    );

    void loadOverview(
      locationId,
      true,
    );
  }


  function handleRefresh() {
    if (!selectedLocationId) {
      return;
    }

    void loadOverview(
      selectedLocationId,
    );
  }


  if (loading) {
    return (
      <p className="text-sm text-slate-500">
        Loading overview...
      </p>
    );
  }


  if (locations.length === 0) {
    return (
      <div className="rounded-lg border border-slate-200 bg-slate-50 p-5">
        <p className="font-medium text-slate-800">
          No locations yet.
        </p>

        <p className="mt-1 text-sm text-slate-500">
          Create a location in Configuration first.
        </p>
      </div>
    );
  }


  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <label className="grid min-w-60 gap-1">
          <span className="text-sm font-medium text-slate-700">
            Location
          </span>

          <select
            value={selectedLocationId}
            onChange={(event) =>
              handleLocationChange(
                event.target.value,
              )
            }
            className="rounded-lg border border-slate-300 bg-white px-3 py-2"
          >
            {locations.map(
              (location) => (
                <option
                  key={location.id}
                  value={location.id}
                >
                  {location.name}
                </option>
              ),
            )}
          </select>
        </label>


        <button
          type="button"
          onClick={handleRefresh}
          disabled={refreshing}
          className="rounded-lg border border-slate-300 px-4 py-2 font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {refreshing
            ? "Refreshing..."
            : "Refresh"}
        </button>
      </div>


      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}


      {overview && (
        <div className="space-y-5">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-xl border border-slate-200 bg-white p-5">
              <p className="text-sm text-slate-500">
                Sensors
              </p>

              <p className="mt-2 text-3xl font-bold text-slate-900">
                {overview.device_counts.sensor}
              </p>

              <p className="mt-1 text-xs text-slate-500">
                Assigned to zones
              </p>
            </div>


            <div className="rounded-xl border border-slate-200 bg-white p-5">
              <p className="text-sm text-slate-500">
                Actuators
              </p>

              <p className="mt-2 text-3xl font-bold text-slate-900">
                {overview.device_counts.actuator}
              </p>

              <p className="mt-1 text-xs text-slate-500">
                Assigned to zones
              </p>
            </div>


            <div className="rounded-xl border border-slate-200 bg-white p-5">
              <p className="text-sm text-slate-500">
                Strategy
              </p>

              <p className="mt-2 text-lg font-semibold text-slate-900">
                {overview.strategy_key ??
                  "No strategy saved"}
              </p>

              <p className="mt-1 text-xs text-slate-500">
                Saved automation strategy
              </p>
            </div>
          </div>


          <div className="rounded-xl border border-slate-200 bg-white p-5">
            <h4 className="font-semibold text-slate-900">
              Last recommendation
            </h4>

            {overview.last_recommendation ? (
              <div className="mt-3">
                <span
                  className={
                    overview
                      .last_recommendation
                      .action === "irrigate"
                      ? "inline-flex rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700"
                      : "inline-flex rounded-full bg-slate-200 px-3 py-1 text-xs font-semibold text-slate-700"
                  }
                >
                  {
                    overview
                      .last_recommendation
                      .action
                  }
                </span>

                <p className="mt-3 text-sm text-slate-700">
                  {
                    overview
                      .last_recommendation
                      .reason
                  }
                </p>
              </div>
            ) : (
              <p className="mt-3 text-sm text-slate-500">
                No saved strategy or recommendation yet.
              </p>
            )}
          </div>


          <div className="grid gap-5">
            {overview.zones.map(
              (zone) => {
                const readingsByDevice =
                  new Map(
                    zone.latest_readings.map(
                      (reading) => [
                        reading.device_id,
                        reading,
                      ],
                    ),
                  );

                return (
                  <section
                    key={zone.id}
                    className="rounded-xl border border-slate-200 bg-white p-5"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-4">
                      <div>
                        <h4 className="text-lg font-semibold text-slate-900">
                          {zone.name}
                        </h4>

                        <p className="mt-1 text-sm text-slate-500">
                          Moisture:
                          {" "}
                          {
                            zone.moisture_threshold_low
                          }
                          {" – "}
                          {
                            zone.moisture_threshold_high
                          }
                        </p>
                      </div>
                    </div>


                    {zone.devices.length ===
                    0 ? (
                      <div className="mt-4 rounded-lg bg-slate-50 p-4 text-sm text-slate-500">
                        No devices assigned to this zone.
                      </div>
                    ) : (
                      <div className="mt-4 space-y-3">
                        {zone.devices.map(
                          (device) => {
                            const reading =
                              readingsByDevice.get(
                                device.id,
                              );

                            return (
                              <div
                                key={device.id}
                                className="rounded-lg border border-slate-200 p-4"
                              >
                                <div className="flex flex-wrap items-start justify-between gap-3">
                                  <div>
                                    <p className="font-medium text-slate-900">
                                      {
                                        device.display_name
                                      }
                                    </p>

                                    <p className="mt-1 text-xs text-slate-500">
                                      {
                                        device.device_type
                                      }
                                      {" · "}
                                      {
                                        device.role
                                      }
                                    </p>
                                  </div>
                                </div>


                                {reading ? (
                                  <div className="mt-3 grid gap-3 md:grid-cols-4">
                                    <div>
                                      <p className="text-xs text-slate-500">
                                        Value
                                      </p>

                                      <p className="font-semibold text-slate-900">
                                        {
                                          reading.value
                                        }
                                        {" "}
                                        {
                                          reading.unit
                                        }
                                      </p>
                                    </div>

                                    <div>
                                      <p className="text-xs text-slate-500">
                                        Tracking
                                      </p>

                                      <p className="font-medium text-slate-900">
                                        {reading.tracking_enabled
                                          ? "Enabled"
                                          : "Off"}
                                      </p>
                                    </div>

                                    <div>
                                      <p className="text-xs text-slate-500">
                                        Interval
                                      </p>

                                      <p className="font-medium text-slate-900">
                                        {
                                          reading.sampling_interval_seconds
                                        }
                                        {" s"}
                                      </p>
                                    </div>

                                    <div>
                                      <p className="text-xs text-slate-500">
                                        Recorded
                                      </p>

                                      <p className="font-medium text-slate-900">
                                        {new Date(
                                          reading.recorded_at,
                                        ).toLocaleString()}
                                      </p>
                                    </div>
                                  </div>
                                ) : (
                                  <p className="mt-3 text-sm text-slate-500">
                                    No reading stored for this device.
                                  </p>
                                )}
                              </div>
                            );
                          },
                        )}
                      </div>
                    )}
                  </section>
                );
              },
            )}
          </div>
        </div>
      )}
    </div>
  );
}