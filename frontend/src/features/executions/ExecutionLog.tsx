import {
  useEffect,
  useState,
} from "react";

import {
  fetchActuatorExecutions,
  type ActuatorExecutionDto,
} from "../../services/api";


type Props = {
  refreshKey?: number;
};


export default function ExecutionLog({
  refreshKey = 0,
}: Props) {
  const [
    executions,
    setExecutions,
  ] = useState<ActuatorExecutionDto[]>(
    []
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


  async function loadExecutions() {
    try {
      setError(null);
      setLoading(true);

      const data =
        await fetchActuatorExecutions(
          20
        );

      setExecutions(data);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load execution log."
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    void loadExecutions();
  }, [refreshKey]);


  if (loading) {
    return (
      <p className="text-sm text-slate-500">
        Loading execution log...
      </p>
    );
  }


  if (error) {
    return (
      <div className="space-y-4">
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>

        <button
          type="button"
          onClick={() =>
            void loadExecutions()
          }
          className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
        >
          Retry
        </button>
      </div>
    );
  }


  if (executions.length === 0) {
    return (
      <div className="rounded-lg border border-slate-200 bg-slate-50 p-6 text-sm text-slate-600">
        No actuator executions have
        been recorded yet.
      </div>
    );
  }


  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-4">
        <p className="text-sm text-slate-500">
          Latest actuator attempts from the
          persisted execution log.
        </p>

        <button
          type="button"
          onClick={() =>
            void loadExecutions()
          }
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Refresh
        </button>
      </div>


      <div className="overflow-x-auto rounded-lg border border-slate-200">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-slate-700">
                Time
              </th>

              <th className="px-4 py-3 text-left font-semibold text-slate-700">
                Device
              </th>

              <th className="px-4 py-3 text-left font-semibold text-slate-700">
                Result
              </th>

              <th className="px-4 py-3 text-left font-semibold text-slate-700">
                Policies
              </th>

              <th className="px-4 py-3 text-left font-semibold text-slate-700">
                Message
              </th>
            </tr>
          </thead>


          <tbody className="divide-y divide-slate-200 bg-white">
            {executions.map(
              (execution) => (
                <tr key={execution.id}>
                  <td className="whitespace-nowrap px-4 py-3 text-slate-600">
                    {new Date(
                      execution.created_at
                    ).toLocaleString()}
                  </td>


                  <td className="px-4 py-3 font-mono text-xs text-slate-700">
                    {execution.device_id}
                  </td>


                  <td className="px-4 py-3">
                    <span
                      className={
                        execution.success
                          ? "rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700"
                          : "rounded-full bg-red-100 px-3 py-1 text-xs font-semibold text-red-700"
                      }
                    >
                      {execution.success
                        ? "Success"
                        : "Blocked / failed"}
                    </span>
                  </td>


                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-2">
                      {execution.policy_applied.map(
                        (policy) => (
                          <span
                            key={policy}
                            className="rounded-full bg-slate-100 px-2 py-1 text-xs font-medium text-slate-700"
                          >
                            {policy}
                          </span>
                        )
                      )}
                    </div>
                  </td>


                  <td className="px-4 py-3 text-slate-600">
                    {execution.message ?? ""}
                  </td>
                </tr>
              )
            )}
          </tbody>
        </table>
      </div>


      <p className="text-xs text-slate-500">
        Phase 9 does not validate the
        command name yet. Until the actuator
        has been running for 30 minutes,
        the command can pass through. A
        successful row has an empty message
        and the logging policy. A blocked row
        shows “Max run time exceeded” with
        maxRunTime and logging.
      </p>
    </div>
  );
}