from uuid import UUID

from domain.devices.entity import Device
from infrastructure.persistence.device_repository import (
    DeviceRepository,
)


class ZoneAssignmentService:
    def __init__(
        self,
        repository: DeviceRepository,
    ):
        self._repo = repository

    def assign(
        self,
        device_id: UUID,
        zone_id: UUID | None,
    ) -> None:
        device = self._repo.get_device_row(device_id)

        if device is None:
            raise LookupError("Device not found.")

        if zone_id is not None:
            zone = self._repo.get_zone_row(zone_id)

            if zone is None:
                raise LookupError("Zone not found.")

        self._repo.assign_device_to_zone(
            device_id,
            zone_id,
        )

    def list_devices(
        self,
        location_id: UUID,
        zone_id: UUID,
    ) -> list[Device]:
        zone = self._repo.get_zone_in_location(
            location_id,
            zone_id,
        )

        if zone is None:
            raise LookupError(
                "Zone not found in this location."
            )

        return self._repo.list_devices_in_zone(
            zone_id
        )