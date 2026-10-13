from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class LocationAutomationContext:
    location_id: UUID
    zone_id: UUID
    moisture: float | None
    low: float
    high: float
    light: float | None = None
    zone_name: str = ""

    def __post_init__(self) -> None:
        if not 0.0 <= self.low <= 1.0:
            raise ValueError(
                "Zone low threshold must be between 0.0 and 1.0."
            )

        if not 0.0 <= self.high <= 1.0:
            raise ValueError(
                "Zone high threshold must be between 0.0 and 1.0."
            )

        if self.low >= self.high:
            raise ValueError(
                "Zone low threshold must be lower than high threshold."
            )