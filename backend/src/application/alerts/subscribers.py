from collections.abc import Callable
from uuid import UUID

from domain.events.bus import EventBus
from domain.events.events import (
    ActuatorStateChanged,
    AlertCreated,
    CommandFailed,
    ReadingCreated,
    ThresholdCrossed,
)


class MoistureThresholdSubscriber:
    def __init__(
        self,
        bus: EventBus,
        get_zone_low: Callable[
            [UUID],
            float | None,
        ],
    ) -> None:
        self._bus = bus
        self._get_zone_low = get_zone_low

    def on_reading(
        self,
        event: ReadingCreated,
    ) -> None:
        if event.unit.lower() != "vwc":
            return

        if event.zone_id is None:
            return

        low = self._get_zone_low(
            event.zone_id
        )

        if low is None:
            return

        if event.value >= low:
            return

        self._bus.publish(
            ThresholdCrossed(
                device_id=event.device_id,
                location_id=event.location_id,
                zone_id=event.zone_id,
                value=event.value,
                threshold_low=low,
            )
        )


class AlertPersistenceSubscriber:
    def __init__(
        self,
        bus: EventBus,
        create_alert: Callable,
    ) -> None:
        self._bus = bus
        self._create_alert = create_alert

    def _save(
        self,
        *,
        location_id,
        zone_id,
        device_id,
        severity,
        message,
        event_type,
    ) -> None:
        row = self._create_alert(
            location_id=location_id,
            zone_id=zone_id,
            device_id=device_id,
            severity=severity,
            message=message,
            event_type=event_type,
        )

        # Phase 12 can subscribe to this same event.
        self._bus.publish(
            AlertCreated(
                id=row.id,
                location_id=row.location_id,
                zone_id=row.zone_id,
                device_id=row.device_id,
                severity=row.severity,
                message=row.message,
                event_type=row.event_type,
                status=row.status,
                created_at=row.created_at,
            )
        )

    def on_threshold(
        self,
        event: ThresholdCrossed,
    ) -> None:
        self._save(
            location_id=event.location_id,
            zone_id=event.zone_id,
            device_id=event.device_id,
            severity="warning",
            message="Moisture below zone low",
            event_type="threshold.crossed",
        )

    def on_command(
        self,
        event: CommandFailed,
    ) -> None:
        self._save(
            location_id=event.location_id,
            zone_id=event.zone_id,
            device_id=event.device_id,
            severity="warning",
            message=event.message,
            event_type="command.failed",
        )

    def on_state(
        self,
        event: ActuatorStateChanged,
    ) -> None:
        if event.state != "error":
            return

        self._save(
            location_id=event.location_id,
            zone_id=event.zone_id,
            device_id=event.device_id,
            severity="critical",
            message="Actuator entered error",
            event_type="state.changed",
        )