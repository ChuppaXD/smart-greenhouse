# Phase 7 — Facade questions

**Pattern / focus:** Facade.

**Read first:** [Guide 07](../../materials/guides/07-facade.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example a video publish pipeline) as if they were your greenhouse classes.
- When a question asks about _this application_, refer to the location overview, the facade, and the dashboard Overview page from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Facade in plain language. What problem appears when every HTTP handler (or every UI screen) repeats the same multi-step dance across repositories and services?

> [!NOTE]
> **_Your Answer_**
>
> _(Facade gives one simple way to use several parts of a system together. Without it, every API handler or UI would have to know which repositories and services to call and how to combine their results. That would make the code more complicated and harder to maintain.)_

2. A facade **orchestrates** collaborators. What should it **not** become (a god object that owns all domain logic)? Where should irrigation policy, sensor translation, and persistence stay instead?

> [!NOTE]
> **_Your Answer_**
>
> _(The facade should mainly coordinate existing services and repositories. It should not contain all the business rules itself. Irrigation decisions stay in the Strategy classes, sensor translation stays in the Adapter classes and database work stays in the repository layer.)_

3. When should you use Facade, and when should you skip it (a single repository call is enough; or you actually need to **translate** a mismatched interface)?

> [!NOTE]
> **_Your Answer_**
>
> _(Facade is useful when one operation needs information or actions from several subsystems. If one simple repository call is enough, a facade is probably unnecessary. Also, facade is not for translating incompatible interfaces; that is what adapter is for.)_

## B. This phase of the application

4. What does `GET /api/locations/{location_id}/overview` return? Name the main pieces of the overview DTO: location, assigned device counts, and `zones` (thresholds, assigned devices, and those devices’ latest readings, including `tracking_enabled` and `sampling_interval_seconds`), plus strategy key and last recommendation. Why may those reading rows come from the sampler or MQTT ingest, not only from `POST /read`? Why is overview scoped by `location_id`?

> [!NOTE]
> **_Your Answer_**
>
> _(The overview returns one snapshot of a location. It contains the location, counts of assigned sensors and actuators, all its zones, the devices in each zone and the newest reading for each device. The reading also shows tracking and sampling settings from the device, plus the saved strategy and the latest recommendation. Readings can come from the manual read, the phase 5 sampler or MQTT because they all store readings in the same sensor_readings table. It is scoped by location_id so the dashboard only shows data belonging to the selected location.)_

5. Why does this phase **not** require a new business table? What already exists from Phases 2–6 that the facade only **composes**?

> [!NOTE]
> **_Your Answer_**
>
> _(No new table is needed because all the information already exists in the database. We already have locations and zones, devices and their assignments, sensor readings and the saved automation strategy. The facade just combines this existing information into one response.)_

6. The overview HTTP handler should call **only** the facade, not reading/strategy/device repositories directly. Why? How does that help tests and later changes to the query shape?

> [!NOTE]
> **_Your Answer_**
>
> _(The handler only needs to know how to ask for an overview. It should not know how the data is collected from different repositories. This makes the API easier to test because the facade can be tested separately and later we can change the database queries without changing the API route.)_

7. The location selector may use the existing locations list. The Overview cards come from **one** overview fetch, and Refresh repeats that same fetch. Why must the React page not stitch device, reading, and automation calls together to build the same snapshot? How does a new reading or a saved strategy show up on overview without extra frontend glue?

> [!NOTE]
> **_Your Answer_**
>
> _(The point of the facade is to give the frontend one complete overview instead of making React understand how the backend is organized. When the page calls the overview endpoint again, the facade reads the current database state, so a new reading or changed strategy appears automatically without adding more frontend API calls and combining their results.)_

## C. Compare, contrast, and scenarios

8. Contrast Facade with **Adapter**. One makes an existing interface usable; the other makes a subsystem simpler to call. Which is which, and how do both appear in this greenhouse app (Phase 5 vs Phase 7)?

> [!NOTE]
> **_Your Answer_**
>
> _(Adapter makes something with a different interface usable by translating it into the format our application expects. In phase 5, the sensor adapters translate simulation, vendor and MQTT data into Reading. Facade makes several existing subsystems easier to use through one entry point. In phase 7, the overview facade combines locations, devices, readings and automation into one API response.)_

9. This phase mentions **N+1** queries. What is an N+1 problem in an overview that lists latest readings for many devices, and what can the facade (or its repository) do about it without putting SQL in the router?

> [!NOTE]
> **_Your Answer_**
>
> _(N+1 happens when the application first gets all the devices and then runs another reading query separately for every device. That can become many database queries very quickly. The repository can instead get the latest reading for all the device IDs in one query and the facade can then match those results to the devices.)_

10. A classmate hides every error behind a generic “overview failed,” so a missing location, a DB outage, and a strategy error look the same. Why is that a trap for a facade?

> [!NOTE]
> **_Your Answer_**
>
> _(The facade should make the system simpler, but it should not hide useful information about what actually went wrong. A missing location should be handled differently from a database problem or a strategy problem. Keeping those errors distinguishable makes the API easier to debug and gives the user a more useful response.)_