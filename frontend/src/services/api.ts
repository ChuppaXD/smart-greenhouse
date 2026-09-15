export type HealthResponse = {
  status: string;
  db: "ok" | "fail";
};

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);

  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }

  return response.json() as Promise<HealthResponse>;
}


export type SensorDto = {
  id: string;
  device_type: string;
  display_name: string;
  default_config: Record<string, unknown>;
};


export async function fetchSensors(): Promise<SensorDto[]> {
  const response = await fetch(`${API_BASE_URL}/api/sensors`);

  if (!response.ok) {
    throw new Error(`Failed to load sensors: ${response.status}`);
  }

  return response.json() as Promise<SensorDto[]>;
}


export async function createSensor(
  type: "moisture" | "light",
  displayName?: string,
): Promise<SensorDto> {
  const response = await fetch(`${API_BASE_URL}/api/sensors`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      type,
      display_name: displayName ?? null,
    }),
  });

  if (!response.ok) {
    const message = await response.text();

    throw new Error(
      `Failed to create sensor: ${response.status} ${message}`,
    );
  }

  return response.json() as Promise<SensorDto>;
}