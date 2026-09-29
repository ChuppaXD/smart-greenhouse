import { useEffect, useState } from "react";

import {
  addZone,
  createLocationConfig,
  deleteLocation,
  deleteZone,
  fetchLocationConfig,
  fetchLocations,
  fetchZoneDevices,
  updateZone,
  type LocationConfigDto,
  type LocationSummaryDto,
  type ZoneDto,
} from "../../services/api";


type Props = {
  onLocationsChanged?: () => void;
};


type DraftZone = {
  name: string;
  low: string;
  high: string;
  schedule: string;
};


const emptyDraftZone = (): DraftZone => ({
  name: "",
  low: "0.2",
  high: "0.45",
  schedule: "{}",
});


function validateDraftZone(
  zone: DraftZone,
  allZones: DraftZone[],
  index: number,
): string | null {
  if (!zone.name.trim()) {
    return "Zone name is required.";
  }

  const low = Number(zone.low);
  const high = Number(zone.high);

  if (!Number.isFinite(low) || !Number.isFinite(high)) {
    return "Thresholds must be numbers.";
  }

  if (low < 0 || low > 1 || high < 0 || high > 1) {
    return "Thresholds must be between 0.0 and 1.0.";
  }

  if (low >= high) {
    return "Low threshold must be less than high.";
  }

  const normalized = zone.name.trim().toLowerCase();

  const duplicate = allZones.some(
    (other, otherIndex) =>
      otherIndex !== index &&
      other.name.trim().toLowerCase() === normalized,
  );

  if (duplicate) {
    return "Zone names must be unique within this location.";
  }

  return null;
}


function parseSchedule(text: string): Record<string, unknown> {
  if (!text.trim()) {
    return {};
  }

  const parsed: unknown = JSON.parse(text);

  if (
    typeof parsed !== "object" ||
    parsed === null ||
    Array.isArray(parsed)
  ) {
    throw new Error(
      "Schedule must be a JSON object.",
    );
  }

  return parsed as Record<string, unknown>;
}


