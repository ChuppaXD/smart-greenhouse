# Phase 11 — Observer questions

**Pattern / focus:** Observer.

**Read first:** [Guide 11](../../materials/guides/11-observer.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example live auction bids) as if they were your greenhouse classes.
- When a question asks about _this application_, refer to the event bus, alerts, publishers, and the event feed from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Observer in plain language. What is a **one-to-many** dependency here, and why must the subject notify dependents **without** knowing their concrete classes?

> [!NOTE]
> **_Your Answer_**
>
> _(Observer allows one subject to notify multiple subscribers when something happens without knowing their concrete implementations. In our greenhouse, the EventBus provides this one-to-many relationship. Different subscribers can react to the same event without the publisher depending on them directly.)_

2. Name the participants (**subject / event bus**, **observer / subscriber**, **concrete observers**, **event**, **publisher**). What does `subscribe` / `unsubscribe` / `publish` (or `notify`) each do? This example’s `EventBus` implements `subscribe` and `publish` only.

> [!NOTE]
> **_Your Answer_**
>
> _(The subject is EventBus. Publishers include ReadingIngest, CommandService and ActuatorTransitionService. The concrete observers are MoistureThresholdSubscriber and AlertPersistenceSubscriber and the events are objects such as ReadingCreated and CommandFailed. subscribe() registers a handler, publish() notifies registered handlers and unsubscribe() would remove a handler, although our Phase 11 bus does not implement it.)_

3. When should you use Observer, and when should you skip it (only one listener forever; or you need a strict multi-step workflow with guaranteed order)?

> [!NOTE]
> **_Your Answer_**
>
> _(Observer is useful when one event should trigger several independent reactions, such as creating alerts, collecting metrics and notifying the dashboard. It is less useful when there will only ever be one simple listener. It is also not suitable by itself for a strict workflow requiring guaranteed execution order and completion of every step.)_

## B. This phase of the application

4. Give at least two **domain events** you publish in this lab, including `reading.created` (only when `tracking_enabled` is true), a threshold-crossed event, command-failed, and `ActuatorStateChanged`. The persistence subscriber stores `state.changed` only when that state is `error`. Who publishes `reading.created`, and why do a manual read, the simulation sampler, and MQTT translation share that one ingest publish? Why must a publisher **not** import the alerts repository or the UI?

> [!NOTE]
> **_Your Answer_**
>
> _(Our greenhouse publishes ReadingCreated, ThresholdCrossed, CommandFailed and ActuatorStateChanged. ReadingIngest publishes ReadingCreated after saving a reading, but only when tracking is enabled. Manual readings, simulation sampler readings and MQTT-translated readings use the same record() method, so they follow one publishing rule. Publishers do not import the alerts repository or UI because subscribers are responsible for those reactions.)_

5. What does `AlertPersistenceSubscriber` (or your equivalent) do when it handles an event? Name the three stored rows: `threshold.crossed` / `warning` / `Moisture below zone low`, `command.failed` / `warning` / the failure message, and `state.changed` / `critical` / `Actuator entered error`. Why do alerts live in the `alerts` table so the event feed still shows them after a **refresh**?

> [!NOTE]
> **_Your Answer_**
>
> _(AlertPersistenceSubscriber reacts to events and creates database rows. It stores threshold.crossed as a warning with the message Moisture below zone low, command.failed as a warning containing the failure message and state.changed as a critical alert with Actuator entered error only when the new state is error. Saving these rows in PostgreSQL lets the Event Feed display alerts even after the page is refreshed.)_

6. The dashboard Event feed **polls** `GET /api/alerts` every 5 seconds in this phase. `services/realtime.ts` is only a **stub**. Why is full WebSocket **not** required in this phase? What should Phase 12 plug into so you do **not** re-implement pub/sub inside socket handlers? Phase 12 subscribes a dashboard socket to this same bus, and the example publishes `AlertCreated` after each insert for that socket.

> [!NOTE]
> **_Your Answer_**
>
> _(Phase 11 uses HTTP polling every five seconds, so it does not need a live WebSocket connection. The realtime.ts file is only a stub. Phase 12 can subscribe a WebSocket broadcaster to the same EventBus, including the AlertCreated events published after alert persistence, without implementing a second event system inside the socket handlers.)_

7. Describe the must-demo path: a **tracked** low-moisture reading leads to an alert row that appears in the feed after poll. Which objects collaborate (reading pipeline → bus → subscriber → API → UI), and which object must **not** write the alert directly? What is stored, and what is not published, when `tracking_enabled` is false?

> [!NOTE]
> **_Your Answer_**
>
> _(A tracked moisture reading is saved through ReadingIngest, which publishes ReadingCreated. The EventBus notifies MoistureThresholdSubscriber, which checks the zone's low threshold and publishes ThresholdCrossed when the value is below it. AlertPersistenceSubscriber stores the alert, GET /api/alerts retrieves it and the Event Feed displays it after polling. The reading service must not insert the alert directly. With tracking disabled, the reading can still be stored, but ReadingCreated is not published.)_

## C. Compare, contrast, and scenarios

8. Contrast Observer with **Facade**. Facade simplifies **calling into** a subsystem. Observer **fans out** notifications after something happened. How do both appear in this greenhouse (Phase 7 overview vs this phase)?

> [!NOTE]
> **_Your Answer_**
>
> _(Facade provides a simplified interface for accessing a subsystem. In Phase 7, our overview facade combines greenhouse information into one response. Observer works in the opposite direction: after something happens, it distributes notifications to subscribers. Phase 11 uses the EventBus to notify the alert-related subscribers.)_

9. Contrast Observer with **Command**. Command captures **intent to act**. Observer propagates **outcomes**. How can `execute()` publish an event without the command class knowing who persists alerts?

> [!NOTE]
> **_Your Answer_**
>
> _(Command represents an intention to perform an action, such as starting or stopping a pump. Observer notifies other components about events resulting from actions. In Phase 10, CommandService executes the command through the invoker and decorated actuator port. In Phase 11, it can publish CommandFailed to the EventBus without the command class needing to know which subscriber persists alerts.)_

10. One subscriber throws during `notify` / `publish` and aborts the loop, so later subscribers never run. Why is that a trap? What should the bus do so a failing alert writer does not block metrics (or later WebSocket) subscribers?

> [!NOTE]
> **_Your Answer_**
>
> _(If one subscriber throws an exception and the bus stops notifying handlers, other subscribers might miss important events. For e.g. an alert database failure should not prevent a metrics or future WebSocket subscriber from receiving a notification. The EventBus should catch and log exceptions for individual subscribers and continue notifying the remaining handlers. For stronger delivery guarantees, a durable queue or outbox would be needed beyond this simple in-process bus.)_