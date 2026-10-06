from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def get_simulation_sensor():
    response = client.get(
        "/api/devices?role=sensor"
    )

    assert response.status_code == 200

    devices = response.json()

    for device in devices:
        protocol = (
            device.get("default_config", {})
            .get("protocol")
        )

        if protocol in {
            "simulation",
            "sim",
        }:
            return device

    response = client.post(
        "/api/devices/provision?family=simulation"
    )

    assert response.status_code == 201

    devices = response.json()

    for device in devices:
        if device["role"] == "sensor":
            return device

    raise AssertionError(
        "No simulation sensor was available."
    )


def test_read_inserts_sensor_reading():
    device = get_simulation_sensor()

    device_id = device["id"]

    before_response = client.get(
        f"/api/sensors/{device_id}/readings?limit=100"
    )

    assert (
        before_response.status_code
        == 200
    )

    before = (
        before_response.json()
    )

    response = client.post(
        f"/api/sensors/{device_id}/read"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["device_id"] == device_id
    assert body["source"] == "simulation"
    assert "value" in body
    assert "unit" in body
    assert "recorded_at" in body

    after_response = client.get(
        f"/api/sensors/{device_id}/readings?limit=100"
    )

    assert (
        after_response.status_code
        == 200
    )

    after = (
        after_response.json()
    )

    assert len(after) > len(before)