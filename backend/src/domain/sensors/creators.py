from abc import ABC, abstractmethod

from domain.sensors.entity import Sensor


class SensorCreator(ABC):
    @abstractmethod
    def create_sensor(
        self,
        display_name: str | None = None,
    ) -> Sensor:
        ...


class MoistureSensorCreator(SensorCreator):
    def create_sensor(
        self,
        display_name: str | None = None,
    ) -> Sensor:
        return Sensor(
            id=None,
            device_type="moisture_sensor",
            display_name=display_name or "Soil moisture sensor",
            default_config={
                "sampling_interval_seconds": 300,
                "protocol": "simulation",
                "unit": "vwc",
                "threshold": 40,
            },
            sampling_interval_seconds=300,
            tracking_enabled=True,
        )


class LightSensorCreator(SensorCreator):
    def create_sensor(
        self,
        display_name: str | None = None,
    ) -> Sensor:
        return Sensor(
            id=None,
            device_type="light_sensor",
            display_name=display_name or "Light sensor",
            default_config={
                "sampling_interval_seconds": 60,
                "protocol": "simulation",
                "unit": "lux",
            },
            sampling_interval_seconds=60,
            tracking_enabled=True,
        )


_CREATORS: dict[str, SensorCreator] = {
    "moisture": MoistureSensorCreator(),
    "light": LightSensorCreator(),
}


def get_creator(sensor_type: str) -> SensorCreator:
    try:
        return _CREATORS[sensor_type]
    except KeyError as exc:
        raise ValueError(f"Unknown sensor type: {sensor_type}") from exc