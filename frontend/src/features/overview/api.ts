import type {
  LocationSummaryDto,
} from "../../services/api";


const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:8000";


export type OverviewDeviceDto = {
  id: string;
  device_type: string;
  role: string;
  display_name: string;
};


export type OverviewReadingDto = {
  device_id: string;
  value: number;
  unit: string;
  recorded_at: string;
  tracking_enabled: boolean;
  sampling_interval_seconds: number;
};


export type OverviewZoneDto = {
  id: string;
  name: string;
  moisture_threshold_low: number;
  moisture_threshold_high: number;
  devices: OverviewDeviceDto[];
  latest_readings: OverviewReadingDto[];
};


export type DeviceCountsDto = {
  sensor: number;
  actuator: number;
};


export type RecommendationSummaryDto = {
  action: string;
  reason: string;
};


export type LocationOverviewDto = {
  location: LocationSummaryDto;
  device_counts: DeviceCountsDto;
  zones: OverviewZoneDto[];
  strategy_key: string | null;
  last_recommendation:
    | RecommendationSummaryDto
    | null;
};


async function readError(
  response: Response,
  fallback: string,
): Promise<string> {
  try {
    const body =
      await response.json();

    if (
      typeof body?.detail === "string"
    ) {
      return body.detail;
    }
  } catch {
    // Keep fallback.
  }

  return fallback;
}


export async function fetchOverview(
  locationId: string,
): Promise<LocationOverviewDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/overview`,
  );

  if (!response.ok) {
    throw new Error(
      await readError(
        response,
        `Failed to load overview: ${response.status}`,
      ),
    );
  }

  return response.json() as Promise<
    LocationOverviewDto
  >;
}