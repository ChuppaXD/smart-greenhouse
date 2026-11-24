from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class ReadingCreated:
    device_id: UUID
    value: float
    unit: str
    source: str
    recorded_at: datetime
    location_id: UUID | None = None
    zone_id: UUID | None = None


@dataclass(frozen=True)
class ThresholdCrossed:
    device_id: UUID
    location_id: UUID | None
    zone_id: UUID
    value: float
    threshold_low: float


@dataclass(frozen=True)
class CommandFailed:
    device_id: UUID
    location_id: UUID | None
    zone_id: UUID | None
    message: str
    command_type: str


@dataclass(frozen=True)
class ActuatorStateChanged:
    device_id: UUID
    location_id: UUID | None
    zone_id: UUID | None
    state: str


@dataclass(frozen=True)
class AlertCreated:
    id: UUID
    device_id: UUID | None
    location_id: UUID | None
    zone_id: UUID | None
    severity: str
    message: str
    event_type: str
    status: str
    created_at: datetime