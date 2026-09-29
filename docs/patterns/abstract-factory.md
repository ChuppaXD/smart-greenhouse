# Abstract factory in Smart Greenhouse

## Problem
The project now needs to support different device families. In this phase there are two families: simulation and edge

Each family should contain compatible devices instead of choosing every sensor and actuator separately. For e.g. a simulation family should use simulation configuration while an edge family should use edge or stub hardware configuration.

If every device was selected independently, it would be easier to accidentally create a mixed setup where some devices belong to simulation and others belong to edge.


## Solution
The project uses the abstract factory pattern to create a complete device family.

The common factory is DeviceFamilyFactory. It defines the family_key and create_device_set()

There are two concrete factories:
SimulationDeviceFactory
EdgeHardwareFactory

Each concrete factory creates four devices:
moisture sensor
light sensor
water pump
grow light

The factory returns them as one group and gives every device the same family key.

The family factories also reuse the factory method creators from phase 2 for the two sensor types. This means factory method is still responsible for creating an individual sensor, while abstract factory puts the related sensors and actuators together into a complete family.


## Factory Method vs Abstract Factory
Factory method is mainly about creating one product. In phase 2, the sensor type key such as moisture or light selects the appropriate sensor creator.

Abstract factory is about creating a product line. In phase 3, choosing simulation or edge gives a complete set of related sensors and actuators.

The abstract factory can still use factory method style creators inside it. The phase 3 family factories use the existing moisture and light creators instead of replacing them.


## Where to look in the code
backend/src/domain/devices/entity.py — unified Device domain entity.
backend/src/domain/devices/family_factory.py — abstract factory and concrete family factories.
backend/src/domain/sensors/creators.py — Phase 2 factory method creators that are reused by the family factories.
backend/src/application/devices/family_service.py — selects the family factory and persists its device set.
backend/src/infrastructure/persistence/device_repository.py — saves and lists devices.
backend/src/interfaces/api/devices.py — unified devices API.
frontend/src/components/devices/ — family switcher and device list.


## Why Device is not the DTO
Device is a domain entity used by the business / application layers. It should not depend on HTTP or Pydantic.

DeviceDto is used at the API boundary. It defines the JSON shape returned to the frontend.

The mapper in application/devices/mappers.py converts a domain Device into a DeviceDto. This keeps the domain separate from the API layer.


## Extension exercise: a third family
As an exercise, add a third device family such as test.

Create a new concrete family factory that implements DeviceFamilyFactory. It should still create two sensors and two actuators, but use its own labels and configuration.

Register the new factory in get_family_factory().

The goal is that the API and repository do not need a new hard coded device construction path for every individual device.