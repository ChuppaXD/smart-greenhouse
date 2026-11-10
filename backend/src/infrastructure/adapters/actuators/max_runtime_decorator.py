from datetime import (
    datetime,
    timedelta,
    timezone,
)
from typing import Callable
from uuid import UUID

from sqlalchemy.orm import Session

from domain.actuators.errors import (
    ActuatorPolicyViolationError,
)
from domain.actuators.ports import (
    ActuatorPort,
)
from infrastructure.persistence.models import (
    ActuatorStateRow,
)


class MaxRunTimeActuatorDecorator(
    ActuatorPort
):
    def __init__(
        self,
        inner: ActuatorPort,
        session: Session,
        *,
        max_runtime: timedelta = timedelta(
            minutes=30
        ),
        clock: Callable[
            [], datetime
        ]
        | None = None,
    ) -> None:
        self._inner = inner
        self._session = session
        self._max_runtime = max_runtime

        self._clock = (
            clock
            or (
                lambda: datetime.now(
                    timezone.utc
                )
            )
        )

    def apply(
        self,
        device_id: UUID,
        command: str,
        payload: dict,
    ) -> None:
        state_row = self._session.get(
            ActuatorStateRow,
            device_id,
        )

        if (
            state_row is not None
            and state_row.state == "running"
            and state_row.updated_at
            <= (
                self._clock()
                - self._max_runtime
            )
        ):
            raise ActuatorPolicyViolationError(
                "Max run time exceeded",
                policy_name="maxRunTime",
            )

        self._inner.apply(
            device_id,
            command,
            payload,
        )