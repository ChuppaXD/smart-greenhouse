import { useEffect, useState } from "react";
import {
  fetchDevices,
  provisionDeviceFamily,
  type DeviceDto,
  type DeviceFamily,
} from "../../services/api";


type Props = {
  family: DeviceFamily;
};


export default function DeviceList({ family }: Props) {
  const [devices, setDevices] = useState<DeviceDto[]>([]);
  const [loading, setLoading] = useState(true);
  const [provisioning, setProvisioning] = useState(false);
  const [error, setError] = useState<string | null>(null);


  async function loadDevices() {
    try {
      setError(null);
      setLoading(true);

      const data = await fetchDevices({ family });

      setDevices(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load devices.",
      );
    } finally {
      setLoading(false);
    }
  }


  async function handleProvision() {
    try {
      setError(null);
      setProvisioning(true);

      await provisionDeviceFamily(family);

      await loadDevices();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to provision device family.",
      );
    } finally {
      setProvisioning(false);
    }
  }


  useEffect(() => {
    void loadDevices();
  }, [family]);


  if (loading) {
    return (
      <p className="text-sm text-slate-500">
        Loading devices...
      </p>
    );
  }


  return (
    <div className="space-y-6">
      <button
        type="button"
        onClick={() => void handleProvision()}
        disabled={provisioning}
        className="rounded-lg bg-slate-900 px-4 py-2 font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {provisioning
          ? "Provisioning..."
          : `Provision ${family} family`}
      </button>


      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}


      {!error && devices.length === 0 && (
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-6 text-sm text-slate-600">
          No {family} devices have been provisioned yet.
        </div>
      )}


      {devices.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2">
          {devices.map((device) => (
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

                <div className="flex gap-2">
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                    {device.role}
                  </span>

                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                    {device.device_family}
                  </span>
                </div>
              </div>


              <div className="mt-4">
                <h5 className="text-sm font-medium text-slate-700">
                  Default configuration
                </h5>

                <pre className="mt-2 overflow-x-auto rounded-md bg-slate-900 p-4 text-xs text-white">
                  {JSON.stringify(
                    device.default_config,
                    null,
                    2,
                  )}
                </pre>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}