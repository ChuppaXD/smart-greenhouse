# Phase 2 — Factory Method questions

**Pattern / focus:** Factory Method.

**Read first:** [Guide 02](../../materials/guides/02-factory-method.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example courier notifiers) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to sensors, creators, the `devices` table, and the sensors API from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Factory Method in plain language. What problem appears when callers scatter `new` / constructors (or a growing `if type == ...`) across the application?

> [!NOTE]
> ***Your Answer***
>
> Factory Method is basically a way to let a separate creator decide which object should be made. The caller only asks for a type instead of knowing all the constructors. If constructors or many if type == ... checks are scattered around the application, adding a new type becomes harder because we have to change many places. It also makes the code more dependent on the concrete classes.

2. Name the main participants of Factory Method (**product**, **concrete product**, **creator**, **concrete creator**, **client**). For each, give one sentence: what it is responsible for.

> [!NOTE]
> ***Your Answer***
>
> 1.Product: The common type or interface that all created objects follow. In my project this is the Sensor entity.2.Concrete product: The actual type of object that is created such as a moisture sensor or light sensor with its own values. 3.Creator: The common creator interface that defines create_sensor(). 4.Concrete creator: The creator that knows how to create one specific sensor type and its default configuration like MoistureSensorCreator or LightSensorCreator. 5.Client: The part that asks for a sensor without creating the concrete class itself. In my project the application service does this through the creator lookup.

3. How do you add a **new product variant** when creators are polymorphic (new class + registry entry) versus when creation lives in one shared `if/elif` function? Why does that difference matter for extension?

> [!NOTE]
> ***Your Answer***
>
> With polymorphic creators, I can add a new creator class and then add it to the registry. The existing callers do not need to know about the new concrete class. With one big if/elif function, I would have to open that function and add another condition there every time. It matters because the creator approach keeps the different creation logic separated and makes adding another sensor type more organized.

## B. This phase of the application

4. In this lab, what is the **product** and what are the **concrete creators**? Why must the API handler (or sensor service) go through a creator/registry instead of constructing `MoistureSensor` / `LightSensor` itself?

> [!NOTE]
> ***Your Answer***
>
> The product is the Sensor domain entity. The concrete creators are MoistureSensorCreator and LightSensorCreator.The API or service should go through the creator because then it does not need to know how each sensor is made or what default values it needs. The creator handles that part, so the creation logic stays in one place.

5. `POST /api/sensors` accepts a short `type` key such as `"moisture"` or `"light"`, while the stored/returned field is `device_type` (for example `moisture_sensor`). Why are those two fields different? Who decides the stored `device_type` and `default_config`?

> [!NOTE]
> ***Your Answer***
>
> The short type is mainly the key used to choose which creator should be used. device_type is the actual type stored for the sensor in the database. For e.g. "moisture" selects the moisture creator and that creator creates a sensor with device_type="moisture_sensor". The concrete creator decides the device_type and the default_config. This means the API does not have to contain those sensor specific values.

6. Why is there a single `devices` table with `role="sensor"` instead of a dedicated `sensors` table? What later phase does that choice prepare for?

> [!NOTE]
> ***Your Answer***
>
> The single devices table makes the structure easier to extend later. Sensors are stored with role="sensor" for now. This prepares for Phase 3, where actuators and device_family will be added to the same device structure instead of creating another separate table.

7. What should happen when the client posts an **unknown** `type`? Where should that rejection be decided (registry/service vs router constructing a concrete class anyway)?

> [!NOTE]
> ***Your Answer***
>
> The request should be rejected with a 400 error and a useful message. The creator registry or service should detect the unknown type and reject it before anything is saved to the database. The router should not try to guess a concrete sensor class itself.

## C. Compare, contrast, and scenarios

8. Contrast Factory Method with a **simple factory** (one function full of `if type == ...`). When is the simple factory “good enough,” and why does this phase still want polymorphic creators?

> [!NOTE]
> ***Your Answer***
>
> A simple factory can be good enough when there are only a few types and the creation logic is very small. For a small project, one function with a few conditions might be easier. This phase still uses polymorphic creators because the course wants us to separate the different creation behaviours. It also makes it easier to add more sensor types later without making one function bigger and bigger.

9. Contrast Factory Method with **Abstract Factory** (Phase 3). Factory Method answers which question? Abstract Factory answers which different question? Why is Factory Method enough for Phase 2 sensors?

> [!NOTE]
> ***Your Answer***
>
> Factory Method mainly answers "which concrete product should be created?" For e.g. should I create a moisture sensor or light sensor? Abstract Factory is more about creating a related group or family of different products. Factory Method is enough for Phase 2 because we are only creating individual sensor products. We do not need to create a whole related family of devices yet. Phase 3 will deal with that kind of family structure.

10. A classmate puts SQLAlchemy session commits (or FastAPI request parsing) **inside** a concrete creator. Why is that a trap? Where should persistence and HTTP stay instead?

> [!NOTE]
> ***Your Answer***
>
> I think that is a trap because then the creator becomes responsible for too many things. It would know about the database or HTTP framework instead of only being responsible for creating the sensor. In this project, HTTP request parsing belongs in the API layer, while database saving and session handling belong in the infrastructure / repository layer. The creator should stay focused on creating the sensor and its default configuration.