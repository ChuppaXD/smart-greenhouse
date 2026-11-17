import {
  useEffect,
  useState,
} from "react";

import {
  executeCommand,
  fetchActuatorDevices,
  fetchCommandHistory,
  type ActuatorDeviceDto,
  type CommandLogDto,
} from "../../services/api";


type Props = {
  refreshKey?: number;
};


export default function CommandPanel({
  refreshKey = 0,
}: Props) {
  const [
    actuators,
    setActuators,
  ] = useState<ActuatorDeviceDto[]>(
    []
  );

  const [
    history,
    setHistory,
  ] = useState<CommandLogDto[]>(
    []
  );

  const [
    lightLevels,
    setLightLevels,
  ] = useState<Record<string, number>>(
    {}
  );

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState<string | null>(
    null
  );


  async function reload() {
    try {
      setError(null);
      setLoading(true);

      const [
        actuatorData,
        historyData,
      ] = await Promise.all([
        fetchActuatorDevices(),
        fetchCommandHistory(50),
      ]);

      setActuators(actuatorData);
      setHistory(historyData);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load command controls."
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    void reload();
  }, [refreshKey]);


  async function runCommand(
    deviceId: string,
    commandType: string,
    payload: Record<string, unknown> = {},
  ) {
    let commandError: string | null = null;

    try {
      setError(null);

      const result = await executeCommand({
        command_type: commandType,
        device_id: deviceId,
        payload,
      });

      if (result.status !== "success") {
        commandError =
          result.error_message ??
          `Command ${result.status}.`;
      }
    } catch (err) {
      commandError =
        err instanceof Error
          ? err.message
          : "Command failed.";
    }

    // Refresh the actuators and saved command history.
    await reload();

    // Show command failures after the refresh.
    if (commandError) {
      setError(commandError);
    }
  }


  if (loading) {
    return (
      <p className="text-sm text-slate-500">
        Loading actuator controls...
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


      {actuators.length === 0 ? (
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-6 text-sm text-slate-600">
          No actuator devices are available.
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {actuators.map(
            (actuator) => {
              const level =
                lightLevels[
                  actuator.id
                ] ?? 1;

              const canStart =
                actuator.allowed_commands.includes(
                  "start_pump"
                );

              const canStop =
                actuator.allowed_commands.includes(
                  "stop_pump"
                );

              const canSetLight =
                actuator.allowed_commands.includes(
                  "set_light_level"
                );

              return (
                <article
                  key={actuator.id}
                  className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
                >
                  <div className="mb-5">
                    <h4 className="font-semibold text-slate-900">
                      {actuator.display_name}
                    </h4>

                    <p className="mt-1 text-sm text-slate-500">
                      {actuator.device_type}
                    </p>

                    <div className="mt-3 flex flex-wrap gap-2">
                      <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                        State:{" "}
                        {actuator.state}
                      </span>

                      <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                        Family:{" "}
                        {actuator.device_family}
                      </span>
                    </div>
                  </div>


                  <div className="space-y-3">
                    <button
                      type="button"
                      disabled={!canStart}
                      onClick={() =>
                        void runCommand(
                          actuator.id,
                          "start_pump",
                        )
                      }
                      className="w-full rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-40"
                    >
                      Start pump
                    </button>


                    <button
                      type="button"
                      disabled={!canStop}
                      onClick={() =>
                        void runCommand(
                          actuator.id,
                          "stop_pump",
                        )
                      }
                      className="w-full rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                      Stop pump
                    </button>


                    <div className="flex gap-2">
                      <input
                        type="number"
                        min="0"
                        value={level}
                        onChange={(
                          event,
                        ) =>
                          setLightLevels(
                            (current) => ({
                              ...current,
                              [actuator.id]:
                                Number(
                                  event
                                    .target
                                    .value,
                                ),
                            }),
                          )
                        }
                        className="min-w-0 flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm"
                      />

                      <button
                        type="button"
                        disabled={
                          !canSetLight
                        }
                        onClick={() =>
                          void runCommand(
                            actuator.id,
                            "set_light_level",
                            {
                              level,
                            },
                          )
                        }
                        className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 disabled:cursor-not-allowed disabled:opacity-40"
                      >
                        Set light
                      </button>
                    </div>
                  </div>


                  <p className="mt-4 text-xs text-slate-500">
                    Allowed:{" "}
                    {actuator
                      .allowed_commands
                      .length > 0
                      ? actuator.allowed_commands.join(
                          ", "
                        )
                      : "none"}
                  </p>
                </article>
              );
            }
          )}
        </div>
      )}


      <div>
        <div className="mb-4 flex items-center justify-between gap-4">
          <div>
            <h4 className="text-lg font-semibold text-slate-900">
              Command history
            </h4>

            <p className="text-sm text-slate-500">
              The newest actuator command attempts.
            </p>
          </div>

          <button
            type="button"
            onClick={() =>
              void reload()
            }
            className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Refresh
          </button>
        </div>


        {history.length === 0 ? (
          <div className="rounded-lg border border-slate-200 bg-slate-50 p-6 text-sm text-slate-600">
            No commands have been executed yet.
          </div>
        ) : (
          <div className="overflow-x-auto rounded-lg border border-slate-200">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-3 text-left font-semibold text-slate-700">
                    Time
                  </th>

                  <th className="px-4 py-3 text-left font-semibold text-slate-700">
                    Command
                  </th>

                  <th className="px-4 py-3 text-left font-semibold text-slate-700">
                    Device
                  </th>

                  <th className="px-4 py-3 text-left font-semibold text-slate-700">
                    Status
                  </th>

                  <th className="px-4 py-3 text-left font-semibold text-slate-700">
                    Message
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-200 bg-white">
                {history.map(
                  (entry) => (
                    <tr
                      key={
                        entry.id
                      }
                    >
                      <td className="whitespace-nowrap px-4 py-3 text-slate-600">
                        {new Date(
                          entry.created_at
                        ).toLocaleString()}
                      </td>

                      <td className="px-4 py-3 font-medium text-slate-900">
                        {
                          entry.command_type
                        }
                      </td>

                      <td className="px-4 py-3 font-mono text-xs text-slate-600">
                        {
                          entry.device_id
                        }
                      </td>

                      <td className="px-4 py-3">
                        <span
                          className={
                            entry.status ===
                            "success"
                              ? "rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700"
                              : entry.status ===
                                  "rejected"
                                ? "rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-700"
                                : "rounded-full bg-red-100 px-3 py-1 text-xs font-semibold text-red-700"
                          }
                        >
                          {
                            entry.status
                          }
                        </span>
                      </td>

                      <td className="px-4 py-3 text-slate-600">
                        {
                          entry.error_message ??
                          ""
                        }
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}