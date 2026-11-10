from datetime import (
    datetime,
    timedelta,
    timezone,
)
from types import SimpleNamespace
from uuid import uuid4

import pytest

from domain.actuators.ports import (
    ActuatorPort,
)
from infrastructure.adapters.actuators.logging_decorator import (
    LoggingActuatorDecorator,
)
from infrastructure.adapters.actuators.max_runtime_decorator import (
    MaxRunTimeActuatorDecorator,
)


class SpyActuator(
    ActuatorPort
):
    def __init__(self) -> None:
        self.calls = 0

    def apply(
        self,
        device_id,
        command,
        payload,
    ) -> None:
        self.calls += 1


class FakeSession:
    def __init__(
        self,
        state,
    ) -> None:
        self.state = state

    def get(
        self,
        model,
        device_id,
    ):
        return self.state


class FakeLogRepository:
    def __init__(self) -> None:
        self.rows = []

    def record(
        self,
        **kwargs,
    ):
        self.rows.append(
            kwargs
        )


def make_running_state(
    minutes_old: int,
):
    return SimpleNamespace(
        state="running",
        updated_at=(
            datetime.now(
                timezone.utc
            )
            - timedelta(
                minutes=minutes_old
            )
        ),
    )


def test_max_runtime_does_not_call_inner():
    inner = SpyActuator()

    session = FakeSession(
        make_running_state(31)
    )

    decorator = (
        MaxRunTimeActuatorDecorator(
            inner,
            session,
        )
    )

    with pytest.raises(
        RuntimeError,
        match="Max run time exceeded",
    ):
        decorator.apply(
            uuid4(),
            "start_pump",
            {},
        )

    assert inner.calls == 0


def test_failed_policy_writes_execution_row():
    inner = SpyActuator()

    session = FakeSession(
        make_running_state(31)
    )

    log_repository = (
        FakeLogRepository()
    )

    decorated = (
        LoggingActuatorDecorator(
            MaxRunTimeActuatorDecorator(
                inner,
                session,
            ),
            log_repository,
        )
    )

    device_id = uuid4()

    with pytest.raises(
        RuntimeError,
        match="Max run time exceeded",
    ):
        decorated.apply(
            device_id,
            "start_pump",
            {},
        )

    assert inner.calls == 0

    assert log_repository.rows == [
        {
            "device_id": device_id,
            "success": False,
            "policy_applied": [
                "maxRunTime",
                "logging",
            ],
            "message": (
                "Max run time exceeded"
            ),
        }
    ]


def test_successful_apply_writes_execution_row():
    inner = SpyActuator()

    session = FakeSession(
        SimpleNamespace(
            state="idle",
            updated_at=(
                datetime.now(
                    timezone.utc
                )
            ),
        )
    )

    log_repository = (
        FakeLogRepository()
    )

    decorated = (
        LoggingActuatorDecorator(
            MaxRunTimeActuatorDecorator(
                inner,
                session,
            ),
            log_repository,
        )
    )

    device_id = uuid4()

    decorated.apply(
        device_id,
        "anything",
        {},
    )

    assert inner.calls == 1

    assert log_repository.rows[0] == {
        "device_id": device_id,
        "success": True,
        "policy_applied": [
            "logging"
        ],
        "message": None,
    }