from datetime import datetime, timedelta

from application.readings.service import ReadingIngest
from infrastructure.persistence.device_repository import (
    DeviceRepository,
)
from infrastructure.persistence.reading_repository import (
    ReadingRepository,
)


class SimulationSampler:
    def __init__(
        self,
        device_repository: DeviceRepository,
        reading_repository: ReadingRepository,
        reading_ingest: ReadingIngest,
    ):
        self._devices = device_repository
        self._readings = reading_repository
        self._ingest = reading_ingest

    def run_once(
        self,
        now: datetime,
    ) -> None:
        if now.tzinfo is None:
            raise ValueError(
                "Sampler time must be timezone-aware."
            )

        devices = self._devices.list_devices(
            role="sensor"
        )

        for device in devices:
            if device.id is None:
                continue

            if not device.tracking_enabled:
                continue

            config = device.default_config or {}

            protocol = config.get(
                "protocol",
                "simulation",
            )

            if protocol not in {
                "simulation",
                "sim",
            }:
                continue

            if (
                config.get("sensor_adapter")
                == "vendor_stub"
            ):
                continue

            latest = (
                self._readings.latest_for_device(
                    device.id
                )
            )

            if latest is not None:
                elapsed = (
                    now - latest.recorded_at
                )

                if elapsed < timedelta(
                    seconds=(
                        device
                        .sampling_interval_seconds
                    )
                ):
                    continue

            self._ingest.take_reading(
                device.id,
                recorded_at=now,
            )