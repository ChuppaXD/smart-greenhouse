from datetime import (
    datetime,
    timezone,
)
from types import (
    SimpleNamespace,
)
from uuid import uuid4

import pytest

from application.commands.service import (
    CommandRejectedError,
    CommandService,
)
from domain.actuators.errors import (
    ActuatorPolicyViolationError,
)
from domain.commands.invoker import (
    CommandInvoker,
)


class FakeDeviceRepository:
    def __init__(
        self,
        device,
    ) -> None:
        self.device = device

    def get_device(
        self,
        device_id,
    ):
        return self.device


class FakeStateRepository:
    def __init__(
        self,
        state: str,
    ) -> None:
        self.state = state
        self.saved_states = []

    def get_state(
        self,
        device_id,
    ):
        return self.state

    def set_state(
        self,
        device_id,
        state,
    ):
        self.saved_states.append(
            (
                device_id,
                state,
            )
        )

        self.state = state


class FakeCommandLogRepository:
    def __init__(self) -> None:
        self.entries = []

    def record(
        self,
        **kwargs,
    ):
        entry = SimpleNamespace(
            id=uuid4(),
            created_at=datetime.now(
                timezone.utc
            ),
            **kwargs,
        )

        self.entries.append(entry)

        return entry


class FakePort:
    def __init__(self) -> None:
        self.calls = []

    def apply(
        self,
        device_id,
        command,
        payload,
    ):
        self.calls.append(
            (
                device_id,
                command,
                payload,
            )
        )


class FailingPort:
    def apply(
        self,
        device_id,
        command,
        payload,
    ):
        raise ActuatorPolicyViolationError(
            "Max run time exceeded",
            policy_name="maxRunTime",
        )


def make_service(
    *,
    state: str,
    port=None,
    device_type: str = "water_pump",
):
    device_id = uuid4()

    device = SimpleNamespace(
        id=device_id,
        role="actuator",
        device_type=device_type,
    )

    device_repository = (
        FakeDeviceRepository(
            device
        )
    )

    state_repository = (
        FakeStateRepository(state)
    )

    command_log_repository = (
        FakeCommandLogRepository()
    )

    actual_port = (
        port
        if port is not None
        else FakePort()
    )

    service = CommandService(
        device_repository=(
            device_repository
        ),
        state_repository=(
            state_repository
        ),
        command_log_repository=(
            command_log_repository
        ),
        port=actual_port,
        invoker=CommandInvoker(),
    )

    return (
        service,
        device_id,
        state_repository,
        command_log_repository,
        actual_port,
    )


def test_illegal_command_rejected_logged():
    (
        service,
        device_id,
        state_repository,
        command_log_repository,
        port,
    ) = make_service(
        state="idle"
    )

    with pytest.raises(
        CommandRejectedError
    ):
        service.execute(
            command_type="stop_pump",
            device_id=device_id,
            payload={},
        )

    assert (
        state_repository.saved_states
        == []
    )

    assert port.calls == []

    assert (
        command_log_repository
        .entries[0]
        .status
        == "rejected"
    )


def test_start_pump_transitions_to_running():
    (
        service,
        device_id,
        state_repository,
        command_log_repository,
        port,
    ) = make_service(
        state="idle"
    )

    result = service.execute(
        command_type="start_pump",
        device_id=device_id,
        payload={},
    )

    assert result.status == "success"

    assert (
        state_repository.state
        == "running"
    )

    assert (
        state_repository.saved_states
        == [
            (
                device_id,
                "running",
            )
        ]
    )

    assert len(port.calls) == 1

    assert (
        command_log_repository
        .entries[0]
        .status
        == "success"
    )


def test_set_light_level_keeps_running_state():
    (
        service,
        device_id,
        state_repository,
        command_log_repository,
        port,
    ) = make_service(
        state="running",
        device_type="grow_light",
    )

    result = service.execute(
        command_type="set_light_level",
        device_id=device_id,
        payload={
            "level": 1
        },
    )

    assert result.status == "success"

    assert (
        state_repository.state
        == "running"
    )

    assert (
        state_repository.saved_states
        == []
    )

    assert len(port.calls) == 1


def test_policy_failure_is_failed_and_state_is_unchanged():
    failing_port = FailingPort()

    (
        service,
        device_id,
        state_repository,
        command_log_repository,
        _,
    ) = make_service(
        state="running",
        port=failing_port,
        device_type="grow_light",
    )

    result = service.execute(
        command_type="set_light_level",
        device_id=device_id,
        payload={
            "level": 1
        },
    )

    assert result.status == "failed"

    assert (
        result.error_message
        == "Max run time exceeded"
    )

    assert (
        state_repository.state
        == "running"
    )

    assert (
        state_repository.saved_states
        == []
    )