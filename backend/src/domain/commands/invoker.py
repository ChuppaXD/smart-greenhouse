from domain.actuators.ports import ActuatorPort
from domain.commands.base import Command


class CommandInvoker:
    def run(
        self,
        command: Command,
        port: ActuatorPort,
    ) -> None:
        command.execute(port)