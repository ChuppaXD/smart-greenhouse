# Phase 9 — Decorator questions

**Pattern / focus:** Decorator.

**Read first:** [Guide 09](../../materials/guides/09-decorator.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example HTTP client wrappers) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to `ActuatorPort`, policy decorators, and `actuator_execution_log` from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Decorator in plain language. Why is stacking wrappers a flexible alternative to a combinatorial explosion of subclasses (`LoggingRetryMaxRuntimeActuator`, …)?

> [!NOTE]
> ***Your Answer***
>
> _(Decorator lets us add extra behavior around an existing object without changing the object itself. In this greenhouse, logging and max-runtime checking can be added around ActuatorPort without creating a different actuator subclass for every combination. This avoids classes such as a separate logging-plus-max-runtime actuator and more combinations would otherwise create even more subclasses)_

2. Name the participants (**component**, **concrete component**, **decorator**, **concrete decorators**). What interface does every decorator present to the caller, and why must that match the wrapped component?

> [!NOTE]
> ***Your Answer***
>
> _(The component is ActuatorPort. The concrete component is SimulationActuatorAdapter, which is the innermost actuator implementation in this phase. The decorator is another implementation of ActuatorPort that contains another ActuatorPort. The concrete decorators here are LoggingActuatorDecorator and MaxRunTimeActuatorDecorator.

Every decorator presents the same apply(device_id, command, payload) method because the caller should be able to use the decorated object exactly like the original port.)_

3. **Order matters.** Using logging and retry (or logging and max-run-time) as an example, explain how wrapping A around B can change what you observe compared with wrapping B around A.

> [!NOTE]
> ***Your Answer***
>
> _(The order changes which decorator sees the call and the result. In this phase the order is LoggingActuatorDecorator outside MaxRunTimeActuatorDecorator. This means logging can see a max-runtime failure and store it in actuator_execution_log. If the order were reversed, the max-runtime decorator could reject the call before the logging decorator is reached, so the logging behavior could be different.)_

## B. This phase of the application

4. What is `ActuatorPort` here, and which **at least two** decorators did you stack around the real adapter (for example logging and max run-time)? Where is the chain wired (composition root / factory), and why not inside the HTTP router?

> [!NOTE]
> ***Your Answer***
>
> _(ActuatorPort is the common interface for applying a command to an actuator. In phase 9, I stacked LoggingActuatorDecorator and MaxRunTimeActuatorDecorator around SimulationActuatorAdapter.

The chain is wired in the actuator service composition/factory when the application is created for a request. The HTTP handler should not build the decorator chain or contain the policy rules because that would mix HTTP code with actuator behavior and make the same chain harder to reuse.)_

5. Max run-time can **short-circuit**: the inner adapter is never called. Why must a blocked attempt still produce a row in `actuator_execution_log` with `success=false` and the policy named in `policy_applied`?

> [!NOTE]
> ***Your Answer***
>
> _(A blocked attempt is still an attempt made by the caller, even though the simulation adapter is never reached. The execution log therefore needs to show that the command was rejected and why it was rejected.

For a max-runtime block the row contains success=false, policy_applied=["maxRunTime", "logging"] and the message Max run time exceeded. This gives the dashboard a complete record of what happened.)_

6. How does max run-time know the actuator has been running too long (for example `actuator_states.updated_at` from Phase 8)? Why is that data from **State**, not something the decorator should invent as a second lifecycle?

> [!NOTE]
> ***Your Answer***
>
> _(Max run-time checks the persisted actuator_states row from phase 8. When the actuator is in running state, it compares the persisted updated_at with the current time. If the timestamp is at least 30 minutes old, the decorator blocks the call.

This data belongs to State because State already represents the actuator lifecycle. The decorator should use that lifecycle information instead of creating a second state or timer system of its own.)_

7. `GET /api/actuators/executions` feeds the dashboard execution log. Why persist attempts in the database instead of only printing to stdout? What should the UI show after a blocked attempt and a refresh?

> [!NOTE]
> ***Your Answer***
>
> _(Printing attempts to stdout would only create temporary information in backend logs. A database record survives backend restarts and can be queried by the API and displayed in the dashboard.

After a blocked attempt and a refresh, the UI should show a failed row with success=false, the policies maxRunTime and logging, and the message Max run time exceeded. A successful attempt should show success=true, policy logging, and an empty message.)_

## C. Compare, contrast, and scenarios

8. Contrast Decorator with **Adapter**. Both wrap. One **keeps** the interface and **adds** behaviour; the other **changes** the interface and **translates**. Which is which in this greenhouse (Phase 9 vs Phase 5)?

> [!NOTE]
> ***Your Answer***
>
> _(The adapter pattern changes or translates an interface so that an implementation can fit the interface expected by the application. In the earlier greenhouse adapter work, different sensor sources were adapted to the application's sensor port and normalized reading model.

The decorator in phase 9 keeps the ActuatorPort interface exactly the same and adds behavior around the call. LoggingActuatorDecorator and MaxRunTimeActuatorDecorator therefore add policies, while the wrapped object is still used through ActuatorPort.)_

9. Contrast Decorator with **inheritance** of combined policies. How does composition let you add or remove a policy without a new subclass for every combination?

> [!NOTE]
> ***Your Answer***
>
> _(With inheritance, different combinations of policies could require many subclasses, such as a logging actuator, a max-runtime actuator and then a separate subclass combining logging and max-runtime. Adding another policy would create even more combinations.

With Decorator, policies are composed by wrapping the object. We can add or remove a policy simply by changing the chain, for e.g. Logging - MaxRunTime - Simulation. No new subclass is needed for every possible combination.)_

10. A classmate’s decorator changes the method signature “a little” (extra required argument, different return type). Another ignores wrap order and cannot explain whether logging runs once per logical call or per inner attempt. Explain why each is a trap.

> [!NOTE]
> ***Your Answer***
>
> _(Changing the decorator's method signature is a trap because the decorator is supposed to remain substitutable for ActuatorPort. If one decorator requires an extra argument or returns a different type, callers can no longer use it like the wrapped component.

Ignoring wrap order is another trap because it changes which decorators see the call and its failures. For e.g. logging outside a retry wrapper can record one logical call, while logging inside the retry wrapper can record each individual retry attempt. Therefore the stack order needs to be intentional and documented.)_