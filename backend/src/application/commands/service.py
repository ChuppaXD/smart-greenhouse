from uuid import UUID

from domain.actuators.context import (
    ActuatorContext,
)
from domain.actuators.errors import (
    ActuatorPolicyViolationError,
)
from domain.actuators.ports import (
    ActuatorPort,
)
from domain.commands.invoker import (
    CommandInvoker,
)
from domain.commands.registry import (
    command_for,
)
from infrastructure.persistence.command_log_repository import (
    CommandLogEntry,
    CommandLogRepository,
)
from infrastructure.persistence.device_repository import (
    DeviceRepository,
)


class CommandRejectedError(
    RuntimeError
):
    def __init__(
        self,
        entry: CommandLogEntry,
    ) -> None:
        super().__init__(
            "Command is not allowed in the current state."
        )

        self.entry = entry


class CommandService:
    def __init__(
        self,
        *,
        device_repository: DeviceRepository,
        state_repository,
        command_log_repository: CommandLogRepository,
        port: ActuatorPort,
        invoker: CommandInvoker,
    ) -> None:
        self._device_repository = (
            device_repository
        )

        self._state_repository = (
            state_repository
        )

        self._command_log_repository = (
            command_log_repository
        )

        self._port = port
        self._invoker = invoker

    def execute(
        self,
        *,
        command_type: str,
        device_id: UUID,
        payload: dict,
    ) -> CommandLogEntry:
        # 1. Convert the type string into a Command object.
        command = command_for(
            command_type,
            device_id,
            payload,
        )

        # 2. Check that the device exists and is an actuator.
        device = (
            self._device_repository.get_device(
                device_id
            )
        )

        if (
            device is None
            or device.role != "actuator"
        ):
            raise LookupError(
                f"Actuator {device_id} was not found."
            )

        # 3. Load the persisted Phase 8 state.
        #
        # IMPORTANT:
        # get_state() returns the state string,
        # not an ActuatorStateRow.
        current_state = (
            self._state_repository.get_state(
                device_id
            )
        )

        if current_state is None:
            raise LookupError(
                f"Actuator state for {device_id} "
                "was not found."
            )

        # 4. Use the existing State pattern.
        context = ActuatorContext.from_state_name(
            device.device_type,
            current_state,
        )

        # 5. State guard.
        if (
            command_type
            not in context.allowed_commands()
        ):
            entry = (
                self._command_log_repository.record(
                    command_type=command_type,
                    device_id=device_id,
                    payload=payload,
                    status="rejected",
                    error_message=(
                        "Command is not allowed "
                        "in the current state."
                    ),
                )
            )

            raise CommandRejectedError(
                entry
            )

        # 6. Execute through the Phase 9
        # decorated ActuatorPort.
        try:
            self._invoker.run(
                command,
                self._port,
            )

        except ActuatorPolicyViolationError as exc:
            return (
                self._command_log_repository.record(
                    command_type=command_type,
                    device_id=device_id,
                    payload=payload,
                    status="failed",
                    error_message=str(exc),
                )
            )

        except Exception as exc:
            return (
                self._command_log_repository.record(
                    command_type=command_type,
                    device_id=device_id,
                    payload=payload,
                    status="failed",
                    error_message=str(exc),
                )
            )

        # 7. Only after the decorated port
        # succeeds do we change lifecycle state.
        if (
            command.target_state is not None
            and command.target_state
            != current_state
        ):
            context.transition(
                command.target_state
            )

            self._state_repository.set_state(
                device_id,
                command.target_state,
            )

        # 8. Finally record success.
        return (
            self._command_log_repository.record(
                command_type=command_type,
                device_id=device_id,
                payload=payload,
                status="success",
                error_message=None,
            )
        )