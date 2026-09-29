export type HealthResponse = {
  status: string;
  db: "ok" | "fail";
};


const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";


export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(
    `${API_BASE_URL}/health`,
  );

  if (!response.ok) {
    throw new Error(
      `Health check failed: ${response.status}`,
    );
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
  const response = await fetch(
    `${API_BASE_URL}/api/sensors`,
  );

  if (!response.ok) {
    throw new Error(
      `Failed to load sensors: ${response.status}`,
    );
  }

  return response.json() as Promise<SensorDto[]>;
}


export async function createSensor(
  type: "moisture" | "light",
  displayName?: string,
): Promise<SensorDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/sensors`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        type,
        display_name: displayName ?? null,
      }),
    },
  );

  if (!response.ok) {
    const message = await response.text();

    throw new Error(
      `Failed to create sensor: ${response.status} ${message}`,
    );
  }

  return response.json() as Promise<SensorDto>;
}


export type DeviceFamily =
  | "simulation"
  | "edge";


export type DeviceDto = {
  id: string;
  device_type: string;
  role: "sensor" | "actuator";
  device_family: string;
  display_name: string;
  default_config: Record<string, unknown>;
  zone_id: string | null;
  location_id: string | null;
};


export async function fetchDevices({
  family,
  role,
}: {
  family?: DeviceFamily;
  role?: "sensor" | "actuator";
} = {}): Promise<DeviceDto[]> {
  const params = new URLSearchParams();

  if (family) {
    params.set("family", family);
  }

  if (role) {
    params.set("role", role);
  }

  const query = params.toString();

  const response = await fetch(
    `${API_BASE_URL}/api/devices${
      query ? `?${query}` : ""
    }`,
  );

  if (!response.ok) {
    throw new Error(
      `Failed to load devices: ${response.status}`,
    );
  }

  return response.json() as Promise<DeviceDto[]>;
}


export async function provisionDeviceFamily(
  family: DeviceFamily,
): Promise<DeviceDto[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/devices/provision?family=${family}`,
    {
      method: "POST",
    },
  );

  if (!response.ok) {
    const message = await response.text();

    throw new Error(
      `Failed to provision device family: ${response.status} ${message}`,
    );
  }

  return response.json() as Promise<DeviceDto[]>;
}


export type ZoneDto = {
  id: string;
  location_id: string;
  name: string;
  moisture_threshold_low: number;
  moisture_threshold_high: number;
  schedule: Record<string, unknown>;
};


export type LocationSummaryDto = {
  id: string;
  name: string;
};


export type LocationConfigDto = {
  location: LocationSummaryDto;
  zones: ZoneDto[];
};


export type ZoneCreateDto = {
  name: string;
  moisture_threshold_low: number;
  moisture_threshold_high: number;
  schedule?: Record<string, unknown>;
};


export type BuildLocationConfigRequest = {
  location_name: string;
  zones: ZoneCreateDto[];
};


export type ZoneUpdateDto = {
  name?: string;
  moisture_threshold_low?: number;
  moisture_threshold_high?: number;
  schedule?: Record<string, unknown>;
};


export async function fetchLocations(): Promise<
  LocationSummaryDto[]
> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations`,
  );

  if (!response.ok) {
    throw new Error(
      `Failed to load locations: ${response.status}`,
    );
  }

  return response.json() as Promise<
    LocationSummaryDto[]
  >;
}


export async function createLocationConfig(
  request: BuildLocationConfigRequest,
): Promise<LocationConfigDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/config`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    },
  );

  if (!response.ok) {
    const message = await response.text();

    throw new Error(
      `Failed to create location: ${response.status} ${message}`,
    );
  }

  return response.json() as Promise<LocationConfigDto>;
}


export async function fetchLocationConfig(
  locationId: string,
): Promise<LocationConfigDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/config`,
  );

  if (!response.ok) {
    throw new Error(
      `Failed to load location config: ${response.status}`,
    );
  }

  return response.json() as Promise<LocationConfigDto>;
}


export async function deleteLocation(
  locationId: string,
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}`,
    {
      method: "DELETE",
    },
  );

  if (!response.ok) {
    const message = await response.text();

    throw new Error(
      `Failed to delete location: ${response.status} ${message}`,
    );
  }
}


export async function addZone(
  locationId: string,
  zone: ZoneCreateDto,
): Promise<ZoneDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/zones`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(zone),
    },
  );

  if (!response.ok) {
    const message = await response.text();

    throw new Error(
      `Failed to add zone: ${response.status} ${message}`,
    );
  }

  return response.json() as Promise<ZoneDto>;
}


export async function updateZone(
  locationId: string,
  zoneId: string,
  zone: ZoneUpdateDto,
): Promise<ZoneDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/zones/${zoneId}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(zone),
    },
  );

  if (!response.ok) {
    const message = await response.text();

    throw new Error(
      `Failed to update zone: ${response.status} ${message}`,
    );
  }

  return response.json() as Promise<ZoneDto>;
}


export async function deleteZone(
  locationId: string,
  zoneId: string,
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/zones/${zoneId}`,
    {
      method: "DELETE",
    },
  );

  if (!response.ok) {
    const message = await response.text();

    throw new Error(
      `Failed to delete zone: ${response.status} ${message}`,
    );
  }
}


export async function assignDeviceToZone(
  deviceId: string,
  zoneId: string | null,
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/api/devices/${deviceId}/zone`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        zone_id: zoneId,
      }),
    },
  );

  if (!response.ok) {
    const message = await response.text();

    throw new Error(
      `Failed to assign device: ${response.status} ${message}`,
    );
  }
}


export async function fetchZoneDevices(
  locationId: string,
  zoneId: string,
): Promise<DeviceDto[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/zones/${zoneId}/devices`,
  );

  if (!response.ok) {
    throw new Error(
      `Failed to load zone devices: ${response.status}`,
    );
  }

  return response.json() as Promise<DeviceDto[]>;
}