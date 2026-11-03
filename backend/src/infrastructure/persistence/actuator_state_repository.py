from uuid import UUID

from sqlalchemy.orm import Session

from infrastructure.persistence.models import (
    ActuatorStateRow,
)


class ActuatorStateRepository:
    def __init__(
        self,
        session: Session,
    ):
        self._session = session

    def get_state(
        self,
        device_id: UUID,
    ) -> str | None:
        row = self._session.get(
            ActuatorStateRow,
            device_id,
        )

        if row is None:
            return None

        return row.state

    def set_state(
        self,
        device_id: UUID,
        state: str,
    ) -> None:
        row = self._session.get(
            ActuatorStateRow,
            device_id,
        )

        if row is None:
            raise LookupError(
                f"Actuator state for device {device_id} was not found."
            )

        try:
            row.state = state

            self._session.commit()
            self._session.refresh(row)

        except Exception:
            self._session.rollback()
            raise