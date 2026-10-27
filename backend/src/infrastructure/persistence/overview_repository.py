from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    func,
    select,
)

from infrastructure.persistence.models import (
    DeviceRow,
    LocationRow,
    ReadingRow,
    ZoneRow,
)


@dataclass(frozen=True)
class OverviewLocationData:
    id: UUID
    name: str
    zones: list["OverviewZoneData"]


@dataclass(frozen=True)
class OverviewZoneData:
    id: UUID
    name: str
    moisture_threshold_low: float
    moisture_threshold_high: float


@dataclass(frozen=True)
class OverviewDeviceData:
    id: UUID
    device_type: str
    role: str
    display_name: str
    zone_id: UUID
    tracking_enabled: bool
    sampling_interval_seconds: int


@dataclass(frozen=True)
class OverviewReadingData:
    device_id: UUID
    value: float
    unit: str
    recorded_at: datetime


class LocationOverviewRepository:
    def __init__(self, session):
        self._session = session

    def get_location_with_zones(
        self,
        location_id: UUID,
    ) -> OverviewLocationData | None:
        statement = (
            select(LocationRow, ZoneRow)
            .outerjoin(
                ZoneRow,
                ZoneRow.location_id == LocationRow.id,
            )
            .where(
                LocationRow.id == location_id,
            )
            .order_by(
                ZoneRow.name,
            )
        )

        rows = (
            self._session.execute(statement)
            .all()
        )

        if not rows:
            return None

        location_row = rows[0][0]

        zones: list[OverviewZoneData] = []

        for _, zone_row in rows:
            if zone_row is None:
                continue

            zones.append(
                OverviewZoneData(
                    id=zone_row.id,
                    name=zone_row.name,
                    moisture_threshold_low=float(
                        zone_row.moisture_threshold_low
                    ),
                    moisture_threshold_high=float(
                        zone_row.moisture_threshold_high
                    ),
                )
            )

        return OverviewLocationData(
            id=location_row.id,
            name=location_row.name,
            zones=zones,
        )

    def list_assigned_devices(
        self,
        location_id: UUID,
    ) -> list[OverviewDeviceData]:
        statement = (
            select(DeviceRow)
            .where(
                DeviceRow.location_id == location_id,
                DeviceRow.zone_id.is_not(None),
            )
            .order_by(
                DeviceRow.created_at,
            )
        )

        rows = (
            self._session.execute(statement)
            .scalars()
            .all()
        )

        return [
            OverviewDeviceData(
                id=row.id,
                device_type=row.device_type,
                role=row.role,
                display_name=(
                    row.display_name
                    or row.device_type
                ),
                zone_id=row.zone_id,
                tracking_enabled=(
                    row.tracking_enabled
                ),
                sampling_interval_seconds=(
                    row.sampling_interval_seconds
                ),
            )
            for row in rows
            if row.zone_id is not None
        ]

    def latest_readings(
        self,
        device_ids: list[UUID],
    ) -> list[OverviewReadingData]:
        if not device_ids:
            return []

        row_number = (
            func.row_number()
            .over(
                partition_by=ReadingRow.device_id,
                order_by=(
                    ReadingRow.recorded_at.desc(),
                    ReadingRow.id.desc(),
                ),
            )
            .label("row_number")
        )

        ranked = (
            select(
                ReadingRow.device_id.label(
                    "device_id"
                ),
                ReadingRow.value.label(
                    "value"
                ),
                ReadingRow.unit.label(
                    "unit"
                ),
                ReadingRow.recorded_at.label(
                    "recorded_at"
                ),
                row_number,
            )
            .where(
                ReadingRow.device_id.in_(
                    device_ids
                )
            )
            .subquery()
        )

        statement = (
            select(
                ranked.c.device_id,
                ranked.c.value,
                ranked.c.unit,
                ranked.c.recorded_at,
            )
            .where(
                ranked.c.row_number == 1
            )
        )

        rows = (
            self._session.execute(statement)
            .all()
        )

        result: list[
            OverviewReadingData
        ] = []

        for row in rows:
            value = row.value

            if isinstance(
                value,
                Decimal,
            ):
                value = float(value)

            result.append(
                OverviewReadingData(
                    device_id=row.device_id,
                    value=float(value),
                    unit=row.unit,
                    recorded_at=row.recorded_at,
                )
            )

        return result