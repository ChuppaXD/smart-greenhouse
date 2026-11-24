from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from application.alerts.subscribers import (
    AlertPersistenceSubscriber,
    MoistureThresholdSubscriber,
)
from application.readings.service import ReadingIngest
from domain.events.bus import EventBus
from domain.events.events import (
    ActuatorStateChanged,
    CommandFailed,
    ReadingCreated,
    ThresholdCrossed,
)
from domain.sensors.reading import Reading


def current_time():
    return datetime.now(timezone.utc)


class FakeAlertStorage:
    def __init__(self):
        self.rows = []

    def create(self, **kwargs):
        row = SimpleNamespace(
            id=uuid4(),
            status="active",
            created_at=current_time(),
            **kwargs,
        )

        self.rows.append(row)
        return row


class FakeDeviceRepository:
    def __init__(self, device):
        self.device = device

    def get_device(self, device_id):
        return self.device


class FakeReadingRepository:
    def __init__(self):
        self.rows = []

    def insert(self, reading):
        self.rows.append(reading)
        return reading


def make_alert_bus():
    bus = EventBus()
    storage = FakeAlertStorage()

    threshold = MoistureThresholdSubscriber(
        bus=bus,
        get_zone_low=lambda zone_id: 0.20,
    )

    persistence = AlertPersistenceSubscriber(
        bus=bus,
        create_alert=storage.create,
    )

    bus.subscribe(
        ReadingCreated,
        threshold.on_reading,
    )

    bus.subscribe(
        ThresholdCrossed,
        persistence.on_threshold,
    )

    bus.subscribe(
        CommandFailed,
        persistence.on_command,
    )

    bus.subscribe(
        ActuatorStateChanged,
        persistence.on_state,
    )

    return bus, storage


@pytest.mark.parametrize(
    "tracking_enabled",
    [True, False],
)
def test_reading_publish_rule(
    tracking_enabled,
):
    bus = EventBus()
    published = []

    bus.subscribe(
        ReadingCreated,
        published.append,
    )

    device_id = uuid4()

    device = SimpleNamespace(
        id=device_id,
        role="sensor",
        tracking_enabled=tracking_enabled,
        location_id=None,
        zone_id=None,
    )

    repository = FakeReadingRepository()

    ingest = ReadingIngest(
        device_repository=FakeDeviceRepository(
            device
        ),
        reading_repository=repository,
        adapter_selector=None,
        event_bus=bus,
    )

    reading = Reading(
        device_id=device_id,
        value=0.10,
        unit="vwc",
        source="simulation",
        recorded_at=current_time(),
    )

    ingest.record(
        device_id,
        reading,
    )

    # Stored regardless of tracking flag.
    assert len(repository.rows) == 1

    # Published only when tracking is enabled.
    assert len(published) == int(
        tracking_enabled
    )


def test_low_moisture_creates_alert():
    bus, storage = make_alert_bus()

    location_id = uuid4()
    zone_id = uuid4()
    device_id = uuid4()

    bus.publish(
        ReadingCreated(
            device_id=device_id,
            value=0.10,
            unit="vwc",
            source="simulation",
            recorded_at=current_time(),
            location_id=location_id,
            zone_id=zone_id,
        )
    )

    assert len(storage.rows) == 1

    alert = storage.rows[0]

    assert alert.event_type == (
        "threshold.crossed"
    )
    assert alert.severity == "warning"
    assert alert.message == (
        "Moisture below zone low"
    )
    assert alert.zone_id == zone_id
    assert alert.location_id == location_id


def test_boundary_does_not_create_alert():
    bus, storage = make_alert_bus()

    bus.publish(
        ReadingCreated(
            device_id=uuid4(),
            value=0.20,
            unit="vwc",
            source="simulation",
            recorded_at=current_time(),
            zone_id=uuid4(),
        )
    )

    assert storage.rows == []


def test_unassigned_reading_no_threshold():
    bus, storage = make_alert_bus()

    bus.publish(
        ReadingCreated(
            device_id=uuid4(),
            value=0.10,
            unit="vwc",
            source="simulation",
            recorded_at=current_time(),
            zone_id=None,
        )
    )

    assert storage.rows == []


def test_failed_command_creates_alert():
    bus, storage = make_alert_bus()

    bus.publish(
        CommandFailed(
            device_id=uuid4(),
            location_id=None,
            zone_id=None,
            command_type="stop_pump",
            message="Max run time exceeded",
        )
    )

    assert len(storage.rows) == 1

    alert = storage.rows[0]

    assert alert.event_type == (
        "command.failed"
    )
    assert alert.severity == "warning"
    assert alert.message == (
        "Max run time exceeded"
    )
    assert alert.location_id is None
    assert alert.zone_id is None


def test_error_state_creates_critical_alert():
    bus, storage = make_alert_bus()

    device_id = uuid4()

    bus.publish(
        ActuatorStateChanged(
            device_id=device_id,
            location_id=None,
            zone_id=None,
            state="error",
        )
    )

    assert len(storage.rows) == 1

    alert = storage.rows[0]

    assert alert.event_type == (
        "state.changed"
    )
    assert alert.severity == "critical"
    assert alert.message == (
        "Actuator entered error"
    )


def test_non_error_state_no_alert():
    bus, storage = make_alert_bus()

    bus.publish(
        ActuatorStateChanged(
            device_id=uuid4(),
            location_id=None,
            zone_id=None,
            state="running",
        )
    )

    assert storage.rows == []


def test_bad_subscriber_does_not_block_next():
    bus = EventBus()
    received = []

    def broken_handler(event):
        raise RuntimeError(
            "Subscriber failed"
        )

    bus.subscribe(
        CommandFailed,
        broken_handler,
    )

    bus.subscribe(
        CommandFailed,
        received.append,
    )

    event = CommandFailed(
        device_id=uuid4(),
        location_id=None,
        zone_id=None,
        command_type="stop_pump",
        message="Max run time exceeded",
    )

    bus.publish(event)

    assert received == [event]