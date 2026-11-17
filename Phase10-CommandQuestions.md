# Phase 10 — Command questions

**Pattern / focus:** Command.

**Read first:** [Guide 10](../../materials/guides/10-command.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example editor undo commands) as if they were your greenhouse classes.
- When a question asks about _this application_, refer to command objects, the invoker, `command_log`, and the controls UI from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Command in plain language. What does it mean to **objectify a request**, and what can you do with that object that you cannot do with a bare `actuator.start()` call (queue, audit, undo, history)?

> [!NOTE]
> **_Your Answer_**
>
> _(The Command pattern turns an action into an object. In this project, starting a pump is represented by StartPumpCommand instead of the router directly calling the actuator. Because the request is an object, it can be checked, executed through an invoker, stored in command_log, and later used for things like queues, history or undo.)_

2. Name the participants (**command**, **receiver**, **invoker**, **client**). Who creates the command, who triggers `execute()`, and who actually changes actuator/hardware state?

> [!NOTE]
> **_Your Answer_**
>
> _(The command is StartPumpCommand, StopPumpCommand or SetLightLevelCommand. The receiver is the actuator port and behind it, the actuator adapter that actually performs the actuator action. The invoker is CommandInvoker, which calls execute() on the command. The application service creates the command from the HTTP request. The real actuator behavior is reached through the existing phase 9 decorated ActuatorPort, ending at SimulationActuatorAdapter.)_

3. If a command supports undo, when must it capture the data needed to reverse the action? Why is “capture **before** mutate” critical?

> [!NOTE]
> **_Your Answer_**
>
> _(For an undo operation, the command must save the information needed to reverse the action before changing anything. For e.g. if a light level is changed, the old light level would need to be known before the new level is written.

Capturing it after the change may lose the old value, so the command would no longer know what to restore. That is why the information needed for undo must be captured before the mutation.)_

## B. This phase of the application

4. Which command types did you implement (for example `start_pump`, `stop_pump`, `set_light_level`)? Why does the HTTP handler create a command and pass it to an **invoker** (or application service) instead of calling the actuator adapter from the router?

> [!NOTE]
> **_Your Answer_**
>
> _(I implemented start_pump, stop_pump and set_light_level. The HTTP handler should create the command request and pass it to the application service, which uses the command registry and CommandInvoker.

The router should not call the actuator adapter directly because that would bypass the State guard, the phase 9 decorators and the command_log history. Keeping this in the command service also keeps the router small.)_

5. Walk through the execute path: (1) consult State / `allowed_commands`, (2) if illegal → **rejected**, (3) if legal → decorated `apply`, update `actuator_states`, log **success** or **failed**. Why must a rejected command **not** change actuator state and **not** reach inner `apply`?

> [!NOTE]
> **_Your Answer_**
>
> _(First the service loads the actuator State and checks allowed_commands().
If the command is not allowed, it writes a rejected row to command_log and stops immediately. There is no apply() call and no State change.
If the command is allowed, the command is sent through CommandInvoker to the decorated ActuatorPort. If that succeeds, the service changes actuator_states through ActuatorContext.transition() when a target state is needed and then writes a success row.
If a phase 9 policy such as max run time blocks the command, the result is failed. The State is left unchanged.)_

6. Distinguish **`rejected`** vs **`failed`** vs **`success`** in `command_log`. Give one greenhouse example of each. Why is “illegal in this state” not the same as “policy or adapter error after the command was accepted”?

> [!NOTE]
> **_Your Answer_**
>
> _(rejected means the request was not legal for the current actuator State. For e.g. trying start_pump when the pump is already running.
failed means the command was allowed, but something stopped it while it was being executed. For e.g. max run time can block set_light_level after the actuator has been running for at least 30 minutes.
success means the command passed the State guard and the decorated port completed the action.
An illegal state and a policy failure are different because the first one is rejected before execution, while the second one happens after the command has already been accepted.)_

7. Why is `command_log` a **different** table from Phase 9 `actuator_execution_log`? What concern does each log record (operator intent vs policy/adapter attempt)?

> [!NOTE]
> **_Your Answer_**
>
> _(command_log records the command request itself. It tells us what action was requested, for which device, what payload was used and whether the command was successful, failed or rejected.
actuator_execution_log belongs to Phase 9 and records what happened around the decorated actuator attempt, such as logging and max-runtime policies.
A rejected command may therefore appear in command_log without creating a row in actuator_execution_log, because it never reached the decorated port.)_

## C. Compare, contrast, and scenarios

8. Contrast Command with **Strategy**. Strategy is an interchangeable **algorithm** (decide / quote). Command is a **side-effectful request** with history. How do they cooperate in this app (Phase 6 recommends; Phase 10 executes)?

> [!NOTE]
> **_Your Answer_**
>
> _(Strategy is about choosing or calculating an algorithm or decision. In this project, phase 6 Strategy can evaluate the greenhouse situation and recommend an action.
Whereas, Command is about representing and executing a concrete action. In phase 10, a command such as StartPumpCommand performs the requested operation and creates an audit record.
They can work together: Strategy can recommend what should happen, and Command can be used later to actually perform that action in a controlled and auditable way.)_

9. Contrast Command with **State**. Who **triggers** the action, and who **decides whether it is legal**? Why must commands not bypass state guards?

> [!NOTE]
> **_Your Answer_**
>
> _(The Command represents the action that someone or something wants to perform. State decides whether that action is legal at the current time.
For e.g. StopPumpCommand can represent a request to stop the pump, while the State's allowed_commands() decides whether stopping is currently allowed.
Commands must not bypass the state guard because otherwise an illegal action could change the actuator even though the State machine says it is not permitted.)_

10. The controls UI should disable actions that are not in `allowed_commands`. Why must the **backend** still reject illegal commands even if the UI is correct? What happens if a classmate’s command calls the raw adapter and skips State and Decorator?

> [!NOTE]
> **_Your Answer_**
>
> _(The UI is only a convenience for the user. A request can still be sent directly through Scalar, curl, another client or a modified frontend. Therefore the backend must always check allowed_commands() itself.
If a command calls the raw adapter and skips State and Decorator, it could perform an illegal action, change the actuator without the correct lifecycle rules and also skip the phase 9 logging and max-runtime policies.
That would break the main purpose of the architecture, because the command would no longer pass through the same guarded and auditable path as every other actuator action.)_
