from domain.sensors.creators import (
    LightSensorCreator,
    MoistureSensorCreator,
)


def test_moisture_creator_defaults():
    sensor = MoistureSensorCreator().create_sensor()

    assert sensor.device_type == "moisture_sensor"
    assert "threshold" in sensor.default_config


def test_light_creator_defaults():
    sensor = LightSensorCreator().create_sensor()

    assert sensor.device_type == "light_sensor"
    assert sensor.default_config["unit"] != "vwc"