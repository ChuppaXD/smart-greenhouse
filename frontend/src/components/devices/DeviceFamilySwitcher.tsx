import type { DeviceFamily } from "../../services/api";


type Props = {
  selectedFamily: DeviceFamily;
  onChange: (family: DeviceFamily) => void;
};


export default function DeviceFamilySwitcher({
  selectedFamily,
  onChange,
}: Props) {
  return (
    <div className="flex flex-wrap gap-3">
      <button
        type="button"
        onClick={() => onChange("simulation")}
        className={
          selectedFamily === "simulation"
            ? "rounded-lg bg-emerald-600 px-4 py-2 font-medium text-white"
            : "rounded-lg border border-slate-300 bg-white px-4 py-2 font-medium text-slate-700 hover:bg-slate-50"
        }
      >
        Simulation
      </button>

      <button
        type="button"
        onClick={() => onChange("edge")}
        className={
          selectedFamily === "edge"
            ? "rounded-lg bg-sky-600 px-4 py-2 font-medium text-white"
            : "rounded-lg border border-slate-300 bg-white px-4 py-2 font-medium text-slate-700 hover:bg-slate-50"
        }
      >
        Edge
      </button>
    </div>
  );
}