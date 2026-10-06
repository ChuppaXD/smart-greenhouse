from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Reading:
    device_id: UUID
    value: float
    unit: str
    source: str
    recorded_at: datetime

    def __post_init__(self) -> None:
        if self.recorded_at.tzinfo is None:
            raise ValueError("recorded_at must be timezone-aware")

        if self.source not in {"simulation", "mqtt", "vendor"}:
            raise ValueError(f"Unsupported reading source: {self.source}")