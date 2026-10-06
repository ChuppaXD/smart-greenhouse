# Adapter pattern in Smart Greenhouse

## Problem
The Smart Greenhouse can receive sensor data in different forms. A simulation sensor generates values in code, while a vendor device may use a different raw data structure. MQTT also has its own payload format.

Using those formats directly throughout the application would make the rest of the system depend on each specific device or protocol.


## Solution
The Adapter pattern converts different sensor sources into one normalized Reading object.

SensorPort is the common interface used by the application. The simulation adapter and vendor stub implement this port.

The simulation adapter generates a value and returns a normalized Reading.

The vendor stub receives a different raw structure and translates it into the same Reading structure.

MqttSensorAdapter translates an MQTT style dictionary into a Reading. Phase 5 does not connect to a broker.

The application uses ReadingIngest as the common path for storing readings in sensor_readings.


## Where it is used
The main classes are:

domain/sensors/ports.py — SensorPort
domain/sensors/reading.py — normalized Reading
infrastructure/adapters/sensors/simulation.py
infrastructure/adapters/sensors/vendor_stub.py
infrastructure/adapters/sensors/mqtt.py
application/readings/service.py — ReadingIngest

The actuator side also has ActuatorPort and SimulationActuatorAdapter. The simulation actuator only records commands in memory and does not control physical hardware.


## Selecting the adapter
Normal sensor selection uses default_config.protocol.

simulation selects the simulation adapter.

mqtt represents the MQTT path, but phase 5 only translates MQTT payloads and does not open a broker connection.

The vendor stub uses a separate sensor_adapter: "vendor_stub" flag so it does not conflict with the normal protocol values.


## Extending the design
A third vendor can be supported by creating another adapter that implements SensorPort. The new adapter translates its own raw format into the same Reading.

The application services do not need to change just because a new sensor vendor is added.