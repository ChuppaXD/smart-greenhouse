from abc import ABC, abstractmethod

from domain.devices.entity import Device
from domain.sensors.creators import (
    LightSensorCreator,
    MoistureSensorCreator,
)


class DeviceFamilyFactory(ABC):
    @property
    @abstractmethod
    def family_key(self) -> str:
        ...


    @abstractmethod
    def create_device_set(self) -> list[Device]:
        ...


class SimulationDeviceFactory(DeviceFamilyFactory):
    @property
    def family_key(self) -> str:
        return "simulation"


    def create_device_set(self) -> list[Device]:
        moisture_sensor = MoistureSensorCreator().create_sensor(
            display_name="Sim soil moisture sensor",
        )

        moisture_config = dict(moisture_sensor.default_config)
        moisture_config["protocol"] = "sim"

        light_sensor = LightSensorCreator().create_sensor(
            display_name="Sim light sensor",
        )

        light_config = dict(light_sensor.default_config)
        light_config["protocol"] = "sim"

        return [
            Device(
                id=None,
                device_type=moisture_sensor.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=moisture_sensor.display_name,
                default_config=moisture_config,
            ),
            Device(
                id=None,
                device_type=light_sensor.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=light_sensor.display_name,
                default_config=light_config,
            ),
            Device(
                id=None,
                device_type="water_pump",
                role="actuator",
                device_family=self.family_key,
                display_name="Sim irrigation pump",
                default_config={
                    "protocol": "sim",
                    "mode": "simulated",
                    "flow_lpm": 2,
                },
            ),
            Device(
                id=None,
                device_type="grow_light",
                role="actuator",
                device_family=self.family_key,
                display_name="Sim grow light",
                default_config={
                    "protocol": "sim",
                    "mode": "simulated",
                    "spectrum": "full",
                },
            ),
        ]


class EdgeHardwareFactory(DeviceFamilyFactory):
    @property
    def family_key(self) -> str:
        return "edge"


    def create_device_set(self) -> list[Device]:
        moisture_sensor = MoistureSensorCreator().create_sensor(
            display_name="Edge soil moisture sensor",
        )

        moisture_config = dict(moisture_sensor.default_config)
        moisture_config["protocol"] = "gpio-stub"

        light_sensor = LightSensorCreator().create_sensor(
            display_name="Edge light sensor",
        )

        light_config = dict(light_sensor.default_config)
        light_config["protocol"] = "gpio-stub"
        light_config["sampling_interval_seconds"] = 30

        return [
            Device(
                id=None,
                device_type=moisture_sensor.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=moisture_sensor.display_name,
                default_config=moisture_config,
            ),
            Device(
                id=None,
                device_type=light_sensor.device_type,
                role="sensor",
                device_family=self.family_key,
                display_name=light_sensor.display_name,
                default_config=light_config,
            ),
            Device(
                id=None,
                device_type="water_pump",
                role="actuator",
                device_family=self.family_key,
                display_name="Edge irrigation pump",
                default_config={
                    "protocol": "gpio-stub",
                    "control_pin": 17,
                },
            ),
            Device(
                id=None,
                device_type="grow_light",
                role="actuator",
                device_family=self.family_key,
                display_name="Edge grow light",
                default_config={
                    "protocol": "gpio-stub",
                    "control_pin": 18,
                },
            ),
        ]


_FAMILY_FACTORIES: dict[str, DeviceFamilyFactory] = {
    "simulation": SimulationDeviceFactory(),
    "edge": EdgeHardwareFactory(),
}


def get_family_factory(family: str) -> DeviceFamilyFactory:
    try:
        return _FAMILY_FACTORIES[family]
    except KeyError as exc:
        raise ValueError(f"Unknown device family: {family}") from exc