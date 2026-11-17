from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.persistence.models import (
    CommandLogRow,
)


@dataclass(frozen=True)
class CommandLogEntry:
    id: UUID
    command_type: str
    device_id: UUID
    payload: dict
    status: str
    error_message: str | None
    created_at: datetime


class CommandLogRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def record(
        self,
        *,
        command_type: str,
        device_id: UUID,
        payload: dict,
        status: str,
        error_message: str | None = None,
    ) -> CommandLogEntry:
        row = CommandLogRow(
            command_type=command_type,
            device_id=device_id,
            payload=payload,
            status=status,
            error_message=error_message,
        )

        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)

        return self._to_entry(row)

    def list_recent(
        self,
        limit: int = 50,
    ) -> list[CommandLogEntry]:
        statement = (
            select(CommandLogRow)
            .order_by(
                CommandLogRow.created_at.desc()
            )
            .limit(limit)
        )

        rows = (
            self._session.execute(statement)
            .scalars()
            .all()
        )

        return [
            self._to_entry(row)
            for row in rows
        ]

    @staticmethod
    def _to_entry(
        row: CommandLogRow,
    ) -> CommandLogEntry:
        return CommandLogEntry(
            id=row.id,
            command_type=row.command_type,
            device_id=row.device_id,
            payload=dict(
                row.payload or {}
            ),
            status=row.status,
            error_message=row.error_message,
            created_at=row.created_at,
        )