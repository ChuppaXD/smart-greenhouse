const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:8000";


export type StrategyKey =
  | "conservative"
  | "aggressive";


export type StrategySelectionDto = {
  location_id: string;
  strategy_key: StrategyKey;
};


export type RecommendationDto = {
  location_id: string;
  strategy_key: StrategyKey;
  action: "irrigate" | "wait";
  reason: string;
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


export async function saveAutomationStrategy(
  locationId: string,
  strategyKey: StrategyKey,
): Promise<StrategySelectionDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/automation`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        strategy_key: strategyKey,
      }),
    },
  );

  if (!response.ok) {
    throw new Error(
      await readError(
        response,
        `Failed to save strategy: ${response.status}`,
      ),
    );
  }

  return response.json() as Promise<
    StrategySelectionDto
  >;
}


export async function evaluateAutomation(
  locationId: string,
): Promise<RecommendationDto> {
  const response = await fetch(
    `${API_BASE_URL}/api/locations/${locationId}/automation/evaluate`,
    {
      method: "POST",
    },
  );

  if (!response.ok) {
    throw new Error(
      await readError(
        response,
        `Failed to evaluate automation: ${response.status}`,
      ),
    );
  }

  return response.json() as Promise<
    RecommendationDto
  >;
}