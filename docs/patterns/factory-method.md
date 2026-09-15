# Factory method in Smart Greenhouse

## Problem

The application needs to create different types of sensors such as moisture sensors and light sensors. They have different default configurations.

A simple approach would be for the API or another caller to create each concrete sensor directly. That would make the callers know too much about every sensor type. When more sensor types are added, many callers could need to be changed.

## Solution

This project uses the Factory Method pattern for sensor creation.

There is a common SensorCreator interface with a create_sensor() method. Concrete creators implement that method:

MoistureSensorCreator
LightSensorCreator

The application asks the creator lookup for a short type key such as moisture or light. The selected creator then creates the correct sensor with its own default configuration.

For e.g. moisture sensors use a moisture related configuration with a VWC unit, sampling interval and threshold. Light sensors use a lux unit and a different sampling interval.

The HTTP API does not directly create concrete sensor types. This keeps the creation decision inside the domain / application design instead of spreading it through the callers.

## Where to look in the code

The main Factory Method code is here:

backend/src/domain/sensors/entity.py — Sensor domain entity
backend/src/domain/sensors/creators.py — SensorCreator, concrete creators and creator lookup
backend/src/application/sensors/service.py — resolves a creator, creates a sensor,and sends it to the repository
backend/src/infrastructure/persistence/device_repository.py — saves the created sensor in the devices table
backend/src/interfaces/api/sensors.py — HTTP API for creating and listing sensors.

## Why this is useful here

The main benefit is that callers do not need to know how every sensor type is constructed.

For e.g. the API only sends a short type key:
moisture
or
light

The creator lookup selects the correct creator and that creator provides the type specific defaults.

This also gives a clear place to add another sensor type later.

## Extension exercise: Temperature sensor

As an exercise, add a TemperatureSensorCreator.

It should:

1. inherit from SensorCreator,
2. implement create_sensor(),
3. use device_type = "temperature_sensor",
4. have a temperature related unit such as celsius,
5. use its own sampling interval,
6. register the creator under a key such as temperature.

The REST API should then be able to create it by using the new type key without directly constructing the concrete sensor in the API route.