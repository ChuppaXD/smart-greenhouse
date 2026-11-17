from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from domain.actuators.ports import ActuatorPort


@dataclass(frozen=True)
class CommandResult:
    status: str
    error_message: str | None = None


class Command(ABC):
    command_type: str
    target_state: str | None = None

    def __init__(
        self,
        device_id: UUID,
        payload: dict,
    ) -> None:
        self.device_id = device_id
        self.payload = payload

    @abstractmethod
    def execute(
        self,
        port: ActuatorPort,
    ) -> None:
        ...