from uuid import uuid4

from fastapi.testclient import (
    TestClient,
)

from main import app


client = TestClient(app)


def create_test_location():
    response = client.post(
        "/api/locations/config",
        json={
            "location_name": "Phase 7 Overview Test",
            "zones": [
                {
                    "name": "Zone A",
                    "moisture_threshold_low": 0.25,
                    "moisture_threshold_high": 0.45,
                    "schedule": {},
                },
                {
                    "name": "Zone B",
                    "moisture_threshold_low": 0.30,
                    "moisture_threshold_high": 0.60,
                    "schedule": {},
                },
            ],
        },
    )

    assert response.status_code == 201

    return response.json()


def create_test_sensor(
    display_name: str,
):
    response = client.post(
        "/api/sensors",
        json={
            "type": "moisture",
            "display_name": display_name,
        },
    )

    assert response.status_code == 201

    return response.json()


def test_overview_returns_strategy_and_readings():
    missing_location_response = client.get(
        f"/api/locations/{uuid4()}/overview"
    )

    assert (
        missing_location_response.status_code
        == 404
    )

    config = create_test_location()

    location_id = config["location"]["id"]

    zones = config["zones"]

    assert len(zones) == 2

    sensor_assigned = create_test_sensor(
        "Overview assigned moisture"
    )

    sensor_unassigned = create_test_sensor(
        "Overview unassigned moisture"
    )

    assigned_sensor_id = (
        sensor_assigned["id"]
    )

    unassigned_sensor_id = (
        sensor_unassigned["id"]
    )

    assign_response = client.patch(
        f"/api/devices/{assigned_sensor_id}/zone",
        json={
            "zone_id": zones[0]["id"]
        },
    )

    assert (
        assign_response.status_code
        == 204
    )

    read_response = client.post(
        f"/api/sensors/{assigned_sensor_id}/read"
    )

    assert (
        read_response.status_code
        == 200
    )

    before_strategy = client.get(
        f"/api/locations/{location_id}/overview"
    )

    assert (
        before_strategy.status_code
        == 200
    )

    before_body = (
        before_strategy.json()
    )

    assert (
        before_body["location"]["name"]
        == "Phase 7 Overview Test"
    )

    assert (
        before_body["strategy_key"]
        is None
    )

    assert (
        before_body["last_recommendation"]
        is None
    )

    assert (
        before_body["device_counts"]["sensor"]
        == 1
    )

    zone_a = next(
        zone
        for zone in before_body["zones"]
        if zone["name"] == "Zone A"
    )

    zone_b = next(
        zone
        for zone in before_body["zones"]
        if zone["name"] == "Zone B"
    )

    zone_a_device_ids = {
        device["id"]
        for device in zone_a["devices"]
    }

    zone_b_device_ids = {
        device["id"]
        for device in zone_b["devices"]
    }

    assert (
        assigned_sensor_id
        in zone_a_device_ids
    )

    assert (
        unassigned_sensor_id
        not in zone_a_device_ids
    )

    assert (
        unassigned_sensor_id
        not in zone_b_device_ids
    )

    assert (
        zone_b["devices"]
        == []
    )

    assert (
        zone_b["latest_readings"]
        == []
    )

    assert (
        len(zone_a["latest_readings"])
        == 1
    )

    reading = (
        zone_a["latest_readings"][0]
    )

    assert (
        reading["device_id"]
        == assigned_sensor_id
    )

    assert "value" in reading
    assert "unit" in reading
    assert "recorded_at" in reading
    assert (
        "tracking_enabled"
        in reading
    )
    assert (
        "sampling_interval_seconds"
        in reading
    )

    strategy_response = client.put(
        f"/api/locations/{location_id}/automation",
        json={
            "strategy_key": "conservative"
        },
    )

    assert (
        strategy_response.status_code
        == 200
    )

    evaluate_response = client.post(
        f"/api/locations/{location_id}/automation/evaluate"
    )

    assert (
        evaluate_response.status_code
        == 200
    )

    evaluate_body = (
        evaluate_response.json()
    )

    after_strategy = client.get(
        f"/api/locations/{location_id}/overview"
    )

    assert (
        after_strategy.status_code
        == 200
    )

    after_body = (
        after_strategy.json()
    )

    assert (
        after_body["strategy_key"]
        == "conservative"
    )

    assert (
        after_body[
            "last_recommendation"
        ]["action"]
        == evaluate_body["action"]
    )

    assert (
        after_body[
            "last_recommendation"
        ]["reason"]
        == evaluate_body["reason"]
    )