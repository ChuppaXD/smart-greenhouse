from uuid import UUID

from application.alerts.subscribers import (
    AlertPersistenceSubscriber,
    MoistureThresholdSubscriber,
)
from domain.events.bus import EventBus
from domain.events.events import (
    ActuatorStateChanged,
    CommandFailed,
    ReadingCreated,
    ThresholdCrossed,
)
from infrastructure.db import SessionLocal
from infrastructure.persistence.alert_repository import (
    AlertRepository,
)
from infrastructure.persistence.models import (
    ZoneRow,
)


def get_zone_low(
    zone_id: UUID,
) -> float | None:
    with SessionLocal() as session:
        zone = session.get(
            ZoneRow,
            zone_id,
        )

        if zone is None:
            return None

        return float(
            zone.moisture_threshold_low
        )


def save_alert(**kwargs):
    with SessionLocal() as session:
        return AlertRepository(
            session
        ).create(**kwargs)


# One shared EventBus for this backend process.
event_bus = EventBus()

threshold_subscriber = (
    MoistureThresholdSubscriber(
        bus=event_bus,
        get_zone_low=get_zone_low,
    )
)

persistence_subscriber = (
    AlertPersistenceSubscriber(
        bus=event_bus,
        create_alert=save_alert,
    )
)

event_bus.subscribe(
    ReadingCreated,
    threshold_subscriber.on_reading,
)

event_bus.subscribe(
    ThresholdCrossed,
    persistence_subscriber.on_threshold,
)

event_bus.subscribe(
    CommandFailed,
    persistence_subscriber.on_command,
)

event_bus.subscribe(
    ActuatorStateChanged,
    persistence_subscriber.on_state,
)