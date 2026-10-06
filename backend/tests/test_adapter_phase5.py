from uuid import uuid4

from domain.devices.entity import Device
from infrastructure.adapters.actuators.simulation import (
    SimulationActuatorAdapter,
)
from infrastructure.adapters.sensors.mqtt import (
    MqttSensorAdapter,
)
from infrastructure.adapters.sensors.simulation import (
    SimulationSensorAdapter,
)
from infrastructure.adapters.sensors.vendor_stub import (
    VendorStubSensorAdapter,
)


def make_device(
    *,
    device_type: str = "moisture_sensor",
    protocol: str = "simulation",
) -> Device:
    return Device(
        id=uuid4(),
        device_type=device_type,
        role="sensor",
        device_family="simulation",
        display_name="Test sensor",
        default_config={
            "protocol": protocol
        },
    )


def test_vendor_adapter_normalizes_raw_payload():
    device = make_device()

    adapter = VendorStubSensorAdapter()

    reading = adapter.translate(
        device,
        {
            "result": {
                "readingValue": 0.41,
                "measurementUnit": "vwc",
            }
        },
    )

    assert reading.device_id == device.id
    assert reading.value == 0.41
    assert reading.unit == "vwc"
    assert reading.source == "vendor"


def test_simulation_adapter_value_in_range():
    adapter = SimulationSensorAdapter()

    moisture = adapter.read(
        make_device(
            device_type="moisture_sensor"
        )
    )

    light = adapter.read(
        make_device(
            device_type="light_sensor"
        )
    )

    assert 0.2 <= moisture.value <= 0.6
    assert moisture.unit == "vwc"
    assert moisture.source == "simulation"

    assert 200 <= light.value <= 2000
    assert light.unit == "lux"
    assert light.source == "simulation"


def test_mqtt_adapter_translates_payload():
    device = make_device(
        protocol="mqtt"
    )

    reading = MqttSensorAdapter().translate(
        device,
        {
            "value": 0.41,
            "unit": "vwc",
        },
    )

    assert reading.device_id == device.id
    assert reading.value == 0.41
    assert reading.unit == "vwc"
    assert reading.source == "mqtt"


def test_simulation_actuator_adapter_records_command():
    device_id = uuid4()

    adapter = SimulationActuatorAdapter()

    adapter.apply(
        device_id=device_id,
        command="water",
        payload={
            "seconds": 5
        },
    )

    assert len(
        adapter.commands
    ) == 1

    assert (
        adapter.commands[0].device_id
        == device_id
    )

    assert (
        adapter.commands[0].command
        == "water"
    )

    assert (
        adapter.commands[0].payload
        == {"seconds": 5}
    )