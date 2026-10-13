from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.automation.context import (
    LocationAutomationContext,
)
from infrastructure.persistence.models import (
    AutomationRuleRow,
    DeviceRow,
    LocationRow,
    ReadingRow,
    ZoneRow,
)


class AutomationRepository:
    def __init__(
        self,
        session: Session,
    ):
        self._session = session

    def location_exists(
        self,
        location_id: UUID,
    ) -> bool:
        return (
            self._session.get(
                LocationRow,
                location_id,
            )
            is not None
        )

    def save_strategy(
        self,
        location_id: UUID,
        strategy_key: str,
    ) -> str:
        rule = (
            self._session.execute(
                select(AutomationRuleRow).where(
                    AutomationRuleRow.location_id
                    == location_id
                )
            )
            .scalars()
            .first()
        )

        now = datetime.now(timezone.utc)

        try:
            if rule is None:
                rule = AutomationRuleRow(
                    location_id=location_id,
                    strategy_key=strategy_key,
                    parameters={},
                    updated_at=now,
                )

                self._session.add(rule)

            else:
                rule.strategy_key = strategy_key
                rule.updated_at = now

            self._session.commit()

        except Exception:
            self._session.rollback()
            raise

        return rule.strategy_key

    def get_strategy_key(
        self,
        location_id: UUID,
    ) -> str | None:
        statement = (
            select(
                AutomationRuleRow.strategy_key
            )
            .where(
                AutomationRuleRow.location_id
                == location_id
            )
        )

        return (
            self._session.execute(statement)
            .scalar_one_or_none()
        )

    def get_zone_contexts(
        self,
        location_id: UUID,
    ) -> list[
        LocationAutomationContext
    ]:
        statement = (
            select(ZoneRow)
            .where(
                ZoneRow.location_id
                == location_id
            )
            .order_by(
                ZoneRow.name
            )
        )

        zones = (
            self._session.execute(statement)
            .scalars()
            .all()
        )

        if not zones:
            return []

        zone_ids = [
            zone.id
            for zone in zones
        ]

        device_statement = (
            select(DeviceRow)
            .where(
                DeviceRow.role == "sensor",
                DeviceRow.zone_id.in_(
                    zone_ids
                ),
            )
        )

        devices = (
            self._session.execute(
                device_statement
            )
            .scalars()
            .all()
        )

        device_ids = [
            device.id
            for device in devices
        ]

        latest_by_device_unit: dict[
            tuple[UUID, str],
            ReadingRow,
        ] = {}

        if device_ids:
            reading_statement = (
                select(ReadingRow)
                .where(
                    ReadingRow.device_id.in_(
                        device_ids
                    )
                )
                .order_by(
                    ReadingRow.recorded_at.desc()
                )
            )

            reading_rows = (
                self._session.execute(
                    reading_statement
                )
                .scalars()
                .all()
            )

            for row in reading_rows:
                key = (
                    row.device_id,
                    row.unit.lower(),
                )

                if key not in latest_by_device_unit:
                    latest_by_device_unit[key] = row

        devices_by_zone: dict[
            UUID,
            list[DeviceRow],
        ] = {}

        for device in devices:
            if device.zone_id is None:
                continue

            devices_by_zone.setdefault(
                device.zone_id,
                [],
            ).append(device)

        contexts: list[
            LocationAutomationContext
        ] = []

        for zone in zones:
            moisture_value: float | None = None
            light_value: float | None = None

            zone_devices = devices_by_zone.get(
                zone.id,
                [],
            )

            moisture_readings: list[
                ReadingRow
            ] = []

            light_readings: list[
                ReadingRow
            ] = []

            for device in zone_devices:
                device_type = (
                    device.device_type.lower()
                )

                if "moisture" in device_type:
                    reading = (
                        latest_by_device_unit.get(
                            (
                                device.id,
                                "vwc",
                            )
                        )
                    )

                    if reading is not None:
                        moisture_readings.append(
                            reading
                        )

                elif "light" in device_type:
                    reading = (
                        latest_by_device_unit.get(
                            (
                                device.id,
                                "lux",
                            )
                        )
                    )

                    if reading is not None:
                        light_readings.append(
                            reading
                        )

            if moisture_readings:
                latest_moisture = max(
                    moisture_readings,
                    key=lambda row: row.recorded_at,
                )

                moisture_value = float(
                    latest_moisture.value
                )

            if light_readings:
                latest_light = max(
                    light_readings,
                    key=lambda row: row.recorded_at,
                )

                light_value = float(
                    latest_light.value
                )

            contexts.append(
                LocationAutomationContext(
                    location_id=location_id,
                    zone_id=zone.id,
                    moisture=moisture_value,
                    low=float(
                        zone.moisture_threshold_low
                    ),
                    high=float(
                        zone.moisture_threshold_high
                    ),
                    light=light_value,
                    zone_name=zone.name,
                )
            )

        return contexts