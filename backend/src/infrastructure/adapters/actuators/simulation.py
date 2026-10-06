from dataclasses import dataclass
from uuid import UUID

from domain.actuators.ports import ActuatorPort


@dataclass(frozen=True)
class AppliedCommand:
    device_id: UUID
    command: str
    payload: dict


class SimulationActuatorAdapter(ActuatorPort):
    def __init__(self) -> None:
        self.commands: list[AppliedCommand] = []

    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict,
    ) -> None:
        self.commands.append(
            AppliedCommand(
                device_id=device_id,
                command=command,
                payload=dict(payload),
            )
        )