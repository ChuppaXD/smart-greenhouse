# Phase 3 — Abstract Factory questions

**Pattern / focus:** Abstract Factory.

**Read first:** [Guide 03](../../materials/guides/03-abstract-factory.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example warrior/mage class kits) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to device families, provision, and the unified devices API from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Abstract Factory in plain language. What goes wrong when related products are chosen independently (`if format` for each piece) instead of as a **family**?

> [!NOTE]
> ***Abstract factory is a way to create a group of related objects that are meant to work together. In my project, the idea is to create a complete device family instead of choosing every device separately. If every sensor and actuator is selected independently with many if statements, it is easier to accidentally mix devices from different families. Then for e.g. a simulation sensor could be used together with an edge actuator even though their settings or protocols are different.***
>
> _(Write your answer here.)_

2. Name the main participants (**abstract factory**, **concrete factory**, **abstract products**, **concrete products**, **client**). How does choosing a factory at the start **commit** the client to one family?

> [!NOTE]
> ***The abstract factory defines how a device family is created, including create_device_set(). The concrete factories are SimulationDeviceFactory and EdgeHardwareFactory. They create the devices for their own family. The abstract products are the common device types that can belong to the family, such as sensors and actuators. The concrete products are the actual devices, such as moisture sensor, light sensor, water pump and grow light with family specific settings. The client is the application service that asks for a family and gets the device set. When the client chooses the simulation factory, all devices in that kit come from the simulation family. The same happens with the edge factory, so the client does not accidentally mix the two families.***
>
> _(Write your answer here.)_

3. When should you use Abstract Factory, and when should you skip it (for example only one product type per request, or mixing siblings is valid)?

> [!NOTE]
> ***I would use abstract factory when several related products need to be created as one matching group. It makes sense here because one family contains both sensors and actuators that should use compatible settings. I would skip it when I only need one product type or when mixing the different products is completely fine. In a small situation, adding a whole family factory could just make the code more complicated.***
>
> _(Write your answer here.)_

## B. This phase of the application

4. In this lab, what is a **device family**, and what does `create_device_set()` (or your equivalent) return? Why must a simulation kit and an edge kit not mix incompatible siblings?

> [!NOTE]
> ***A device family is a group of devices made for the same environment or way of running the system. In my project the two families are simulation and edge. create_device_set() returns a complete list of four devices: two sensors and two actuators. The simulation and edge kits should not mix because they can have different configuration and protocols. A simulation device can be made for simulated communication while an edge device can use stub hardware settings, so mixing them could give an inconsistent setup.***
>
> _(Write your answer here.)_

5. Phase 2 Factory Method creators still exist. How does Abstract Factory **compose** them rather than replace them? What would you lose if you deleted the sensor creators and inlined all construction inside the family factory?

> [!NOTE]
> ***The Phase 2 sensor creators are still responsible for creating the individual sensor types. The abstract factory uses those creators when it builds a complete family. For e.g. the family factory can use the moisture creator and light creator to make the two sensors, then add the pump and grow light for the same family. If I deleted the sensor creators, all the sensor creation logic would move into the family factories. Then there would be duplicated logic and the clear separation from phase 2 would be lost. Adding or changing a sensor type would also become harder.***
>
> _(Write your answer here.)_

6. Why add a `device_family` column on the existing `devices` table (with a default/backfill such as `"simulation"`) instead of a new table per family? What happens to Phase 2 sensor rows if you forget the backfill?

> [!NOTE]
> ***Using the existing devices table keeps all devices in one place. The device_family column tells us which family each device belongs to, while role tells us if it is a sensor or actuator. This also makes it easier to use the same table when more device types are added later. If the old phase 2 sensor rows are not given a family value, they can have a missing or invalid family. Then filtering by family can give wrong results and the old sensors may not fit correctly into the new family structure.***
>
> _(Write your answer here.)_

7. `POST /api/devices/provision` returns a kit (expected size: two sensors and two actuators). `GET /api/devices` can filter by `family` and `role`. Why must the UI be able to filter by family? Why do `/api/sensors` routes from Phase 2 still need to work?

> [!NOTE]
> ***The UI needs to filter by family so it does not show devices from the simulation family when I selected edge or the other way around. Otherwise the user could see a mixed kit and the family switcher would not really work.The /api/sensors routes should still work because phase 2 already created individual sensors through factory method. Keeping those routes means the old sensor functionality is not broken just because phase 3 added the new unified devices API.***
>
> _(Write your answer here.)_

## C. Compare, contrast, and scenarios

8. Draw the contrast in one paragraph: Factory Method vs Abstract Factory. Use the questions “which **one** product?” versus “which product **line**?” and mention that Abstract Factory often **uses** Factory Method–style methods inside.

> [!NOTE]
> ***Factory method is mainly about which one product I should create. In my phase 2 project, it chooses between individual sensor types like moisture or light. Abstract factory is about which product line I should create. In phase 3, it creates a complete family with sensors and actuators that belong together. Abstract factory can also use factory method style creation methods inside it, which is what happens in my project because the family factories still use the phase 2 sensor creators.***
>
> _(Write your answer here.)_

9. A DTO or HTTP handler constructs concrete simulation/edge device types directly, bypassing the family factory. What consistency bug can that reintroduce? How should HTTP stay on the abstract factory / service instead?

> [!NOTE]
> ***That could make the API create a device that does not belong to the selected family. For e.g. the request could ask for an edge kit but the handler creates a simulation device directly. HTTP should only pass the requested family to the service. The service should choose the correct abstract factory and let that factory create the matching devices. This keeps the family decision out of the HTTP layer.***
>
> _(Write your answer here.)_

10. Someone proposes a single “god factory” that creates locations, readings, and devices “because we already have a factory.” Why is that a misuse of Abstract Factory?

> [!NOTE]
> ***I think that would be too much responsibility for one factory. Abstract factory is useful for a related group of products, but locations, readings and devices are different parts of the application and do not automatically belong to one product family. A huge factory would become harder to understand and maintain. It would also make the pattern less useful because we would be using it just because we already have a factory, instead of because there is a real family of related objects to create.***
>
> _(Write your answer here.)_
