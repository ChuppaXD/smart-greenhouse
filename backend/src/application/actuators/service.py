from typing import Protocol
from uuid import UUID

from application.actuators.dto import (
    ActuatorExecutionDto,
)
from domain.actuators.execution import (
    ActuatorExecution,
)
from domain.actuators.ports import (
    ActuatorPort,
)


class ExecutionLogReader(
    Protocol
):
    def list_recent(
        self,
        limit: int,
    ) -> list[ActuatorExecution]:
        ...


class ActuatorService:
    def __init__(
        self,
        port: ActuatorPort,
        execution_log: ExecutionLogReader,
    ) -> None:
        self._port = port
        self._execution_log = (
            execution_log
        )

    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict,
    ) -> None:
        self._port.apply(
            device_id,
            command,
            payload,
        )

    def list_executions(
        self,
        limit: int,
    ) -> list[ActuatorExecutionDto]:
        executions = (
            self._execution_log.list_recent(
                limit
            )
        )

        return [
            ActuatorExecutionDto(
                id=execution.id,
                device_id=execution.device_id,
                success=execution.success,
                policy_applied=list(
                    execution.policy_applied
                ),
                message=execution.message,
                created_at=execution.created_at,
            )
            for execution in executions
        ]