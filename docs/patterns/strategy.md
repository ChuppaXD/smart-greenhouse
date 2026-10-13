# Strategy Pattern

## Problem
The greenhouse may need different automation behaviours for the same sensor data. For e.g. one strategy can be more careful about irrigation while another can react sooner.
Putting all of these rules into one service or API route would make the code harder to change.


## Solution
The strategy pattern puts each algorithm into its own class behind one common interface.
AutomationStrategy defines the decide(context) operation.
This phase has two concrete strategies:
* ConservativeMoistureStrategy
* AggressiveMoistureStrategy

Both receive the same LocationAutomationContext, but they can make different decisions.
The conservative strategy waits while moisture is inside the configured low / high band and only recommends irrigation below the low threshold.
The aggressive strategy recommends irrigation whenever moisture is below the high threshold, so it reacts sooner.


## Where it is used
The main Strategy code is in:
* domain/automation/strategy.py
* domain/automation/context.py
* application/automation/service.py
* infrastructure/persistence/automation_repository.py
* interfaces/api/automation.py
* frontend/src/features/automation/StrategyPanel.tsx

The repository loads the latest moisture readings from sensors assigned to each zone and combines them with the zone's stored thresholds.
The strategy classes only receive the plain python context. They do not use SQLAlchemy, FastAPI or database rows.


## Persisted strategy
The selected strategy is stored in the automation_rules table.
Each location_id can have only one active strategy.
The API saves the selected strategy before evaluation. Evaluation then reads the saved strategy from the database instead of trusting a temporary query parameter.


## Zone readings
Evaluation is done per zone.
Only readings from sensors whose devices.zone_id belongs to that zone are used.
A zone with no assigned moisture sensor does not use another zone's sensor. It produces a wait result explaining that there is no moisture sensor in that zone.


## Adding a third strategy
A third strategy could be added by creating another class that implements AutomationStrategy, for e.g. an EnergySavingStrategy.
It would implement its own decide(context) method and be added to the strategy lookup.

The application service and API would not need separate if blocks for the new algorithm.