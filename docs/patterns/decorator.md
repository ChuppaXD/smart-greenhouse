# Decorator pattern - phase 9

## Problem
The actuator port needs additional policies such as logging and maximum run time.

Putting all policies directly inside the simulation adapter would make that adapter responsible for too many things. Creating a separate subclass for every combination would also create too many classes.


## Solution
Phase 9 uses the decorator pattern around the existing ActuatorPort.
Commands flow through the wrappers in this order:
LoggingActuatorDecorator MaxRunTimeActuatorDecorator SimulationActuatorAdapter