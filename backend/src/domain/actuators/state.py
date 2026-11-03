from __future__ import annotations

from abc import ABC


class IllegalTransitionError(ValueError):
    """Raised when an actuator cannot move to the requested state."""


class ActuatorState(ABC):
    """State interface for the actuator lifecycle."""

    name: str
    allowed_targets: tuple[str, ...]
    command_keys: tuple[str, ...]


class OffState(ActuatorState):
    name = "off"
    allowed_targets = (
        "idle",
        "error",
    )
    command_keys = (
        "turn_on",
    )


class IdleState(ActuatorState):
    name = "idle"
    allowed_targets = (
        "running",
        "maintenance",
        "off",
        "error",
    )
    command_keys = (
        "start",
        "enter_maintenance",
        "turn_off",
    )


class RunningState(ActuatorState):
    name = "running"
    allowed_targets = (
        "idle",
        "error",
    )
    command_keys = (
        "stop",
    )


class ErrorState(ActuatorState):
    name = "error"
    allowed_targets = (
        "idle",
    )
    command_keys = (
        "reset_error",
    )


class MaintenanceState(ActuatorState):
    name = "maintenance"
    allowed_targets = (
        "idle",
        "off",
        "error",
    )
    command_keys = (
        "exit_maintenance",
        "turn_off",
    )


_STATE_TYPES: dict[
    str,
    type[ActuatorState],
] = {
    "off": OffState,
    "idle": IdleState,
    "running": RunningState,
    "error": ErrorState,
    "maintenance": MaintenanceState,
}


def create_state(
    state_name: str,
) -> ActuatorState:
    normalized = state_name.strip().lower()

    state_type = _STATE_TYPES.get(
        normalized
    )

    if state_type is None:
        raise IllegalTransitionError(
            f"Unknown actuator state: {state_name}."
        )

    return state_type()


def state_names() -> tuple[str, ...]:
    return tuple(_STATE_TYPES)