import { useState } from "react";

import SensorList from "../features/sensors/SensorList";
import DeviceFamilySwitcher from "../components/devices/DeviceFamilySwitcher";
import DeviceList from "../components/devices/DeviceList";
import type { DeviceFamily } from "../services/api";


const sections = [
  { id: "config", title: "Configuration" },
  { id: "automation", title: "Automation" },
  { id: "overview", title: "Overview" },
  { id: "controls", title: "Controls" },
  { id: "events", title: "Events" },
];


export default function DashboardPage() {
  const [family, setFamily] = useState<DeviceFamily>("simulation");


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

          <DeviceList family={family} />
        </div>
      </section>


      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {sections.map((section) => (
          <section
            key={section.id}
            id={section.id}
            className="min-h-40 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <h3 className="text-lg font-semibold text-slate-900">
              {section.title}
            </h3>

            <p className="mt-2 text-sm text-slate-500">
              Placeholder for later phases.
            </p>
          </section>
        ))}
      </div>
    </div>
  );
}