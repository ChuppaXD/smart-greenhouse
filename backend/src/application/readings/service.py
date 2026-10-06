from dataclasses import replace
from datetime import datetime
from uuid import UUID

from application.readings.dto import ReadingDto
from domain.devices.entity import Device
from domain.sensors.ports import SensorPort
from domain.sensors.reading import Reading
from infrastructure.adapters.sensors.selector import (
    SensorAdapterSelector,
)
from infrastructure.persistence.device_repository import (
    DeviceRepository,
)
from infrastructure.persistence.reading_repository import (
    ReadingRepository,
)


class DeviceNotFoundError(LookupError):
    pass


class ReadingIngest:
    def __init__(
        self,
        device_repository: DeviceRepository,
        reading_repository: ReadingRepository,
        adapter_selector: SensorAdapterSelector,
    ):
        self._devices = device_repository
        self._readings = reading_repository
        self._selector = adapter_selector

    def take_reading(
        self,
        device_id: UUID,
        recorded_at: datetime | None = None,
    ) -> ReadingDto:
        device = self._get_sensor(
            device_id
        )

        port: SensorPort = (
            self._selector.select(device)
        )

        reading = port.read(device)

        if recorded_at is not None:
            reading = replace(
                reading,
                recorded_at=recorded_at,
            )

        return self.record(
            device_id,
            reading,
        )

    def record(
        self,
        device_id: UUID,
        reading: Reading,
    ) -> ReadingDto:
        self._get_sensor(device_id)

        if reading.device_id != device_id:
            raise ValueError(
                "Reading device_id does not match "
                "the requested device."
            )

        saved = self._readings.insert(
            reading
        )

        return ReadingDto(
            device_id=saved.device_id,
            value=saved.value,
            unit=saved.unit,
            source=saved.source,
            recorded_at=saved.recorded_at,
        )

    def list_readings(
        self,
        device_id: UUID,
        limit: int = 20,
    ) -> list[ReadingDto]:
        self._get_sensor(device_id)

        readings = (
            self._readings.list_for_device(
                device_id,
                limit,
            )
        )

        return [
            ReadingDto(
                device_id=reading.device_id,
                value=reading.value,
                unit=reading.unit,
                source=reading.source,
                recorded_at=reading.recorded_at,
            )
            for reading in readings
        ]

    def _get_sensor(
        self,
        device_id: UUID,
    ) -> Device:
        device = self._devices.get_device(
            device_id
        )

        if device is None:
            raise DeviceNotFoundError(
                f"Device {device_id} was not found."
            )

        if device.role != "sensor":
            raise ValueError(
                f"Device {device_id} is not a sensor."
            )

        return device