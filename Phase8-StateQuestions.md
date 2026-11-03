# Phase 8 — State questions

**Pattern / focus:** State.

**Read first:** [Guide 08](../../materials/guides/08-state.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example support-ticket states) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to actuator lifecycle, persisted state, and `allowed_commands` from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of the State pattern in plain language. What problem appears when lifecycle is modelled as boolean flags and scattered `if` guards?

> [!NOTE]
> ***Your Answer***
>
> _(The state pattern puts the rules for an object's different lifecycle states in one place. In our greenhouse, an actuator can be idle, running, in maintenance, off or in error. If we used many boolean flags and 'if' statements, we could create invalid combinations such as running and maintenance being true at the same time. The state pattern makes the current state explicit and controls which transitions are legal.)_

2. Name the participants (**context**, **state interface**, **concrete states**, **client**). How does a successful command lead to a **transition**, and where do **guards** live?

> [!NOTE]
> ***Your Answer***
>
> _(The context is ActuatorContext. The state interface is ActuatorState. The concrete states are OffState, IdleState, RunningState, ErrorState and MaintenanceState. The client is the application service that asks the context to transition. The transition guard is inside the domain state classes and ActuatorContext, not in the router or React. If the transition is legal, the context changes state and the application service saves the new state.)_

3. What is `allowed_commands` (or equivalent) for? Why is exposing “what can I do **now**?” better than letting the UI guess from a raw state string?

> [!NOTE]
> ***Your Answer***
>
> _(allowed_commands tells the client which commands are legal in the current state. For e.g. a running pump can allow stop_pump, while an idle pump can allow start_pump. This is better than making the UI guess from a state string because the domain remains the single source of truth. The UI only displays what the backend says is allowed.)_

## B. This phase of the application

4. Which actuator states did you implement (for example idle, running, error)? Sketch the **legal** transitions (which command or event moves idle → running, running → idle, into error, and out of error).

> [!NOTE]
> ***Your Answer***
>
> _(I implemented off, idle, running, maintenance and error.
The main legal transitions are:
off - idle
idle - running
running - idle
idle - maintenance
maintenance - idle
idle - off
maintenance - off
-Any normal state can move to 'error' when a fault happens. From 'error', the actuator can return to 'idle' after a reset.
For e.g. start_pump can move a pump from idle to running, while stop_pump moves it from running back to idle.)_

5. Why is actuator state stored in `actuator_states` (or equivalent) rather than only in process memory? What must still be true after you restart the backend?

> [!NOTE]
> ***Your Answer***
>
> _(The state is stored in actuator_states because process memory would be lost when the backend restarts. PostgreSQL keeps the current lifecycle state as persistent data. After restarting the backend, an actuator that was running before the restart must still be reported as running and its allowed_commands must still match that state.)_

6. An **illegal** transition must raise a domain error and **must not** update the database. Why? Which HTTP status is reasonable for that case (400 or 409), and why should the rule live in the domain rather than in React?

> [!NOTE]
> ***Your Answer***
>
> _(An illegal transition must not change the database because the actuator would otherwise enter a state that is not allowed by the lifecycle rules. I used IllegalTransitionError in the domain. HTTP 409 conflict is reasonable because the requested action conflicts with the actuator's current state. The rule belongs in the domain because the same rule must work for the API, future command code and other clients. React is only the user interface and should not be the source of the business rule.)_

7. Device JSON gains `state` and `allowed_commands`. How does the dashboard use those fields (badges, disable illegal buttons)? How does this prepare **Phase 10 Command**?

> [!NOTE]
> ***Your Answer***
>
> _(The dashboard shows the actuator's current state as a badge and displays the allowed commands. For e.g. a running pump shows running and stop_pump. The UI does not recreate the transition rules itself. In phase 10, command can use the same allowed_commands and state guards to check that a command is legal before executing it through the actuator port.)_

## C. Compare, contrast, and scenarios

8. Contrast State with **Strategy**. Both look like “context delegates to an object.” Who typically **changes** the active object, and is the variation a **lifecycle** or a **selectable policy**? Give a greenhouse example of each (this phase vs Phase 6).

> [!NOTE]
> ***Your Answer***
>
> _(State represents the current lifecycle of an object and normally changes because the object's commands or events move it to another state. In this phase, an actuator changes from idle to running or from running to idle.
-Strategy represents a selectable policy. In phase 6, the location can use the conservative or aggressive moisture strategy. The strategy is selected as an automation policy, while the actuator state changes as part of its lifecycle.)_

9. Contrast State with a pile of booleans (`is_running`, `is_fault`, `is_maintenance`). Why do illegal combinations of flags appear, and how do explicit state objects (or a transition table) prevent that?

> [!NOTE]
> ***Your Answer***
>
> _(With several booleans, different flags can accidentally become true at the same time. For e.g. an actuator could end up with is_running = true and is_maintenance = true, even though those situations should not happen together. Explicit states represent one lifecycle state at a time. The transition table also defines which next states are legal, so invalid combinations are avoided.
)_

10. A classmate puts HTTP status mapping or SQLAlchemy commits **inside** a concrete state class. Another state mutates a flag directly and skips `transition` / `set_state`. Explain why each is a trap.

> [!NOTE]
> ***Your Answer***
>
> _(Putting HTTP status mapping inside a concrete state class mixes the domain with the API layer. The domain should not know about FastAPI or HTTP status codes. Putting SQLAlchemy commits inside a state class also mixes the domain with persistence. The repository and application service should handle database operations.

-If a state changes a flag directly and skips transition or set_state, it can bypass the lifecycle guards and the normal persistence flow. That could allow an illegal state or leave the database and the domain object out of sync. The transition should always go through the domain rules first and then be saved by the application and repository layers.)_