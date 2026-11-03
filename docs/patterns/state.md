# State Pattern

## Problem
An actuator has a lifecycle.

A water pump or grow light can be idle, running, in maintenance, turned off or in an error state.

Using boolean flags such as is_running, is_fault and is_maintenance would allow contradictory combinations.

It would also spread transition checks across the API, application service and UI.


## Solution
The state pattern keeps the actuator lifecycle rules in the domain.

The main code is in:

- backend/src/domain/actuators/state.py
- backend/src/domain/actuators/context.py
- backend/src/application/devices/state_service.py
- backend/src/infrastructure/persistence/actuator_state_repository.py
- backend/src/infrastructure/persistence/models.py
- backend/src/interfaces/api/devices.py

ActuatorContext holds the current ActuatorState.

The concrete state classes define which target states are legal and which commands are available.


## Implemented states
The greenhouse actuator lifecycle uses:
- off
- idle
- running
- error
- maintenance


## Legal transitions
```text
off -> idle, error
idle -> running, maintenance, off, error
running -> idle, error
maintenance -> idle, off, error
error -> idle