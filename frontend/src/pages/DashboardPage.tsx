import { useState } from "react";

import LocationConfigWizard from "../components/config/LocationConfigWizard";
import DeviceFamilySwitcher from "../components/devices/DeviceFamilySwitcher";
import DeviceList from "../components/devices/DeviceList";
import StrategyPanel from "../features/automation/StrategyPanel";
import OverviewPanel from "../features/overview/OverviewPanel";
import SensorList from "../features/sensors/SensorList";
import type { DeviceFamily } from "../services/api";


export default function DashboardPage() {
  const [family, setFamily] =
    useState<DeviceFamily>(
      "simulation",
    );

  const [
    locationRefreshKey,
    setLocationRefreshKey,
  ] = useState(0);


  function handleLocationsChanged() {
    setLocationRefreshKey(
      (current) => current + 1,
    );
  }


  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-slate-900">
          Dashboard
        </h2>

        <p className="mt-2 text-slate-600">
          Smart Greenhouse monitoring and control.
        </p>
      </div>


      <section
        id="sensors"
        className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <div className="mb-6">
          <h3 className="text-xl font-semibold text-slate-900">
            Sensors
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            Create and view greenhouse sensors.
          </p>
        </div>

        <SensorList />
      </section>


      <section
        id="configuration"
        className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <div className="mb-6">
          <h3 className="text-xl font-semibold text-slate-900">
            Configuration
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            Create locations and manage their zones.
          </p>
        </div>

        <LocationConfigWizard
          onLocationsChanged={
            handleLocationsChanged
          }
        />
      </section>


      <section
        id="devices"
        className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <div className="mb-6">
          <h3 className="text-xl font-semibold text-slate-900">
            Devices
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            Provision and view a complete device family.
          </p>
        </div>

        <div className="space-y-6">
          <DeviceFamilySwitcher
            selectedFamily={family}
            onChange={setFamily}
          />

          <DeviceList
            family={family}
            refreshKey={
              locationRefreshKey
            }
          />
        </div>
      </section>


      <section
        id="automation"
        className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <div className="mb-6">
          <h3 className="text-xl font-semibold text-slate-900">
            Automation
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            Choose and evaluate the location automation strategy.
          </p>
        </div>

        <StrategyPanel
          refreshKey={
            locationRefreshKey
          }
        />
      </section>


      <section
        id="overview"
        className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      >
        <div className="mb-6">
          <h3 className="text-xl font-semibold text-slate-900">
            Overview
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            One current snapshot of the selected location.
          </p>
        </div>

        <OverviewPanel
          refreshKey={
            locationRefreshKey
          }
        />
      </section>


      <div className="grid gap-6 md:grid-cols-2">
        <section
          id="controls"
          className="min-h-40 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <h3 className="text-lg font-semibold text-slate-900">
            Controls
          </h3>

          <p className="mt-2 text-sm text-slate-500">
            Placeholder for later phases.
          </p>
        </section>


        <section
          id="events"
          className="min-h-40 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
        >
          <h3 className="text-lg font-semibold text-slate-900">
            Events
          </h3>

          <p className="mt-2 text-sm text-slate-500">
            Placeholder for later phases.
          </p>
        </section>
      </div>
    </div>
  );
}