from uuid import UUID

from pydantic import BaseModel


class ZoneCreateDto(BaseModel):
    name: str
    moisture_threshold_low: float
    moisture_threshold_high: float
    schedule: dict | None = None


class BuildLocationConfigRequestDto(BaseModel):
    location_name: str
    zones: list[ZoneCreateDto]


class ZoneResponseDto(BaseModel):
    id: UUID
    location_id: UUID
    name: str
    moisture_threshold_low: float
    moisture_threshold_high: float
    schedule: dict


class LocationSummaryDto(BaseModel):
    id: UUID
    name: str


class LocationConfigDto(BaseModel):
    location: LocationSummaryDto
    zones: list[ZoneResponseDto]


class ZoneUpdateDto(BaseModel):
    name: str | None = None
    moisture_threshold_low: float | None = None
    moisture_threshold_high: float | None = None
    schedule: dict | None = None


class ZoneAssignmentRequestDto(BaseModel):
    zone_id: UUID | None