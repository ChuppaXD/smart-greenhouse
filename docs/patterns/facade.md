# Facade pattern

## Problem
The dashboard needs information from several parts of the Smart Greenhouse application at the same time.

It needs the location and zones, assigned devices, latest readings, the saved automation strategy and the current recommendation.

Without a facade, the dashboard or HTTP route would need to know about several repositories and services and combine their results itself.


## Solution
The facade pattern provides one simple entry point for this larger operation.

LocationOverviewFacade.get_overview(location_id) creates one overview read model for the selected location.

The facade coordinates the existing location/device/reading data and the phase 6 automation service.

The HTTP handler only calls the facade.


## Where it is used
The main code is:
- application/overview/dto.py
- application/overview/facade.py
- infrastructure/persistence/overview_repository.py
- interfaces/api/overview.py
- frontend/src/features/overview/OverviewPanel.tsx

The overview repository performs the database queries.

The facade converts those results into one LocationOverviewDto.

The automation service remains responsible for "Strategy" decisions. The facade does not reimplement irrigation logic.


## Recommendation
last_recommendation is calculated when the overview is requested and a strategy key has been saved.

The recommendation is not stored in another table and is not cached by the facade.

This means a new reading or a changed strategy is visible the next time the overview is fetched.


## Query shape
The overview loads the location and its zones, then gets assigned devices for that location and the newest reading for those device ids.

The latest reading query gets one newest row per device instead of querying readings separately for every device.

The existing automation evaluation may still perform its own per zone moisture lookup. That logic stays inside the automation service.


## Database
No new business table is needed for the overview.

The facade composes data that already exists from the earlier phases:
- locations and zones
- devices and assignments
- sensor readings
- automation rules

The overview is therefore a read model, not a new business entity.


## Extending the facade
Later phases can be added for more information to the overview without making the dashboard call many different backend endpoints.

For e.g. a later phase could include actuator lifecycle information while keeping the dashboard entry point as one overview request.