from __future__ import annotations

from dataclasses import dataclass

from domain.actuators.state import (
    ActuatorState,
    IllegalTransitionError,
    create_state,
)


_COMMAND_NAMES: dict[
    str,
    dict[str, str],
] = {
    "water_pump": {
        "start": "start_pump",
        "stop": "stop_pump",
        "turn_on": "turn_on_pump",
        "turn_off": "turn_off_pump",
        "enter_maintenance": "enter_maintenance",
        "exit_maintenance": "exit_maintenance",
        "reset_error": "reset_error",
    },
    "grow_light": {
        "start": "start_grow_light",
        "stop": "stop_grow_light",
        "turn_on": "turn_on_grow_light",
        "turn_off": "turn_off_grow_light",
        "enter_maintenance": "enter_maintenance",
        "exit_maintenance": "exit_maintenance",
        "reset_error": "reset_error",
    },
}


_DEFAULT_COMMAND_NAMES = {
    "start": "start",
    "stop": "stop",
    "turn_on": "turn_on",
    "turn_off": "turn_off",
    "enter_maintenance": "enter_maintenance",
    "exit_maintenance": "exit_maintenance",
    "reset_error": "reset_error",
}


@dataclass
class ActuatorContext:
    """Context that owns the current actuator state."""

    device_type: str
    current_state: ActuatorState

    @classmethod
    def from_state_name(
        cls,
        device_type: str,
        state: str,
    ) -> "ActuatorContext":
        return cls(
            device_type=device_type,
            current_state=create_state(state),
        )

    @property
    def state(self) -> str:
        return self.current_state.name

    def transition(
        self,
        target: str,
    ) -> None:
        normalized = target.strip().lower()

        if (
            normalized
            not in self.current_state.allowed_targets
        ):
            raise IllegalTransitionError(
                f"Illegal actuator transition: "
                f"{self.state} -> {normalized}."
            )

        self.current_state = create_state(
            normalized
        )

    def allowed_commands(self) -> list[str]:
        command_names = _COMMAND_NAMES.get(
            self.device_type,
            _DEFAULT_COMMAND_NAMES,
        )

        return [
            command_names[key]
            for key
            in self.current_state.command_keys
        ]