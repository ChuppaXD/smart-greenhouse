import { useEffect, useState } from "react";

import {
  fetchLocations,
  type LocationSummaryDto,
} from "../../services/api";

import {
  evaluateAutomation,
  saveAutomationStrategy,
  type RecommendationDto,
  type StrategyKey,
} from "./api";


type StrategyPanelProps = {
  refreshKey: number;
};


const strategies: Array<{
  key: StrategyKey;
  label: string;
}> = [
  {
    key: "conservative",
    label: "Conservative",
  },
  {
    key: "aggressive",
    label: "Aggressive",
  },
];


export default function StrategyPanel({
  refreshKey,
}: StrategyPanelProps) {
  const [locations, setLocations] =
    useState<LocationSummaryDto[]>(
      [],
    );

  const [
    selectedLocationId,
    setSelectedLocationId,
  ] = useState("");

  const [strategyKey, setStrategyKey] =
    useState<StrategyKey>(
      "conservative",
    );

  const [
    recommendation,
    setRecommendation,
  ] = useState<RecommendationDto | null>(
    null,
  );

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [evaluating, setEvaluating] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const [success, setSuccess] =
    useState<string | null>(null);


  async function loadLocations() {
    try {
      setLoading(true);
      setError(null);

      const data =
        await fetchLocations();

      setLocations(data);

      setSelectedLocationId(
        (current) => {
          if (
            current &&
            data.some(
              (location) =>
                location.id === current,
            )
          ) {
            return current;
          }

          return data[0]?.id ?? "";
        },
      );

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


  useEffect(() => {
    void loadLocations();
  }, [refreshKey]);


  async function handleSave() {
    if (!selectedLocationId) {
      setError(
        "Select a location first.",
      );
      return;
    }

    try {
      setSaving(true);
      setError(null);
      setSuccess(null);
      setRecommendation(null);

      await saveAutomationStrategy(
        selectedLocationId,
        strategyKey,
      );

      setSuccess(
        `Saved ${strategyKey} strategy for the selected location.`,
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to save strategy.",
      );
    } finally {
      setSaving(false);
    }
  }


  async function handleEvaluate() {
    if (!selectedLocationId) {
      setError(
        "Select a location first.",
      );
      return;
    }

    try {
      setEvaluating(true);
      setError(null);
      setSuccess(null);

      const result =
        await evaluateAutomation(
          selectedLocationId,
        );

      setRecommendation(result);

      setStrategyKey(
        result.strategy_key,
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to evaluate automation.",
      );
    } finally {
      setEvaluating(false);
    }
  }


  if (loading) {
    return (
      <p className="text-sm text-slate-500">
        Loading automation settings...
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
          Create a location in the Configuration section first.
        </p>
      </div>
    );
  }


  return (
    <div className="space-y-5">
      <div className="grid gap-4 md:grid-cols-2">
        <label className="grid gap-1">
          <span className="text-sm font-medium text-slate-700">
            Location
          </span>

          <select
            value={selectedLocationId}
            onChange={(event) => {
              setSelectedLocationId(
                event.target.value,
              );
              setRecommendation(null);
              setError(null);
              setSuccess(null);
            }}
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


        <label className="grid gap-1">
          <span className="text-sm font-medium text-slate-700">
            Strategy
          </span>

          <select
            value={strategyKey}
            onChange={(event) => {
              setStrategyKey(
                event.target.value as StrategyKey,
              );
              setRecommendation(null);
              setError(null);
              setSuccess(null);
            }}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2"
          >
            {strategies.map(
              (strategy) => (
                <option
                  key={strategy.key}
                  value={strategy.key}
                >
                  {strategy.label}
                </option>
              ),
            )}
          </select>
        </label>
      </div>


      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() =>
            void handleSave()
          }
          disabled={saving}
          className="rounded-lg bg-slate-900 px-4 py-2 font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {saving
            ? "Saving..."
            : "Save strategy"}
        </button>


        <button
          type="button"
          onClick={() =>
            void handleEvaluate()
          }
          disabled={
            evaluating ||
            !selectedLocationId
          }
          className="rounded-lg border border-slate-300 px-4 py-2 font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {evaluating
            ? "Evaluating..."
            : "Evaluate"}
        </button>
      </div>


      {success && (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">
          {success}
        </div>
      )}


      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      )}


      {recommendation && (
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h4 className="text-lg font-semibold text-slate-900">
              Automation recommendation
            </h4>

            <span
              className={
                recommendation.action
                  === "irrigate"
                  ? "rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700"
                  : "rounded-full bg-slate-200 px-3 py-1 text-xs font-semibold text-slate-700"
              }
            >
              {recommendation.action}
            </span>
          </div>

          <p className="mt-3 text-sm text-slate-600">
            Strategy:{" "}
            <span className="font-medium text-slate-800">
              {recommendation.strategy_key}
            </span>
          </p>

          <p className="mt-2 text-sm text-slate-700">
            {recommendation.reason}
          </p>
        </div>
      )}
    </div>
  );
}