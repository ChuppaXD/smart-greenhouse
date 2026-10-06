from dataclasses import dataclass
from uuid import UUID


@dataclass
class Sensor:
    id: UUID | None
    device_type: str
    display_name: str
    default_config: dict
    sampling_interval_seconds: int = 300
    tracking_enabled: bool = True