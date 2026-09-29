# Phase 4 — Builder questions

**Pattern / focus:** Builder.

**Read first:** [Guide 04](../../materials/guides/04-builder.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example ramen orders) as if they were your greenhouse classes.
- When a question asks about _this application_, refer to locations, zones, `location_id`, and the configuration wizard from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Builder in plain language. Why does construction of a complex object need **stepwise assembly** and **validation at the end** (`build()`), instead of a telescoping constructor or a half-filled dict written straight to the database?

> [!NOTE]
> **_Your Answer_**
>
> _(The builder pattern makes it easier to create a complex object one part at a time. In our case, the location name and zones are added step by step and build() checks that the whole configuration is valid before it is saved. This is safer than sending a half filled object directly to the database.)_

2. Name the main participants (**product**, **builder**, **optional director**, **client**). Until `build()` succeeds, is the intermediate object a finished domain product? Why does that distinction matter?

> [!NOTE]
> **_Your Answer_**
>
> _(The product is the final LocationConfig, the builder is LocationConfigBuilder, the client is the application code that uses the builder and a director can be used when the building steps follow a fixed process. Before build() succeeds, the builder is only holding the data needed to create the product. It is not a finished domain object yet, which matters because invalid or incomplete data must not be treated as a valid saved configuration.)_

3. List at least three kinds of invalid configuration a location/zone `build()` should reject in **this** lab (name, zones, moisture thresholds). Why must those rules live in the **domain** builder, not only in the HTTP layer?

> [!NOTE]
> **_Your Answer_**
>
> _(The builder should reject an empty location name, a location with no zones, invalid moisture values outside 0.0–1.0, inverted thresholds where low is greater than or equal to high and duplicate zone names in the same location. These rules belong in the domain builder because the domain should always protect itself, even if the data comes from somewhere other than the HTTP API.)_

## B. This phase of the application

4. What aggregate does the builder produce (location plus zones)? Why does this course use **`location_id`** (and never `greenhouse_id`) as the name for that scope?

> [!NOTE]
> **_Your Answer_**
>
> _(The builder produces one location configuration containing the location and its zones. The course uses location_id because that is the required name for this phase and it keeps the database and API terminology consistent. greenhouse_id is not used in this phase.)_

5. Describe the path from API request to persistence: DTO → builder steps → `build()` → repository. What must **not** be persisted if `build()` raises `ConfigurationError` (or equivalent)? Why does assigning a device wait until the zone row exists, and why does the client send only `zone_id`?

> [!NOTE]
> **_Your Answer_**
>
> _(The API receives the request as a DTO, the application maps it to builder calls, adds the location and zones and then calls build(). If build() raises ConfigurationError, nothing from that configuration should be saved. Device assignment happens later because the zone needs a real database id first. The client only sends zone_id because the server already knows the location from that zone, so the client cannot accidentally send a different location.)_

6. Saving a location and its zones must be **one transaction**. What goes wrong if the location row commits and a later zone insert fails? How does that relate to “no half-built aggregates in the database”?

> [!NOTE]
> **_Your Answer_**
>
> _(If the location is committed first and a zone insert fails later, the database could contain a location without all of its zones. That would leave a half built configuration. Using one transaction means either the location and all zones are saved or everything is rolled back if something fails.)_

7. The configuration wizard UI collects fields in steps. How does that UI map to Builder without turning React (or the HTTP handler) into the place that owns domain validation?

> [!NOTE]
> **_Your Answer_**
>
> _(The wizard only collects the location name, zone details, thresholds and schedule, then sends them to the API. React can show simple input errors to help the user, but the real configuration rules are still checked by the domain builder when the API handles the request. This keeps the validation in one proper place instead of putting the business rules inside the UI.)_

## C. Compare, contrast, and scenarios

8. Contrast Builder with Factory Method and with Abstract Factory. Which pattern answers “which type?”, which answers “which matching kit?”, and which answers “how do we assemble one **valid whole** in steps?”

> [!NOTE]
> **_Your Answer_**
>
> _(Factory method is mainly about deciding which type of object to create. Abstract factory is about creating a matching group of related objects. Builder is about assembling one complete object step by step and checking that it is valid. In this phase, builder is used to create one valid location configuration with its zones.)_

9. Fluent method chaining (`builder.add_zone(...).build()`) is a coding style. Why is a fluent interface **not** the same thing as the Builder pattern?

> [!NOTE]
> **_Your Answer_**
>
> _(Fluent interface only describes how methods are written, for e.g. calling several methods in one chain. A class can use fluent methods without actually being a builder. Builder is about controlling the construction of a complex object, including the steps and validation needed before the final object is created.)_

10. A classmate validates thresholds only in FastAPI / Pydantic and leaves `build()` empty. Another mutates builder fields after `build()` while treating the product as immutable. Explain why each is a trap.

> [!NOTE]
> **_Your Answer_**
>
> _(The first approach is a problem because the domain itself is not protecting its rules. If the builder can create an invalid configuration, another caller could bypass the FastAPI validation and still get bad data. The second approach is a problem because once build() returns the final product, it should represent the completed configuration. Changing builder data afterward should not change an already created immutable product.)_
