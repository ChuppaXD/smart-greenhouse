# Builder Pattern in Smart Greenhouse

## Problem
A location configuration can contain several pieces of information. A location needs a name and it must contain one or more zones. Each zone has a name, moisture thresholds and an optional schedule.

Creating this configuration directly with many constructor arguments could make it easier to create incomplete or invalid configurations.


## Solution
The project uses LocationConfigBuilder to construct a location configuration step by step.

The builder allows the caller to:
set the location name,
add one or more zones,
call build() when the configuration is ready.

The build() method checks the complete configuration before it can be saved.

The validation includes:
location name is not empty,
at least one zone exists,
zone names are unique inside the location,
thresholds are between 0.0 and 1.0,
the low threshold is strictly smaller than the high threshold.

An invalid configuration raises ConfigurationError.


## Why this is Builder
This is Builder because the object is constructed in several steps and the final build() call produces a validated configuration.

It is different from factory method because factory method chooses how to create one type of product.

It is different from abstract factory because abstract factory creates a related family of products.

Here the problem is constructing one valid location configuration from several parts, so Builder fits the problem.


## Where validation lives
Validation belongs in the domain layer.

The main Builder code is:
backend/src/domain/locations/config_builder.py

The domain does not depend on FastAPI, SQLAlchemy or Pydantic.

Saved location zone updates also reuse the same threshold and name rules instead of putting all validation only in the HTTP layer.


## Why location_id is used
The project uses location and location_id because a zone belongs to a saved location.

The zones.location_id field points to the location that owns the zone.

A device can then be assigned to a zone using devices.zone_id. When that assignment is made, devices.location_id is copied from the zone's location_id.

There is no greenhouse_id in this phase.


## Why device assignment is not part of the Builder
The builder only creates a location configuration.

A zone does not have a database id until the configuration has been saved.

Because of that, attaching devices while calling build() would mix two different responsibilities.

Device assignment is handled later by ZoneAssignmentService after the zone already exists in the database.

The same is true for listing locations, deleting a location, and adding, editing, or deleting zones on a saved location. Those are separate operations and do not rebuild the configuration.


## Main code paths
backend/src/domain/locations/entity.py
backend/src/domain/locations/config_builder.py
backend/src/domain/locations/errors.py
backend/src/application/locations/dto.py
backend/src/application/locations/config_service.py
backend/src/application/locations/zone_assignment_service.py
backend/src/infrastructure/persistence/location_repository.py
backend/src/interfaces/api/locations.py


## Extension exercise
We can be adding another kind of location configuration rule, such as a configurable temperature range.

The Builder could be extended with a new method for that configuration and build() could validate it before creating the final LocationConfig.

The new rule should stay in the domain and should not make the Builder responsible for database or HTTP operations.