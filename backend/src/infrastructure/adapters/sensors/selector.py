from domain.devices.entity import Device
from domain.sensors.ports import SensorPort

from infrastructure.adapters.sensors.simulation import (
    SimulationSensorAdapter,
)
from infrastructure.adapters.sensors.vendor_stub import (
    VendorStubSensorAdapter,
)


class SensorAdapterSelector:
    def __init__(self) -> None:
        self._simulation = SimulationSensorAdapter()
        self._vendor_stub = VendorStubSensorAdapter()

    def select(
        self,
        device: Device,
    ) -> SensorPort:
        config = device.default_config or {}

        if config.get("sensor_adapter") == "vendor_stub":
            return self._vendor_stub

        protocol = config.get(
            "protocol",
            "simulation",
        )

        # "sim" is the old Phase 3 value.
        # Treating it as the same thing as "simulation"
        # so already-created devices continue working.
        if protocol in {
            "simulation",
            "sim",
        }:
            return self._simulation

        if protocol == "mqtt":
            raise ValueError(
                "MQTT devices are translated with "
                "MqttSensorAdapter in Phase 5. "
                "No broker is used here."
            )

        raise ValueError(
            f"Unsupported sensor protocol: {protocol}"
        )