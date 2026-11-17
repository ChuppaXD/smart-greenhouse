from uuid import UUID

from domain.commands.base import Command
from domain.commands.light import (
    SetLightLevelCommand,
)
from domain.commands.pump import (
    StartPumpCommand,
    StopPumpCommand,
)


COMMAND_REGISTRY: dict[
    str,
    type[Command],
] = {
    "start_pump": StartPumpCommand,
    "stop_pump": StopPumpCommand,
    "set_light_level": SetLightLevelCommand,
}


class UnknownCommandTypeError(
    ValueError
):
    pass


def command_for(
    command_type: str,
    device_id: UUID,
    payload: dict,
) -> Command:
    command_class = COMMAND_REGISTRY.get(
        command_type
    )

    if command_class is None:
        raise UnknownCommandTypeError(
            f"Unknown command type: {command_type}"
        )

    return command_class(
        device_id,
        payload,
    )