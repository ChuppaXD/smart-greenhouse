from uuid import UUID

from application.devices.dto import DeviceDto
from application.devices.mappers import device_to_dto
from domain.actuators.context import ActuatorContext
from infrastructure.persistence.actuator_state_repository import (
    ActuatorStateRepository,
)
from infrastructure.persistence.device_repository import (
    DeviceRepository,
)


class ActuatorStateService:
    def __init__(
        self,
        device_repository: DeviceRepository,
        state_repository: ActuatorStateRepository,
    ):
        self._devices = device_repository
        self._states = state_repository

    def get_status(
        self,
        device_id: UUID,
    ) -> DeviceDto:
        device = self._devices.get_device(
            device_id
        )

        if (
            device is None
            or device.role != "actuator"
        ):
            raise LookupError(
                f"Actuator {device_id} was not found."
            )

        return device_to_dto(device)

    def transition(
        self,
        device_id: UUID,
        target: str,
    ) -> DeviceDto:
        device = self._devices.get_device(
            device_id
        )

        if (
            device is None
            or device.role != "actuator"
        ):
            raise LookupError(
                f"Actuator {device_id} was not found."
            )

        current_state = (
            self._states.get_state(
                device_id
            )
        )

        if current_state is None:
            raise LookupError(
                f"Actuator state for device "
                f"{device_id} was not found."
            )

        context = (
            ActuatorContext.from_state_name(
                device_type=device.device_type,
                state=current_state,
            )
        )

        # The domain validates the transition
        # before the repository saves it.
        context.transition(target)

        self._states.set_state(
            device_id=device_id,
            state=context.state,
        )

        updated_device = (
            self._devices.get_device(
                device_id
            )
        )

        if updated_device is None:
            raise LookupError(
                f"Actuator {device_id} was not found "
                "after transition."
            )

        return device_to_dto(
            updated_device
        )