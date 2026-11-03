from uuid import uuid4

from fastapi.testclient import TestClient

from domain.actuators.context import ActuatorContext
from domain.actuators.state import (
    IllegalTransitionError,
)
from main import app


client = TestClient(app)


def test_idle_to_running_allowed():
    context = ActuatorContext.from_state_name(
        device_type="water_pump",
        state="idle",
    )

    context.transition("running")

    assert context.state == "running"

    assert context.allowed_commands() == [
        "stop_pump"
    ]


def test_running_to_maintenance_rejected():
    context = ActuatorContext.from_state_name(
        device_type="water_pump",
        state="running",
    )

    try:
        context.transition("maintenance")

        assert False, (
            "Expected IllegalTransitionError"
        )

    except IllegalTransitionError:
        pass

    assert context.state == "running"


def test_all_states_have_expected_error_and_reset_path():
    context = ActuatorContext.from_state_name(
        device_type="grow_light",
        state="idle",
    )

    context.transition("error")

    assert context.state == "error"

    assert context.allowed_commands() == [
        "reset_error"
    ]

    context.transition("idle")

    assert context.state == "idle"


def test_illegal_transition_does_not_update_row():
    provision = client.post(
        "/api/devices/provision?family=simulation"
    )

    assert provision.status_code == 201

    actuator = next(
        device
        for device in provision.json()
        if device["role"] == "actuator"
    )

    device_id = actuator["id"]

    start = client.post(
        f"/api/devices/{device_id}/transition",
        json={
            "target": "running"
        },
    )

    assert start.status_code == 200

    assert (
        start.json()["state"]
        == "running"
    )

    illegal = client.post(
        f"/api/devices/{device_id}/transition",
        json={
            "target": "maintenance"
        },
    )

    assert illegal.status_code == 409

    devices = client.get(
        "/api/devices?role=actuator"
    )

    assert devices.status_code == 200

    current = next(
        device
        for device in devices.json()
        if device["id"] == device_id
    )

    assert current["state"] == "running"

    stop = client.post(
        f"/api/devices/{device_id}/transition",
        json={
            "target": "idle"
        },
    )

    assert stop.status_code == 200

    assert (
        stop.json()["state"]
        == "idle"
    )


def test_device_json_exposes_state_and_allowed_commands():
    provision = client.post(
        "/api/devices/provision?family=simulation"
    )

    assert provision.status_code == 201

    actuators = [
        device
        for device in provision.json()
        if device["role"] == "actuator"
    ]

    assert len(actuators) == 2

    for device in actuators:
        assert device["state"] == "idle"

        assert isinstance(
            device["allowed_commands"],
            list,
        )

        assert device["allowed_commands"]


def test_missing_actuator_returns_404():
    response = client.post(
        f"/api/devices/{uuid4()}/transition",
        json={
            "target": "running"
        },
    )

    assert response.status_code == 404