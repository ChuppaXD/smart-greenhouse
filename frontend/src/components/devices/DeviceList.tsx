import { useEffect, useState } from "react";

import {
  assignDeviceToZone,
  fetchDevices,
  fetchLocationConfig,
  fetchLocations,
  provisionDeviceFamily,
  type DeviceDto,
  type DeviceFamily,
  type LocationSummaryDto,
} from "../../services/api";


type Props = {
  family: DeviceFamily;
  refreshKey?: number;
};


type ZoneOption = {
  zoneId: string;
  locationId: string;
  locationName: string;
  zoneName: string;
};


function stateBadgeClass(
  state: string,
): string {
  switch (state) {
    case "idle":
      return "bg-slate-100 text-slate-700";

    case "running":
      return "bg-emerald-100 text-emerald-700";

    case "error":
      return "bg-red-100 text-red-700";

    case "maintenance":
      return "bg-amber-100 text-amber-800";

    case "off":
      return "bg-gray-200 text-gray-700";

    default:
      return "bg-slate-100 text-slate-600";
  }
}


export default function DeviceList({
  family,
  refreshKey = 0,
}: Props) {
  const [devices, setDevices] = useState<
    DeviceDto[]
  >([]);

  const [zoneOptions, setZoneOptions] =
    useState<ZoneOption[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [provisioning, setProvisioning] =
    useState(false);

  const [assigningDeviceId, setAssigningDeviceId] =
    useState<string | null>(null);

  const [refreshing, setRefreshing] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  async function loadDevices(
    showInitialLoading = true,
  ) {
    try {
      setError(null);

      if (showInitialLoading) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }

      const [
        deviceData,
        locationData,
      ] = await Promise.all([
        fetchDevices({
          family,
        }),
        fetchLocations(),
      ]);

      const configs =
        await Promise.all(
          locationData.map(
            (
              location: LocationSummaryDto,
            ) =>
              fetchLocationConfig(
                location.id,
              ),
          ),
        );

      const options: ZoneOption[] =
        configs.flatMap(
          (config) =>
            config.zones.map(
              (zone) => ({
                zoneId: zone.id,
                locationId:
                  config.location.id,
                locationName:
                  config.location.name,
                zoneName: zone.name,
              }),
            ),
        );

      setDevices(deviceData);
      setZoneOptions(options);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load devices.",
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }


  async function handleProvision() {
    try {
      setError(null);
      setProvisioning(true);

      await provisionDeviceFamily(
        family
      );

      await loadDevices(false);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to provision family.",
      );
    } finally {
      setProvisioning(false);
    }
  }


  async function handleAssignment(
    device: DeviceDto,
    zoneId: string | null,
  ) {
    try {
      setError(null);

      setAssigningDeviceId(
        device.id
      );

      await assignDeviceToZone(
        device.id,
        zoneId
      );

      const selectedOption =
        zoneOptions.find(
          (option) =>
            option.zoneId === zoneId,
        );

      setDevices((current) =>
        current.map(
          (currentDevice) =>
            currentDevice.id ===
            device.id
              ? {
                  ...currentDevice,
                  zone_id: zoneId,
                  location_id:
                    selectedOption?.locationId ??
                    null,
                }
              : currentDevice,
        ),
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to assign device.",
      );
    } finally {
      setAssigningDeviceId(
        null
      );
    }
  }


  useEffect(() => {
    void loadDevices();
  }, [family, refreshKey]);


  if (loading) {
    return (
      <p className="text-sm text-slate-500">
        Loading devices...
      </p>
    );
  }


  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() =>
            void handleProvision()
          }
          disabled={provisioning}
          className="rounded-lg bg-slate-900 px-4 py-2 font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {provisioning
            ? "Provisioning..."
            : `Provision ${family} family`}
        </button>

        <button
          type="button"
          onClick={() =>
            void loadDevices(false)
          }
          disabled={refreshing}
          className="rounded-lg border border-slate-300 bg-white px-4 py-2 font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {refreshing
            ? "Refreshing..."
            : "Refresh devices"}
        </button>
      </div>


      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}


      {!error &&
        devices.length === 0 && (
          <div className="rounded-lg border border-slate-200 bg-slate-50 p-6 text-sm text-slate-600">
            No {family} devices have
            been provisioned yet.
          </div>
        )}


      {devices.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2">
          {devices.map((device) => {
            const currentOption =
              zoneOptions.find(
                (option) =>
                  option.zoneId ===
                  device.zone_id,
              );

            const commandText =
              device.allowed_commands.length > 0
                ? device.allowed_commands.join(
                    ", "
                  )
                : "No actuator commands available in this state.";

            return (
              <article
                key={device.id}
                className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
              >
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <h4 className="font-semibold text-slate-900">
                      {device.display_name}
                    </h4>

                    <p className="mt-1 text-sm text-slate-500">
                      {device.device_type}
                    </p>
                  </div>


                  <div className="flex flex-wrap gap-2">
                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                      {device.role}
                    </span>

                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                      {device.device_family}
                    </span>

                    {device.role ===
                      "actuator" && (
                      <span
                        title={
                          `Allowed commands now: ` +
                          commandText
                        }
                        className={
                          `rounded-full px-3 py-1 ` +
                          `text-xs font-semibold ` +
                          stateBadgeClass(
                            device.state
                          )
                        }
                      >
                        {device.state}
                      </span>
                    )}
                  </div>
                </div>


                {device.role ===
                  "actuator" && (
                  <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Allowed commands
                    </p>

                    <p className="mt-1 text-sm text-slate-700">
                      {commandText}
                    </p>
                  </div>
                )}


                <div className="mt-5">
                  <label className="block text-sm font-medium text-slate-700">
                    Zone assignment
                  </label>

                  <select
                    value={
                      device.zone_id ?? ""
                    }
                    onChange={(event) =>
                      void handleAssignment(
                        device,
                        event.target.value ||
                          null
                      )
                    }
                    disabled={
                      assigningDeviceId ===
                      device.id
                    }
                    className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2"
                  >
                    <option value="">
                      Unassigned
                    </option>

                    {Object.entries(
                      zoneOptions.reduce(
                        (
                          groups,
                          option,
                        ) => {
                          (
                            groups[
                              option
                                .locationId
                            ] ??= []
                          ).push(option);

                          return groups;
                        },
                        {} as Record<
                          string,
                          ZoneOption[]
                        >
                      ),
                    ).map(
                      ([
                        locationId,
                        options,
                      ]) => (
                        <optgroup
                          key={locationId}
                          label={
                            options[0]
                              ?.locationName ??
                            "Location"
                          }
                        >
                          {options.map(
                            (
                              option
                            ) => (
                              <option
                                key={
                                  option.zoneId
                                }
                                value={
                                  option.zoneId
                                }
                              >
                                {
                                  option.locationName
                                }
                                {" — "}
                                {
                                  option.zoneName
                                }
                              </option>
                            )
                          )}
                        </optgroup>
                      )
                    )}
                  </select>


                  <p className="mt-2 text-xs text-slate-500">
                    Current:{" "}
                    {currentOption
                      ? `${currentOption.locationName} — ${currentOption.zoneName}`
                      : "Unassigned"}
                  </p>
                </div>


                <div className="mt-4">
                  <h5 className="text-sm font-medium text-slate-700">
                    Default configuration
                  </h5>

                  <pre className="mt-2 overflow-x-auto rounded-md bg-slate-900 p-4 text-xs text-white">
                    {JSON.stringify(
                      device.default_config,
                      null,
                      2
                    )}
                  </pre>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}