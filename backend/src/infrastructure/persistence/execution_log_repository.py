from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.actuators.execution import (
    ActuatorExecution,
)
from infrastructure.persistence.models import (
    ActuatorExecutionLogRow,
)


class ExecutionLogRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def record(
        self,
        *,
        device_id: UUID,
        success: bool,
        policy_applied: Sequence[str],
        message: str | None,
    ) -> ActuatorExecution:
        row = ActuatorExecutionLogRow(
            device_id=device_id,
            success=success,
            policy_applied=list(
                policy_applied
            ),
            message=message,
        )

        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)

        return self._to_domain(row)

    def list_recent(
        self,
        limit: int = 20,
    ) -> list[ActuatorExecution]:
        statement = (
            select(
                ActuatorExecutionLogRow
            )
            .order_by(
                ActuatorExecutionLogRow.created_at.desc()
            )
            .limit(limit)
        )

        rows = (
            self._session.execute(
                statement
            )
            .scalars()
            .all()
        )

        return [
            self._to_domain(row)
            for row in rows
        ]

    @staticmethod
    def _to_domain(
        row: ActuatorExecutionLogRow,
    ) -> ActuatorExecution:
        return ActuatorExecution(
            id=row.id,
            device_id=row.device_id,
            success=row.success,
            policy_applied=list(
                row.policy_applied or []
            ),
            message=row.message,
            created_at=row.created_at,
        )