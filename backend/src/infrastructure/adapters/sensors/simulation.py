import random
from datetime import datetime, timezone

from domain.devices.entity import Device
from domain.sensors.ports import SensorPort
from domain.sensors.reading import Reading


class SimulationSensorAdapter(SensorPort):
    def read(self, device: Device) -> Reading:
        if device.id is None:
            raise ValueError(
                "Cannot read an unpersisted device."
            )

        device_type = device.device_type.lower()

        if "moisture" in device_type:
            value = random.uniform(0.2, 0.6)
            unit = "vwc"

        elif "light" in device_type:
            value = random.uniform(200.0, 2000.0)
            unit = "lux"

        else:
            raise ValueError(
                "Unsupported simulation sensor type: "
                f"{device.device_type}"
            )

        return Reading(
            device_id=device.id,
            value=float(value),
            unit=unit,
            source="simulation",
            recorded_at=datetime.now(timezone.utc),
        )