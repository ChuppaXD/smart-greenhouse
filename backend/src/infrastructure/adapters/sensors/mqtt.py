from datetime import datetime, timezone

from domain.devices.entity import Device
from domain.sensors.reading import Reading


class MqttSensorAdapter:
    def translate(
        self,
        device: Device,
        payload: dict,
    ) -> Reading:
        if device.id is None:
            raise ValueError(
                "Cannot translate data for an unpersisted device."
            )

        if not isinstance(payload, dict):
            raise ValueError(
                "MQTT payload must be a dictionary."
            )

        if "value" not in payload:
            raise ValueError(
                "MQTT payload is missing 'value'."
            )

        if "unit" not in payload:
            raise ValueError(
                "MQTT payload is missing 'unit'."
            )

        try:
            value = float(payload["value"])
        except (
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "MQTT value must be numeric."
            ) from exc

        unit = str(payload["unit"])

        if not unit.strip():
            raise ValueError(
                "MQTT unit must not be empty."
            )

        return Reading(
            device_id=device.id,
            value=value,
            unit=unit,
            source="mqtt",
            recorded_at=datetime.now(timezone.utc),
        )