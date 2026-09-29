from uuid import uuid4

from fastapi.testclient import TestClient

from domain.locations.config_builder import (
    LocationConfigBuilder,
)
from domain.locations.errors import ConfigurationError
from main import app


client = TestClient(app)


def test_build_success():
    config = (
        LocationConfigBuilder()
        .with_location_name("Test Site")
        .add_zone(
            name="Zone A",
            moisture_threshold_low=0.2,
            moisture_threshold_high=0.45,
            schedule={"watering": "08:00"},
        )
        .build()
    )

    assert config.location.name == "Test Site"
    assert len(config.location.zones) == 1
    assert config.location.zones[0].name == "Zone A"


def test_build_requires_name():
    try:
        (
            LocationConfigBuilder()
            .add_zone(
                name="Zone A",
                moisture_threshold_low=0.2,
                moisture_threshold_high=0.4,
            )
            .build()
        )

        assert False, "Expected ConfigurationError"

    except ConfigurationError:
        pass


def test_build_requires_zones():
    try:
        (
            LocationConfigBuilder()
            .with_location_name("Test Site")
            .build()
        )

        assert False, "Expected ConfigurationError"

    except ConfigurationError:
        pass


def test_build_rejects_invalid_thresholds():
    try:
        (
            LocationConfigBuilder()
            .with_location_name("Test Site")
            .add_zone(
                name="Zone A",
                moisture_threshold_low=0.8,
                moisture_threshold_high=0.2,
            )
        )

        assert False, "Expected ConfigurationError"

    except ConfigurationError:
        pass


def create_location(
    location_name: str | None = None,
    zones: list[dict] | None = None,
):
    name = location_name or (
        f"Test Location {uuid4().hex[:8]}"
    )

    zone_data = zones or [
        {
            "name": "Zone A",
            "moisture_threshold_low": 0.2,
            "moisture_threshold_high": 0.45,
            "schedule": {"watering": "08:00"},
        }
    ]

    response = client.post(
        "/api/locations/config",
        json={
            "location_name": name,
            "zones": zone_data,
        },
    )

    assert response.status_code == 201

    return response.json()


def ensure_devices(count: int = 2):
    devices = client.get(
        "/api/devices"
    ).json()

    if len(devices) < count:
        provision = client.post(
            "/api/devices/provision?family=simulation"
        )

        assert provision.status_code == 201

        devices = client.get(
            "/api/devices"
        ).json()

    assert len(devices) >= count

    return devices[:count]


def unassign_devices(
    devices: list[dict],
) -> None:
    for device in devices:
        response = client.patch(
            f"/api/devices/{device['id']}/zone",
            json={"zone_id": None},
        )

        assert response.status_code == 204


def delete_location(
    location_id: str,
) -> None:
    client.delete(
        f"/api/locations/{location_id}"
    )


