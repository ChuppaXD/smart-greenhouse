from datetime import (
    datetime,
    timedelta,
    timezone,
)
from uuid import UUID, uuid4

from application.readings.sampler import (
    SimulationSampler,
)
from domain.devices.entity import Device
from domain.sensors.reading import Reading


class FakeDeviceRepository:
    def __init__(
        self,
        devices: list[Device],
    ):
        self._devices = devices

    def list_devices(
        self,
        *,
        device_family: str | None = None,
        role: str | None = None,
    ) -> list[Device]:
        result = self._devices

        if device_family is not None:
            result = [
                device
                for device in result
                if device.device_family
                == device_family
            ]

        if role is not None:
            result = [
                device
                for device in result
                if device.role == role
            ]

        return result


class FakeReadingRepository:
    def __init__(self):
        self._readings: dict[
            UUID,
            list[Reading],
        ] = {}

    def latest_for_device(
        self,
        device_id: UUID,
    ) -> Reading | None:
        rows = self._readings.get(
            device_id,
            [],
        )

        if not rows:
            return None

        return rows[-1]

    def add(
        self,
        reading: Reading,
    ) -> None:
        self._readings.setdefault(
            reading.device_id,
            [],
        ).append(reading)

    def count(
        self,
        device_id: UUID,
    ) -> int:
        return len(
            self._readings.get(
                device_id,
                [],
            )
        )


class FakeReadingIngest:
    def __init__(
        self,
        repository: FakeReadingRepository,
    ):
        self._repository = repository

    def take_reading(
        self,
        device_id: UUID,
        recorded_at: datetime | None = None,
    ) -> None:
        if recorded_at is None:
            raise AssertionError(
                "The sampler should provide its test clock."
            )

        self._repository.add(
            Reading(
                device_id=device_id,
                value=0.4,
                unit="vwc",
                source="simulation",
                recorded_at=recorded_at,
            )
        )


def make_device(
    *,
    protocol: str = "simulation",
    tracking_enabled: bool = True,
    interval: int = 30,
) -> Device:
    return Device(
        id=uuid4(),
        device_type="moisture_sensor",
        role="sensor",
        device_family="simulation",
        display_name="Test sensor",
        default_config={
            "protocol": protocol
        },
        sampling_interval_seconds=interval,
        tracking_enabled=tracking_enabled,
    )


def test_sampler_respects_interval_and_tracking():
    simulation = make_device(
        interval=30
    )

    disabled = make_device(
        tracking_enabled=False
    )

    mqtt = make_device(
        protocol="mqtt"
    )

    reading_repository = (
        FakeReadingRepository()
    )

    sampler = SimulationSampler(
        device_repository=(
            FakeDeviceRepository(
                [
                    simulation,
                    disabled,
                    mqtt,
                ]
            )
        ),
        reading_repository=(
            reading_repository
        ),
        reading_ingest=FakeReadingIngest(
            reading_repository
        ),
    )

    first = datetime(
        2026,
        9,
        30,
        12,
        0,
        tzinfo=timezone.utc,
    )

    sampler.run_once(first)

    assert (
        reading_repository.count(
            simulation.id
        )
        == 1
    )

    assert (
        reading_repository.count(
            disabled.id
        )
        == 0
    )

    assert (
        reading_repository.count(
            mqtt.id
        )
        == 0
    )

    sampler.run_once(
        first
        + timedelta(seconds=10)
    )

    assert (
        reading_repository.count(
            simulation.id
        )
        == 1
    )

    sampler.run_once(
        first
        + timedelta(seconds=30)
    )

    assert (
        reading_repository.count(
            simulation.id
        )
        == 2
    )