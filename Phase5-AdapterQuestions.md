# Phase 5 — Adapter questions

**Pattern / focus:** Adapter.

**Read first:** [Guide 05](../../materials/guides/05-adapter.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example a legacy XML calendar client) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to sensor ports, adapters, readings, and `sensor_readings` from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Adapter in plain language. What problem appears when business code speaks a vendor or legacy protocol (odd field names, units, XML, status codes) directly?

> [!NOTE]
> ***Your Answer***
>
> _(The adapter pattern helps different systems work together when their interfaces or data formats are different. Without an adapter, the main application would have to understand vendor specific field names, units or data formats itself. That would make the business code harder to change and maintain.)_

2. Name the participants (**target / port**, **adaptee**, **adapter**, **client**). What does the adapter translate, and what must it **not** decide (business policy)?

> [!NOTE]
> ***Your Answer***
>
> _(The target or port is the interface the application expects, such as SensorPort. The adaptee is the original sensor or data format. The adapter connects the two and translates the data into the format the application understands. The client uses the port. The adapter should not decide things like when to water the plants or other business rules.)_

3. GoF distinguishes an **object adapter** (composition) from a **class adapter** (inheritance). Which does modern code prefer, and why?

> [!NOTE]
> ***Your Answer***
>
> _(Modern code usually prefers object adapters using composition. The adapter contains or uses the original object instead of inheriting from it. This gives more flexibility and keeps the adapter less tightly connected to the adaptee.)_

## B. This phase of the application

4. What is `SensorPort` in this lab, and what normalized value type (for example `Reading`) do adapters return? Why do application services depend on the port rather than on a simulation driver or vendor SDK?

> [!NOTE]
> ***Your Answer***
>
> _(SensorPort is the common interface that sensors use in this application. The adapters return a normalized Reading with the device id, value, unit, source and time. The application uses the port so it does not need to know which sensor adapter or vendor format is being used.)_

5. You need three translations onto the same normalized reading: a simulation adapter, a vendor stub, and an MQTT translator that accepts a payload dict. Why is the different raw shape the point of the exercise? How does `source` (`simulation`, `vendor`, or `mqtt`) show which adapter produced the reading, and why must the MQTT translator not open a broker in this phase? Phase 12 may deliver that same dict on a device HTTP route or through an optional broker — why must this phase still not open either transport?

> [!NOTE]
> ***Your Answer***
>
> _(The different raw shapes show why adapter is useful. The simulation, vendor and MQTT data can look different, but they are all converted into the same Reading for the application. The source field shows where the reading came from, such as simulation, vendor or mqtt. MQTT should not open a broker in this phase because phase 5 is only about translation. The actual device HTTP or broker transport is planned for phase 12.)_

6. Readings are **appended** to `sensor_readings` (history grows). Why not keep only the latest value in memory or overwrite a single row, and which later phase consumes this history? Why do a manual read, the simulation sampler, and (later) MQTT share **one** writer of that table? Why does the sampler skip devices with tracking off and MQTT devices, and why do sensor cards poll the latest stored reading until Phase 12?

> [!NOTE]
> ***Your Answer***
>
> _(Keeping the readings as separate rows gives us a history that can be used later by "strategy" and other features. A manual read, the sampler and later MQTT should use the same writer so all readings are stored in the same way. The sampler skips tracking off devices because they should not be automatically sampled and it skips MQTT devices because MQTT is not being used as a sampler transport in this phase. The sensor cards poll the latest stored reading so the UI can show new database readings until phase 12 replaces the polling with WebSockets.)_

7. `POST /api/sensors/{id}/read` runs an adapter, persists, and returns a DTO. What HTTP status is appropriate when the device is missing versus when the adapter fails? Why must the router never see vendor-shaped types?

> [!NOTE]
> ***Your Answer***
>
> _(A missing device should return 404 Not Found. If the adapter or reading data has a validation or other input problem, it should return a 400 level error. The router should only work with the common application types and Reading, because vendor specific data should be handled inside the adapter.)_

## C. Compare, contrast, and scenarios

8. Contrast Adapter with **Facade**. Adapter changes the **shape** of an existing interface; Facade simplifies **how to use** a subsystem. Give a greenhouse-shaped example of each (Adapter this phase; Facade in Phase 7).

> [!NOTE]
> ***Your Answer***
>
> _(Adapter changes one interface or data format into another one that the application expects. In this phase, a vendor sensor payload is converted into a normal Reading. A Facade is different because it gives the user one simpler way to use a more complicated subsystem. For e.g. a later greenhouse Facade could provide one simple operation that gets sensor data, checks configuration and returns a dashboard summary without the caller having to know all the internal services.)_

9. Contrast Adapter with **Decorator**. Both wrap an object. What is different about the interface they present to the client?

> [!NOTE]
> ***Your Answer***
>
> _(Adapter changes the interface so the client can use something that had a different interface. Decorator normally keeps the same interface but adds extra behaviour around it. In this project, SensorPort adapters make different sensor sources look the same, while phase 9 Decorators will add behaviour around the ActuatorPort.)_

10. A classmate puts irrigation policy (“if moisture &lt; 0.3 then water”) inside the vendor adapter. Why is that a trap? Where should that decision live instead (later Strategy), and what should stay in the adapter?

> [!NOTE]
> ***Your Answer***
>
> _(That is a trap because the adapter should only translate the vendor data into the common format. If irrigation rules are put inside it, the adapter becomes responsible for business logic too. The irrigation decision should later be handled by the Strategy pattern. The adapter should only translate the incoming data, convert it when needed and return a normal Reading.)_