export default function LocationConfigWizard({
  onLocationsChanged,
}: Props) {
  const [locations, setLocations] = useState<
    LocationSummaryDto[]
  >([]);

  const [selectedLocationId, setSelectedLocationId] =
    useState<string | null>(null);

  const [selectedConfig, setSelectedConfig] =
    useState<LocationConfigDto | null>(null);

  const [zoneDevices, setZoneDevices] = useState<
    Record<string, string[]>
  >({});

  const [scheduleTexts, setScheduleTexts] =
    useState<Record<string, string>>({});

  const [newLocationName, setNewLocationName] =
    useState("");

  const [newZones, setNewZones] = useState<
    DraftZone[]
  >([emptyDraftZone()]);

  const [newZone, setNewZone] = useState<DraftZone>(
    emptyDraftZone(),
  );

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(
    null,
  );
  const [success, setSuccess] = useState<string | null>(
    null,
  );


  async function loadLocations(
    selectId?: string | null,
  ) {
    try {
      setError(null);

      const data = await fetchLocations();

      setLocations(data);

      if (selectId !== undefined) {
        setSelectedLocationId(selectId);
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load locations.",
      );
    } finally {
      setLoading(false);
    }
  }


  async function loadConfig(
    locationId: string,
  ) {
    try {
      setError(null);
      setSuccess(null);

      const config =
        await fetchLocationConfig(locationId);

      setSelectedConfig(config);

      setScheduleTexts(
        Object.fromEntries(
          config.zones.map((zone) => [
            zone.id,
            JSON.stringify(
              zone.schedule,
              null,
              2,
            ),
          ]),
        ),
      );

      const deviceResults =
        await Promise.all(
          config.zones.map(
            async (zone) => {
              const devices =
                await fetchZoneDevices(
                  config.location.id,
                  zone.id,
                );

              return [
                zone.id,
                devices.map(
                  (device) =>
                    device.display_name,
                ),
              ] as const;
            },
          ),
        );

      setZoneDevices(
        Object.fromEntries(deviceResults),
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load location.",
      );
    }
  }


  useEffect(() => {
    void loadLocations();
  }, []);


  useEffect(() => {
    if (selectedLocationId) {
      void loadConfig(selectedLocationId);
    } else {
      setSelectedConfig(null);
      setZoneDevices({});
    }
  }, [selectedLocationId]);


  function updateDraftZone(
    index: number,
    field: keyof DraftZone,
    value: string,
  ) {
    setNewZones((current) =>
      current.map((zone, zoneIndex) =>
        zoneIndex === index
          ? {
              ...zone,
              [field]: value,
            }
          : zone,
      ),
    );
  }


  async function handleCreateLocation() {
    try {
      setError(null);
      setSuccess(null);

      if (!newLocationName.trim()) {
        throw new Error(
          "Location name is required.",
        );
      }

      if (newZones.length === 0) {
        throw new Error(
          "Add at least one zone.",
        );
      }

      for (let index = 0; index < newZones.length; index += 1) {
        const validationError =
          validateDraftZone(
            newZones[index],
            newZones,
            index,
          );

        if (validationError) {
          throw new Error(
            `Zone ${index + 1}: ${validationError}`,
          );
        }
      }

      const zones = newZones.map((zone) => ({
        name: zone.name.trim(),
        moisture_threshold_low: Number(zone.low),
        moisture_threshold_high: Number(zone.high),
        schedule: parseSchedule(
          zone.schedule,
        ),
      }));

      setSaving(true);

      const created =
        await createLocationConfig({
          location_name:
            newLocationName.trim(),
          zones,
        });

      setNewLocationName("");
      setNewZones([emptyDraftZone()]);

      await loadLocations(
        created.location.id,
      );

      setSuccess(
        `Created ${created.location.name}.`,
      );

      onLocationsChanged?.();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to create location.",
      );
    } finally {
      setSaving(false);
    }
  }


  async function handleDeleteLocation(
    location: LocationSummaryDto,
  ) {
    const confirmed = window.confirm(
      `Delete location "${location.name}"? Its zones will also be deleted.`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setError(null);
      setSuccess(null);
      setSaving(true);

      await deleteLocation(location.id);

      if (
        selectedLocationId ===
        location.id
      ) {
        setSelectedLocationId(null);
        setSelectedConfig(null);
        setZoneDevices({});
      }

      await loadLocations();

      setSuccess(
        `Deleted ${location.name}.`,
      );

      onLocationsChanged?.();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to delete location.",
      );
    } finally {
      setSaving(false);
    }
  }


  function updateSelectedZone(
    zoneId: string,
    field:
      | "name"
      | "moisture_threshold_low"
      | "moisture_threshold_high",
    value: string,
  ) {
    setSelectedConfig((current) => {
      if (!current) {
        return current;
      }

      return {
        ...current,
        zones: current.zones.map(
          (zone) =>
            zone.id === zoneId
              ? {
                  ...zone,
                  [field]:
                    field ===
                    "name"
                      ? value
                      : Number(value),
                }
              : zone,
        ),
      };
    });
  }


  async function handleSaveZone(
    zone: ZoneDto,
  ) {
    if (!selectedConfig) {
      return;
    }

    try {
      setError(null);
      setSuccess(null);
      setSaving(true);

      const schedule =
        parseSchedule(
          scheduleTexts[zone.id] ??
            JSON.stringify(
              zone.schedule,
            ),
        );

      if (!zone.name.trim()) {
        throw new Error(
          "Zone name is required.",
        );
      }

      if (
        zone.moisture_threshold_low <
          0 ||
        zone.moisture_threshold_low > 1 ||
        zone.moisture_threshold_high <
          0 ||
        zone.moisture_threshold_high > 1
      ) {
        throw new Error(
          "Thresholds must be between 0.0 and 1.0.",
        );
      }

      if (
        zone.moisture_threshold_low >=
        zone.moisture_threshold_high
      ) {
        throw new Error(
          "Low threshold must be less than high.",
        );
      }

      await updateZone(
        selectedConfig.location.id,
        zone.id,
        {
          name: zone.name.trim(),
          moisture_threshold_low:
            zone.moisture_threshold_low,
          moisture_threshold_high:
            zone.moisture_threshold_high,
          schedule,
        },
      );

      await loadConfig(
        selectedConfig.location.id,
      );

      setSuccess(
        `Updated zone ${zone.name}.`,
      );

      onLocationsChanged?.();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to update zone.",
      );
    } finally {
      setSaving(false);
    }
  }


  async function handleAddZone() {
    if (!selectedConfig) {
      return;
    }

    try {
      setError(null);
      setSuccess(null);

      const validationError =
        validateDraftZone(
          newZone,
          [newZone],
          0,
        );

      if (validationError) {
        throw new Error(
          validationError,
        );
      }

      const schedule =
        parseSchedule(
          newZone.schedule,
        );

      setSaving(true);

      await addZone(
        selectedConfig.location.id,
        {
          name: newZone.name.trim(),
          moisture_threshold_low:
            Number(newZone.low),
          moisture_threshold_high:
            Number(newZone.high),
          schedule,
        },
      );

      setNewZone(
        emptyDraftZone(),
      );

      await loadConfig(
        selectedConfig.location.id,
      );

      setSuccess("Zone added.");

      onLocationsChanged?.();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to add zone.",
      );
    } finally {
      setSaving(false);
    }
  }


  async function handleDeleteZone(
    zone: ZoneDto,
  ) {
    if (!selectedConfig) {
      return;
    }

    if (selectedConfig.zones.length <= 1) {
      setError(
        "The last zone cannot be deleted.",
      );
      return;
    }

    try {
      setError(null);
      setSuccess(null);
      setSaving(true);

      await deleteZone(
        selectedConfig.location.id,
        zone.id,
      );

      await loadConfig(
        selectedConfig.location.id,
      );

      setSuccess(
        `Deleted zone ${zone.name}.`,
      );

      onLocationsChanged?.();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to delete zone.",
      );
    } finally {
      setSaving(false);
    }
  }


  if (loading) {
    return (
      <p className="text-sm text-slate-500">
        Loading locations...
      </p>
    );
  }


  return (
    <div className="space-y-8">
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {success && (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">
          {success}
        </div>
      )}


      <div className="rounded-lg border border-slate-200 bg-slate-50 p-5">
        <h4 className="font-semibold text-slate-900">
          Create a new location
        </h4>

        <div className="mt-4 space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-700">
              Location name
            </label>

            <input
              value={newLocationName}
              onChange={(event) =>
                setNewLocationName(
                  event.target.value,
                )
              }
              placeholder="Lab Site A"
              className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2"
            />
          </div>


          {newZones.map(
            (zone, index) => (
              <div
                key={index}
                className="rounded-lg border border-slate-200 bg-white p-4"
              >
                <div className="mb-3 flex items-center justify-between">
                  <h5 className="font-medium text-slate-900">
                    Zone {index + 1}
                  </h5>

                  {newZones.length > 1 && (
                    <button
                      type="button"
                      onClick={() =>
                        setNewZones(
                          (current) =>
                            current.filter(
                              (_, zoneIndex) =>
                                zoneIndex !==
                                index,
                            ),
                        )
                      }
                      className="text-sm text-red-600 hover:underline"
                    >
                      Remove
                    </button>
                  )}
                </div>


                <div className="grid gap-4 md:grid-cols-3">
                  <div>
                    <label className="block text-sm text-slate-600">
                      Name
                    </label>

                    <input
                      value={zone.name}
                      onChange={(event) =>
                        updateDraftZone(
                          index,
                          "name",
                          event.target.value,
                        )
                      }
                      className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
                    />
                  </div>

                  <div>
                    <label className="block text-sm text-slate-600">
                      Low threshold
                    </label>

                    <input
                      type="number"
                      min="0"
                      max="1"
                      step="0.01"
                      value={zone.low}
                      onChange={(event) =>
                        updateDraftZone(
                          index,
                          "low",
                          event.target.value,
                        )
                      }
                      className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
                    />
                  </div>

                  <div>
                    <label className="block text-sm text-slate-600">
                      High threshold
                    </label>

                    <input
                      type="number"
                      min="0"
                      max="1"
                      step="0.01"
                      value={zone.high}
                      onChange={(event) =>
                        updateDraftZone(
                          index,
                          "high",
                          event.target.value,
                        )
                      }
                      className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
                    />
                  </div>
                </div>


                <label className="mt-4 block text-sm text-slate-600">
                  Schedule JSON
                </label>

                <textarea
                  value={zone.schedule}
                  onChange={(event) =>
                    updateDraftZone(
                      index,
                      "schedule",
                      event.target.value,
                    )
                  }
                  rows={4}
                  className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 font-mono text-sm"
                />


                <p className="mt-2 text-xs text-slate-500">
                  Example: {"{\"watering\":\"08:00\"}"}
                </p>


                {validateDraftZone(
                  zone,
                  newZones,
                  index,
                ) && (
                  <p className="mt-2 text-sm text-red-600">
                    {validateDraftZone(
                      zone,
                      newZones,
                      index,
                    )}
                  </p>
                )}
              </div>
            ),
          )}


          <button
            type="button"
            onClick={() =>
              setNewZones((current) => [
                ...current,
                emptyDraftZone(),
              ])
            }
            className="rounded-lg border border-slate-300 bg-white px-4 py-2 font-medium text-slate-700 hover:bg-slate-50"
          >
            Add another zone
          </button>


          <div>
            <button
              type="button"
              onClick={() =>
                void handleCreateLocation()
              }
              disabled={saving}
              className="rounded-lg bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {saving
                ? "Saving..."
                : "Create location"}
            </button>
          </div>
        </div>
      </div>


      <div>
        <h4 className="font-semibold text-slate-900">
          Saved locations
        </h4>

        {locations.length === 0 ? (
          <p className="mt-3 text-sm text-slate-500">
            No saved locations yet.
          </p>
        ) : (
          <div className="mt-3 space-y-2">
            {locations.map(
              (location) => (
                <div
                  key={location.id}
                  className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-200 bg-white p-4"
                >
                  <button
                    type="button"
                    onClick={() =>
                      setSelectedLocationId(
                        location.id,
                      )
                    }
                    className="text-left"
                  >
                    <p className="font-medium text-slate-900">
                      {location.name}
                    </p>

                    <p className="text-xs text-slate-500">
                      {location.id}
                    </p>
                  </button>


                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={() =>
                        setSelectedLocationId(
                          location.id,
                        )
                      }
                      className="rounded-lg border border-slate-300 px-3 py-2 text-sm hover:bg-slate-50"
                    >
                      Select
                    </button>

                    <button
                      type="button"
                      onClick={() =>
                        void handleDeleteLocation(
                          location,
                        )
                      }
                      disabled={saving}
                      className="rounded-lg border border-red-200 px-3 py-2 text-sm text-red-700 hover:bg-red-50 disabled:opacity-50"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ),
            )}
          </div>
        )}
      </div>


      {selectedConfig && (
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-6">
            <h4 className="text-xl font-semibold text-slate-900">
              {selectedConfig.location.name}
            </h4>

            <p className="mt-1 break-all text-xs text-slate-500">
              Location ID:{" "}
              {selectedConfig.location.id}
            </p>
          </div>


          <div className="space-y-6">
            {selectedConfig.zones.map(
              (zone) => (
                <div
                  key={zone.id}
                  className="rounded-lg border border-slate-200 bg-slate-50 p-5"
                >
                  <div className="grid gap-4 md:grid-cols-3">
                    <div>
                      <label className="block text-sm text-slate-600">
                        Zone name
                      </label>

                      <input
                        value={zone.name}
                        onChange={(event) =>
                          updateSelectedZone(
                            zone.id,
                            "name",
                            event.target.value,
                          )
                        }
                        className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2"
                      />
                    </div>

                    <div>
                      <label className="block text-sm text-slate-600">
                        Low threshold
                      </label>

                      <input
                        type="number"
                        min="0"
                        max="1"
                        step="0.01"
                        value={
                          zone.moisture_threshold_low
                        }
                        onChange={(event) =>
                          updateSelectedZone(
                            zone.id,
                            "moisture_threshold_low",
                            event.target.value,
                          )
                        }
                        className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2"
                      />
                    </div>

                    <div>
                      <label className="block text-sm text-slate-600">
                        High threshold
                      </label>

                      <input
                        type="number"
                        min="0"
                        max="1"
                        step="0.01"
                        value={
                          zone.moisture_threshold_high
                        }
                        onChange={(event) =>
                          updateSelectedZone(
                            zone.id,
                            "moisture_threshold_high",
                            event.target.value,
                          )
                        }
                        className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2"
                      />
                    </div>
                  </div>


                  <label className="mt-4 block text-sm text-slate-600">
                    Schedule JSON
                  </label>

                  <textarea
                    value={
                      scheduleTexts[zone.id] ??
                      JSON.stringify(
                        zone.schedule,
                        null,
                        2,
                      )
                    }
                    onChange={(event) =>
                      setScheduleTexts(
                        (current) => ({
                          ...current,
                          [zone.id]:
                            event.target.value,
                        }),
                      )
                    }
                    rows={5}
                    className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 font-mono text-sm"
                  />


                  <div className="mt-4 flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() =>
                        void handleSaveZone(
                          zone,
                        )
                      }
                      disabled={saving}
                      className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
                    >
                      Save zone
                    </button>

                    <button
                      type="button"
                      onClick={() =>
                        void handleDeleteZone(
                          zone,
                        )
                      }
                      disabled={
                        saving ||
                        selectedConfig.zones
                          .length <= 1
                      }
                      className="rounded-lg border border-red-200 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      Delete zone
                    </button>
                  </div>


                  <div className="mt-5">
                    <h5 className="text-sm font-semibold text-slate-700">
                      Devices in this zone
                    </h5>

                    {(
                      zoneDevices[zone.id] ??
                      []
                    ).length === 0 ? (
                      <p className="mt-2 text-sm text-slate-500">
                        No devices assigned.
                      </p>
                    ) : (
                      <ul className="mt-2 space-y-1">
                        {zoneDevices[
                          zone.id
                        ].map(
                          (
                            deviceName,
                            index,
                          ) => (
                            <li
                              key={`${zone.id}-${index}`}
                              className="text-sm text-slate-700"
                            >
                              {deviceName}
                            </li>
                          ),
                        )}
                      </ul>
                    )}
                  </div>
                </div>
              ),
            )}


            <div className="rounded-lg border border-dashed border-slate-300 p-5">
              <h5 className="font-semibold text-slate-900">
                Add zone
              </h5>

              <div className="mt-4 grid gap-4 md:grid-cols-3">
                <div>
                  <label className="block text-sm text-slate-600">
                    Name
                  </label>

                  <input
                    value={newZone.name}
                    onChange={(event) =>
                      setNewZone(
                        (current) => ({
                          ...current,
                          name: event.target.value,
                        }),
                      )
                    }
                    className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
                  />
                </div>

                <div>
                  <label className="block text-sm text-slate-600">
                    Low threshold
                  </label>

                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.01"
                    value={newZone.low}
                    onChange={(event) =>
                      setNewZone(
                        (current) => ({
                          ...current,
                          low: event.target.value,
                        }),
                      )
                    }
                    className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
                  />
                </div>

                <div>
                  <label className="block text-sm text-slate-600">
                    High threshold
                  </label>

                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.01"
                    value={newZone.high}
                    onChange={(event) =>
                      setNewZone(
                        (current) => ({
                          ...current,
                          high: event.target.value,
                        }),
                      )
                    }
                    className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
                  />
                </div>
              </div>


              <label className="mt-4 block text-sm text-slate-600">
                Schedule JSON
              </label>

              <textarea
                value={newZone.schedule}
                onChange={(event) =>
                  setNewZone(
                    (current) => ({
                      ...current,
                      schedule:
                        event.target.value,
                    }),
                  )
                }
                rows={4}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 font-mono text-sm"
              />


              <button
                type="button"
                onClick={() =>
                  void handleAddZone()
                }
                disabled={saving}
                className="mt-4 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
              >
                Add zone
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}