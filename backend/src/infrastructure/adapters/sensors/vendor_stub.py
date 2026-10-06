from datetime import datetime, timezone

from domain.devices.entity import Device
from domain.sensors.ports import SensorPort
from domain.sensors.reading import Reading


class VendorStubSensorAdapter(SensorPort):
    def read(self, device: Device) -> Reading:
        raw_payload = self._get_raw_payload(device)

        return self.translate(
            device,
            raw_payload,
        )

    def translate(
        self,
        device: Device,
        payload: dict,
    ) -> Reading:
        if device.id is None:
            raise ValueError(
                "Cannot read an unpersisted device."
            )

        try:
            result = payload["result"]
            value = float(
                result["readingValue"]
            )
            unit = str(
                result["measurementUnit"]
            )
        except (
            KeyError,
            TypeError,
            ValueError,
        ) as exc:
            raise ValueError(
                "Invalid vendor payload."
            ) from exc

        return Reading(
            device_id=device.id,
            value=value,
            unit=unit,
            source="vendor",
            recorded_at=datetime.now(timezone.utc),
        )

    def _get_raw_payload(
        self,
        device: Device,
    ) -> dict:
        device_type = device.device_type.lower()

        if "moisture" in device_type:
            return {
                "result": {
                    "readingValue": 0.41,
                    "measurementUnit": "vwc",
                }
            }

        if "light" in device_type:
            return {
                "result": {
                    "readingValue": 850.0,
                    "measurementUnit": "lux",
                }
            }

        raise ValueError(
            "Unsupported vendor sensor type: "
            f"{device.device_type}"
        )