def test_create_config_persists():
    config = create_location()

    try:
        location_id = config["location"]["id"]

        response = client.get(
            f"/api/locations/{location_id}/config"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["location"]["id"] == location_id
        assert len(data["zones"]) == 1
        assert (
            data["zones"][0]["location_id"]
            == location_id
        )

    finally:
        delete_location(location_id)


def test_invalid_payload_returns_400():
    response = client.post(
        "/api/locations/config",
        json={
            "location_name": "Invalid Site",
            "zones": [
                {
                    "name": "Bad Zone",
                    "moisture_threshold_low": 0.8,
                    "moisture_threshold_high": 0.2,
                }
            ],
        },
    )

    assert response.status_code == 400


def test_assign_two_devices_to_zone():
    config = create_location(
        zones=[
            {
                "name": "Zone A",
                "moisture_threshold_low": 0.2,
                "moisture_threshold_high": 0.45,
            },
            {
                "name": "Zone B",
                "moisture_threshold_low": 0.3,
                "moisture_threshold_high": 0.5,
            },
        ]
    )

    devices = ensure_devices(3)

    location_id = config["location"]["id"]
    zone_a = config["zones"][0]["id"]
    zone_b = config["zones"][1]["id"]

    try:
        for device in devices[:2]:
            response = client.patch(
                f"/api/devices/{device['id']}/zone",
                json={"zone_id": zone_b},
            )

            assert response.status_code == 204

        response = client.patch(
            f"/api/devices/{devices[2]['id']}/zone",
            json={"zone_id": zone_a},
        )

        assert response.status_code == 204

        response = client.get(
            f"/api/locations/{location_id}/zones/{zone_b}/devices"
        )

        assert response.status_code == 200

        zone_b_ids = {
            device["id"]
            for device in response.json()
        }

        assert zone_b_ids == {
            devices[0]["id"],
            devices[1]["id"],
        }

        assert devices[2]["id"] not in zone_b_ids

    finally:
        unassign_devices(devices)
        delete_location(location_id)


def test_unassign_clears_zone_and_location():
    config = create_location()

    devices = ensure_devices(1)

    location_id = config["location"]["id"]
    zone_id = config["zones"][0]["id"]

    try:
        device_id = devices[0]["id"]

        response = client.patch(
            f"/api/devices/{device_id}/zone",
            json={"zone_id": zone_id},
        )

        assert response.status_code == 204

        response = client.patch(
            f"/api/devices/{device_id}/zone",
            json={"zone_id": None},
        )

        assert response.status_code == 204

        all_devices = client.get(
            "/api/devices"
        ).json()

        updated = next(
            device
            for device in all_devices
            if device["id"] == device_id
        )

        assert updated["zone_id"] is None
        assert updated["location_id"] is None

    finally:
        unassign_devices(devices)
        delete_location(location_id)


def test_list_locations():
    first = create_location(
        location_name=(
            f"Location A {uuid4().hex[:8]}"
        )
    )

    second = create_location(
        location_name=(
            f"Location B {uuid4().hex[:8]}"
        )
    )

    try:
        response = client.get(
            "/api/locations"
        )

        assert response.status_code == 200

        ids = {
            location["id"]
            for location in response.json()
        }

        assert first["location"]["id"] in ids
        assert second["location"]["id"] in ids

    finally:
        delete_location(
            first["location"]["id"]
        )
        delete_location(
            second["location"]["id"]
        )


def test_delete_location_clears_assignments():
    config = create_location()

    devices = ensure_devices(1)

    location_id = config["location"]["id"]
    zone_id = config["zones"][0]["id"]
    device_id = devices[0]["id"]

    try:
        response = client.patch(
            f"/api/devices/{device_id}/zone",
            json={"zone_id": zone_id},
        )

        assert response.status_code == 204

        response = client.delete(
            f"/api/locations/{location_id}"
        )

        assert response.status_code == 204

        response = client.get(
            f"/api/locations/{location_id}/config"
        )

        assert response.status_code == 404

        all_devices = client.get(
            "/api/devices"
        ).json()

        updated = next(
            device
            for device in all_devices
            if device["id"] == device_id
        )

        assert updated["zone_id"] is None
        assert updated["location_id"] is None

    finally:
        unassign_devices(devices)


def test_add_zone_to_location():
    config = create_location()

    location_id = config["location"]["id"]

    try:
        response = client.post(
            f"/api/locations/{location_id}/zones",
            json={
                "name": "Zone B",
                "moisture_threshold_low": 0.3,
                "moisture_threshold_high": 0.5,
                "schedule": {},
            },
        )

        assert response.status_code == 201

        response = client.get(
            f"/api/locations/{location_id}/config"
        )

        assert response.status_code == 200
        assert len(response.json()["zones"]) == 2

    finally:
        delete_location(location_id)


def test_update_zone_rejects_invalid_thresholds():
    config = create_location(
        zones=[
            {
                "name": "Zone A",
                "moisture_threshold_low": 0.2,
                "moisture_threshold_high": 0.45,
            },
            {
                "name": "Zone B",
                "moisture_threshold_low": 0.3,
                "moisture_threshold_high": 0.5,
            },
        ]
    )

    location_id = config["location"]["id"]
    zone_id = config["zones"][0]["id"]

    try:
        response = client.patch(
            f"/api/locations/{location_id}/zones/{zone_id}",
            json={
                "moisture_threshold_low": 0.8,
                "moisture_threshold_high": 0.2,
            },
        )

        assert response.status_code == 400

        response = client.get(
            f"/api/locations/{location_id}/config"
        )

        assert response.status_code == 200

        zone = next(
            zone
            for zone in response.json()["zones"]
            if zone["id"] == zone_id
        )

        assert (
            zone["moisture_threshold_low"]
            == 0.2
        )

        assert (
            zone["moisture_threshold_high"]
            == 0.45
        )

    finally:
        delete_location(location_id)


def test_delete_zone_clears_assignments():
    config = create_location(
        zones=[
            {
                "name": "Zone A",
                "moisture_threshold_low": 0.2,
                "moisture_threshold_high": 0.45,
            },
            {
                "name": "Zone B",
                "moisture_threshold_low": 0.3,
                "moisture_threshold_high": 0.5,
            },
        ]
    )

    devices = ensure_devices(1)

    location_id = config["location"]["id"]
    zone_id = config["zones"][1]["id"]
    device_id = devices[0]["id"]

    try:
        response = client.patch(
            f"/api/devices/{device_id}/zone",
            json={"zone_id": zone_id},
        )

        assert response.status_code == 204

        response = client.delete(
            f"/api/locations/{location_id}/zones/{zone_id}"
        )

        assert response.status_code == 204

        all_devices = client.get(
            "/api/devices"
        ).json()

        updated = next(
            device
            for device in all_devices
            if device["id"] == device_id
        )

        assert updated["zone_id"] is None
        assert updated["location_id"] is None

    finally:
        unassign_devices(devices)
        delete_location(location_id)


def test_delete_last_zone_is_rejected():
    config = create_location()

    location_id = config["location"]["id"]
    zone_id = config["zones"][0]["id"]

    try:
        response = client.delete(
            f"/api/locations/{location_id}/zones/{zone_id}"
        )

        assert response.status_code == 400

        response = client.get(
            f"/api/locations/{location_id}/config"
        )

        assert response.status_code == 200
        assert len(response.json()["zones"]) == 1

    finally:
        delete_location(location_id)