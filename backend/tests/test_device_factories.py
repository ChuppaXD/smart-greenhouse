from domain.devices.family_factory import (
    EdgeHardwareFactory,
    SimulationDeviceFactory,
)


def test_simulation_factory_returns_four_devices():
    devices = SimulationDeviceFactory().create_device_set()

    assert len(devices) == 4
    assert {device.device_family for device in devices} == {
        "simulation"
    }
    assert {device.role for device in devices} == {
        "sensor",
        "actuator",
    }


def test_edge_factory_differs_from_simulation():
    simulation_devices = (
        SimulationDeviceFactory().create_device_set()
    )

    edge_devices = (
        EdgeHardwareFactory().create_device_set()
    )

    assert len(edge_devices) == 4

    assert {
        device.device_family
        for device in edge_devices
    } == {"edge"}

    simulation_protocols = {
        device.default_config.get("protocol")
        for device in simulation_devices
    }

    edge_protocols = {
        device.default_config.get("protocol")
        for device in edge_devices
    }

    assert simulation_protocols != edge_protocols