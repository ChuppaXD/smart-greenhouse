# Observer pattern - phase 11

## Intent
Observer defines a one-to-many relationship. When a
subject publishes an event, all registered observers
can react without the publisher knowing their classes.


## Problem
The Smart Greenhouse needs to react to sensor readings,
failed actuator commands, and actuator state changes.

Directly inserting alerts inside ReadingIngest,
CommandService, or ActuatorTransitionService would
couple business logic to alert persistence.

It would also make later features such as metrics
and WebSocket updates harder to add.


## Solution
The application uses one in-process EventBus with
subscribe() and publish() methods.

Publishers:
- ReadingIngest publishes ReadingCreated.
- CommandService publishes CommandFailed.
- ActuatorTransitionService publishes ActuatorStateChanged.
- CommandService also publishes ActuatorStateChanged when
  it successfully saves a changed actuator state.

Subscribers:
- MoistureThresholdSubscriber checks moisture readings
  against the low threshold of the assigned zone.
- AlertPersistenceSubscriber stores alerts in PostgreSQL.

The moisture subscriber publishes ThresholdCrossed when
a tracked vwc reading is strictly below the zone low.


## Alert types
| Event | Severity | Message |
|---|---|---|
| threshold.crossed | warning | Moisture below zone low |
| command.failed | warning | The command failure message |
| state.changed | critical | Actuator entered error |

A state.changed alert is persisted only when the
new actuator state is error.


## Reading pipeline
All reading sources use ReadingIngest.record():

- Manual sensor read
- Simulation sampler
- MQTT-translated reading

The reading is persisted first.

ReadingCreated is published only when the device's
tracking_enabled property is true.

The event contains the device ID, reading value,
unit, source, timestamp, location ID, and zone ID.

For unassigned devices, location_id and zone_id are null.


## Persistence
AlertRepository persists alerts in the alerts table.

Alerts survive browser refresh because they are stored
in PostgreSQL instead of only in React state.

Foreign keys to locations, zones, and devices are
nullable and use ON DELETE SET NULL.


## API and dashboard
GET /api/alerts returns stored alerts.

It supports:
- status: active, resolved, or all
- location_id
- zone_id
- since
- limit

The dashboard EventFeed polls the API every five seconds.

No WebSocket is implemented in Phase 11.


## Error handling
EventBus calls subscribers in subscription order.
A subscriber exception is logged, and later subscribers
still get the event.

The event bus is in-process and is not a durable
message queue. Persisted alerts provide the durable
history required for the dashboard.


## Phase 12 extension
Phase 12 can subscribe a WebSocket publisher to this
same EventBus.

The AlertPersistenceSubscriber publishes AlertCreated
after inserting a new alert.

The dashboard WebSocket can listen for AlertCreated
without duplicating sensor thresholds, command
failure rules, or alert persistence.

The frontend services/realtime.ts file is a stub until
Phase 12.


## Compared with other patterns
Facade, introduced in Phase 7, simplifies queries
into a subsystem.

Command, introduced in Phase 10, packages an intent
to perform an actuator action.

Observer distributes notifications about events
after those actions or readings occur.