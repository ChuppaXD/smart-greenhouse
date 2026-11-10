from uuid import UUID

from domain.actuators.errors import (
    ActuatorPolicyViolationError,
)
from domain.actuators.ports import (
    ActuatorPort,
)
from infrastructure.persistence.execution_log_repository import (
    ExecutionLogRepository,
)


class LoggingActuatorDecorator(
    ActuatorPort
):
    def __init__(
        self,
        inner: ActuatorPort,
        log_repository: ExecutionLogRepository,
    ) -> None:
        self._inner = inner
        self._log_repository = (
            log_repository
        )

    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict,
    ) -> None:
        try:
            self._inner.apply(
                device_id,
                command,
                payload,
            )

        except ActuatorPolicyViolationError as exc:
            self._log_repository.record(
                device_id=device_id,
                success=False,
                policy_applied=[
                    exc.policy_name,
                    "logging",
                ],
                message=str(exc),
            )

            raise

        except Exception as exc:
            self._log_repository.record(
                device_id=device_id,
                success=False,
                policy_applied=[
                    "logging"
                ],
                message=str(exc),
            )

            raise

        else:
            self._log_repository.record(
                device_id=device_id,
                success=True,
                policy_applied=[
                    "logging"
                ],
                message=None,
            )