from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.devices.entity import Device
from domain.sensors.entity import Sensor
from infrastructure.persistence.models import (
    DeviceRow,
    ZoneRow,
)


class DeviceRepository:
    def __init__(
        self,
        session: Session,
    ):
        self._session = session

    def save_device(
        self,
        device: Device,
    ) -> Device:
        row = DeviceRow(
            device_type=device.device_type,
            role=device.role,
            device_family=device.device_family,
            sampling_interval_seconds=(
                self._resolve_sampling_interval(device)
            ),
            tracking_enabled=device.tracking_enabled,
            zone_id=device.zone_id,
            location_id=device.location_id,
            display_name=device.display_name,
            default_config=device.default_config,
        )

        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)

        return self._to_device(row)

    def save_devices(
        self,
        devices: list[Device],
    ) -> list[Device]:
        rows = [
            DeviceRow(
                device_type=device.device_type,
                role=device.role,
                device_family=device.device_family,
                sampling_interval_seconds=(
                    self._resolve_sampling_interval(device)
                ),
                tracking_enabled=device.tracking_enabled,
                zone_id=device.zone_id,
                location_id=device.location_id,
                display_name=device.display_name,
                default_config=device.default_config,
            )
            for device in devices
        ]

        self._session.add_all(rows)
        self._session.commit()

        for row in rows:
            self._session.refresh(row)

        return [
            self._to_device(row)
            for row in rows
        ]

    def list_devices(
        self,
        *,
        device_family: str | None = None,
        role: str | None = None,
    ) -> list[Device]:
        statement = select(DeviceRow)

        if device_family is not None:
            statement = statement.where(
                DeviceRow.device_family
                == device_family
            )

        if role is not None:
            statement = statement.where(
                DeviceRow.role == role
            )

        statement = statement.order_by(
            DeviceRow.created_at.desc()
        )

        rows = (
            self._session.execute(statement)
            .scalars()
            .all()
        )

        return [
            self._to_device(row)
            for row in rows
        ]

    def get_device(
        self,
        device_id: UUID,
    ) -> Device | None:
        row = self.get_device_row(device_id)

        if row is None:
            return None

        return self._to_device(row)

    def update_sampling(
        self,
        device_id: UUID,
        sampling_interval_seconds: int,
        tracking_enabled: bool,
    ) -> Device | None:
        row = self.get_device_row(device_id)

        if row is None:
            return None

        try:
            row.sampling_interval_seconds = (
                sampling_interval_seconds
            )
            row.tracking_enabled = (
                tracking_enabled
            )

            self._session.commit()
            self._session.refresh(row)

        except Exception:
            self._session.rollback()
            raise

        return self._to_device(row)

    # Phase 2 compatibility
    def save_sensor(
        self,
        sensor: Sensor,
    ) -> Sensor:
        row = DeviceRow(
            device_type=sensor.device_type,
            role="sensor",
            device_family="simulation",
            sampling_interval_seconds=(
                sensor.sampling_interval_seconds
            ),
            tracking_enabled=sensor.tracking_enabled,
            zone_id=None,
            location_id=None,
            display_name=sensor.display_name,
            default_config=sensor.default_config,
        )

        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)

        return Sensor(
            id=row.id,
            device_type=row.device_type,
            display_name=row.display_name or "",
            default_config=row.default_config,
            sampling_interval_seconds=(
                row.sampling_interval_seconds
            ),
            tracking_enabled=row.tracking_enabled,
        )

    # Phase 2 compatibility
    def list_sensors(self) -> list[Sensor]:
        statement = (
            select(DeviceRow)
            .where(
                DeviceRow.role == "sensor"
            )
            .order_by(
                DeviceRow.created_at.desc()
            )
        )

        rows = (
            self._session.execute(statement)
            .scalars()
            .all()
        )

        return [
            Sensor(
                id=row.id,
                device_type=row.device_type,
                display_name=row.display_name or "",
                default_config=row.default_config,
                sampling_interval_seconds=(
                    row.sampling_interval_seconds
                ),
                tracking_enabled=row.tracking_enabled,
            )
            for row in rows
        ]

    def get_device_row(
        self,
        device_id: UUID,
    ) -> DeviceRow | None:
        return self._session.get(
            DeviceRow,
            device_id,
        )

    def get_zone_row(
        self,
        zone_id: UUID,
    ) -> ZoneRow | None:
        return self._session.get(
            ZoneRow,
            zone_id,
        )

    def get_zone_in_location(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> ZoneRow | None:
        statement = (
            select(ZoneRow)
            .where(
                ZoneRow.id == zone_id,
                ZoneRow.location_id
                == location_id,
            )
        )

        return (
            self._session.execute(statement)
            .scalars()
            .first()
        )

    def assign_device_to_zone(
        self,
        device_id: UUID,
        zone_id: UUID | None,
    ) -> None:
        device = self.get_device_row(
            device_id
        )

        if device is None:
            raise LookupError(
                "Device not found."
            )

        try:
            if zone_id is None:
                device.zone_id = None
                device.location_id = None

            else:
                zone = self.get_zone_row(
                    zone_id
                )

                if zone is None:
                    raise LookupError(
                        "Zone not found."
                    )

                device.zone_id = zone.id
                device.location_id = (
                    zone.location_id
                )

            self._session.commit()

        except Exception:
            self._session.rollback()
            raise

    def list_devices_in_zone(
        self,
        zone_id: UUID,
    ) -> list[Device]:
        statement = (
            select(DeviceRow)
            .where(
                DeviceRow.zone_id == zone_id
            )
            .order_by(
                DeviceRow.created_at.desc()
            )
        )

        rows = (
            self._session.execute(statement)
            .scalars()
            .all()
        )

        return [
            self._to_device(row)
            for row in rows
        ]

    @staticmethod
    def _resolve_sampling_interval(
        device: Device,
    ) -> int:
        configured = (
            device.default_config or {}
        ).get("sampling_interval_seconds")

        if isinstance(
            configured,
            (int, float),
        ) and not isinstance(
            configured,
            bool,
        ):
            configured_int = int(
                configured
            )

            if configured_int >= 5:
                return configured_int

        return device.sampling_interval_seconds

    @staticmethod
    def _to_device(
        row: DeviceRow,
    ) -> Device:
        return Device(
            id=row.id,
            device_type=row.device_type,
            role=row.role,
            device_family=row.device_family,
            display_name=row.display_name or "",
            default_config=row.default_config,
            zone_id=row.zone_id,
            location_id=row.location_id,
            sampling_interval_seconds=(
                row.sampling_interval_seconds
            ),
            tracking_enabled=(
                row.tracking_enabled
            ),
        )