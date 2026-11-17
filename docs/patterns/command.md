# Command pattern - Phase 10

## Intent
The command pattern turns an actuator request into an object.

Instead of the HTTP layer directly calling an actuator operation, the request becomes a command such as StartPumpCommand.

Because the request is an object, it can be checked, executed through an invoker and stored in command history.


## Participants
The main participants in this greenhouse are:
- Command - common interface with execute(port).
- StartPumpCommand - starts the pump.
- StopPumpCommand - stops the pump.
- SetLightLevelCommand - changes the light level.
- CommandInvoker - calls execute() on a command.
- ActuatorPort - the receiver interface used by commands.
- SimulationActuatorAdapter - the concrete actuator adapter behind the Phase 9 decorators.
- The application command service - creates the command and coordinates State, execution and logging.


## Command registry
The command type from HTTP is mapped to a command class by the command registry.

For e.g.
start_pump       to StartPumpCommand
stop_pump        to StopPumpCommand
set_light_level  to SetLightLevelCommand